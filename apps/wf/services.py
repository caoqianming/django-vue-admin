import importlib
from threading import Thread
from apps.utils.sms import send_sms
from apps.wf.serializers import TicketSimpleSerializer
from apps.system.models import Dept, User
from apps.wf.models import CustomField, State, Ticket, TicketFlow, Transition, Workflow
from rest_framework.exceptions import APIException, PermissionDenied, ValidationError
from django.utils import timezone
from datetime import timedelta, datetime
import random
from apps.utils.queryset import get_parent_queryset
from apps.wf.tasks import run_task
from rest_framework.exceptions import ParseError


class WfService(object):
    @staticmethod
    def get_worlflow_states(workflow: Workflow):
        """
        获取工作流状态列表
        """
        return State.objects.filter(workflow=workflow, is_deleted=False).order_by('sort')

    @staticmethod
    def get_workflow_transitions(workflow: Workflow):
        """
        获取工作流流转列表
        """
        return Transition.objects.filter(workflow=workflow, is_deleted=False)

    @staticmethod
    def get_workflow_start_state(workflow: Workflow):
        """
        获取工作流初始状态
        """
        try:
            wf_state_obj = State.objects.get(workflow=workflow, type=State.STATE_TYPE_START, is_deleted=False)
            return wf_state_obj
        except Exception:
            raise APIException('工作流状态配置错误')

    @staticmethod
    def get_workflow_end_state(workflow: Workflow):
        """
        获取工作流结束状态
        """
        try:
            wf_state_obj = State.objects.get(workflow=workflow, type=State.STATE_TYPE_END, is_deleted=False)
            return wf_state_obj
        except Exception:
            raise APIException('工作流状态配置错误')

    @staticmethod
    def get_workflow_custom_fields(workflow: Workflow):
        """
        获取工单字段
        """
        return CustomField.objects.filter(is_deleted=False, workflow=workflow).order_by('sort')

    @staticmethod
    def get_workflow_custom_fields_list(workflow: Workflow):
        """
        获取工单字段key List
        """
        return list(CustomField.objects.filter(is_deleted=False,
                    workflow=workflow).order_by('sort').values_list('field_key', flat=True))

    @classmethod
    def get_ticket_transitions(cls, ticket: Ticket):
        """
        获取工单当前状态下可用的流转条件
        """
        return cls.get_state_transitions(ticket.state)

    @classmethod
    def get_state_transitions(cls, state: State):
        """
        获取状态可执行的操作
        """
        return Transition.objects.filter(is_deleted=False, source_state=state).all()

    @classmethod
    def get_ticket_steps(cls, ticket: Ticket):
        steps = cls.get_worlflow_states(ticket.workflow)
        nsteps_list = []
        for i in steps:
            if ticket.state == i or (not i.is_hidden):
                nsteps_list.append(i)
        return nsteps_list

    @classmethod
    def get_transition_by_args(cls, kwargs: dict):
        """
        查询并获取流转
        """
        kwargs['is_deleted'] = False
        return Transition.objects.filter(**kwargs).all()

    @classmethod
    def get_ticket_sn(cls, workflow: Workflow, now=None):
        """
        生成工单流水号
        """
        if now is None:
            now = datetime.now()
        today = str(now)[:10]+' 00:00:00'
        ticket_day_count_new = Ticket.objects.get_queryset(all=True).filter(
            create_time__gte=today, create_time__lte=now, workflow=workflow).count()
        return '%s_%04d%02d%02d%04d' % (workflow.sn_prefix, now.year, now.month, now.day, ticket_day_count_new)

    @classmethod
    def get_next_state_by_transition_and_ticket_info(cls, ticket: Ticket,
                                                     transition: Transition, new_ticket_data: dict = {}) -> object:
        """
        获取下个节点状态
        """
        destination_state = transition.destination_state
        ticket_all_value = cls.get_ticket_all_field_value(ticket)
        ticket_all_value.update(**new_ticket_data)
        for key, value in ticket_all_value.items():
            if isinstance(ticket_all_value[key], str):
                ticket_all_value[key] = "'" + ticket_all_value[key] + "'"
        if transition.condition_expression:
            for i in transition.condition_expression:
                expression = i['expression'].format(**ticket_all_value)
                import datetime
                import time  # 用于支持条件表达式中对时间的操作
                if eval(expression, {'__builtins__': None}, {'datetime': datetime, 'time': time}):
                    destination_state = State.objects.get(pk=i['target_state'])
                    return destination_state
        return destination_state

    @classmethod
    def get_ticket_state_participant_info(cls, state: State,
                                          ticket: Ticket, new_ticket_data: dict = {}, handler: User = None):
        """
        获取工单目标状态实际的处理人, 处理人类型
        """
        if state.type == State.STATE_TYPE_START:
            """
            回到初始状态
            """
            return dict(destination_participant_type=State.PARTICIPANT_TYPE_PERSONAL,
                        destination_participant=ticket.create_by.id,
                        multi_all_person={})
        elif state.type == State.STATE_TYPE_END:
            """
            到达结束状态
            """
            return dict(destination_participant_type=0,
                        destination_participant=0,
                        multi_all_person={})
        multi_all_person_dict = {}
        destination_participant_type, destination_participant = state.participant_type, state.participant
        if destination_participant_type == State.PARTICIPANT_TYPE_FIELD:
            destination_participant = new_ticket_data.get(destination_participant, 0) if destination_participant \
                in new_ticket_data else Ticket.ticket_data.get(destination_participant, 0)

        elif destination_participant_type == State.PARTICIPANT_TYPE_FORMCODE:  # 代码获取
            module, func = destination_participant.rsplit(".", 1)
            m = importlib.import_module(module)
            f = getattr(m, func)
            destination_participant = f(state=state, ticket=ticket, new_ticket_data=new_ticket_data, handler=handler)

        elif destination_participant_type == State.PARTICIPANT_TYPE_DEPT:  # 部门
            destination_participant = list(User.objects.filter(
                depts__in=destination_participant).values_list('id', flat=True))

        elif destination_participant_type == State.PARTICIPANT_TYPE_POST:  # 岗位
            user_queryset = User.objects.filter(posts__in=destination_participant)
            # 如果选择了岗位, 可能需要走过滤策略
            if state.filter_dept not in [0, '0', None]:
                # if not new_ticket_data.get(state.filter_dept, None):
                #     raise ParseError('部门过滤字段错误')
                if '.' not in state.filter_dept:
                    dpts = Dept.objects.filter(id=new_ticket_data[state.filter_dept])
                else:
                    dpt_attrs = state.filter_dept.split('.')  # 通过反向查询得到可能有多层
                    expr = ticket
                    for i in dpt_attrs:
                        expr = getattr(expr, i)
                    dpts = Dept.objects.filter(id=expr.id)
                user_queryset = user_queryset.filter(depts__in=dpts)
            # if state.filter_policy == 1:
            #     depts = get_parent_queryset(ticket.belong_dept)
            #     user_queryset = user_queryset.filter(depts__in=depts)
            # elif state.filter_policy == 2:
            #     depts = get_parent_queryset(ticket.create_by.belong_dept)
            #     user_queryset = user_queryset.filter(depts__in=depts)
            # elif state.filter_policy == 3:
            #     depts = get_parent_queryset(handler.belong_dept)
            #     user_queryset = user_queryset.filter(depts__in=depts)
            destination_participant = list(user_queryset.values_list('id', flat=True))
        elif destination_participant_type == State.PARTICIPANT_TYPE_ROLE:  # 角色
            user_queryset = User.objects.filter(roles__in=destination_participant, is_active=True, is_deleted=False)
            # 如果选择了角色, 需要走过滤策略
            if state.filter_dept not in [0, '0', None]:
                # if not new_ticket_data.get(state.filter_dept, None):
                #     raise ParseError('部门过滤字段错误')
                if '.' not in state.filter_dept:
                    dpts = Dept.objects.filter(id=new_ticket_data[state.filter_dept])
                else:
                    dpt_attrs = state.filter_dept.split('.')
                    expr = ticket
                    for i in dpt_attrs:
                        expr = getattr(expr, i)
                    dpts = Dept.objects.filter(id=expr.id)
                user_queryset = user_queryset.filter(depts__in=dpts)
            # if state.filter_policy == 1:
            #     depts = get_parent_queryset(ticket.belong_dept)
            #     user_queryset = user_queryset.filter(depts__in=depts)
            # elif state.filter_policy == 2:
            #     depts = get_parent_queryset(ticket.create_by.belong_dept)
            #     user_queryset = user_queryset.filter(depts__in=depts)
            # elif state.filter_policy == 3:
            #     depts = get_parent_queryset(handler.belong_dept)
            #     user_queryset = user_queryset.filter(depts__in=depts)
            destination_participant = list(user_queryset.values_list('id', flat=True))
        if destination_participant_type != 0 and (not destination_participant):
            raise ParseError('下一步未找到处理人,工单无法继续')
        if type(destination_participant) == list:
            destination_participant_type = State.PARTICIPANT_TYPE_MULTI
            destination_participant = list(set(destination_participant))
            if len(destination_participant) == 1:  # 如果只有一个人
                destination_participant_type = State.PARTICIPANT_TYPE_PERSONAL
                destination_participant = destination_participant[0]
        elif destination_participant_type == State.PARTICIPANT_TYPE_ROBOT:
            pass
        else:
            destination_participant_type = State.PARTICIPANT_TYPE_PERSONAL
        if destination_participant_type == State.PARTICIPANT_TYPE_MULTI:
            if state.distribute_type == State.STATE_DISTRIBUTE_TYPE_RANDOM:
                destination_participant = random.choice(destination_participant)
            elif state.distribute_type == State.STATE_DISTRIBUTE_TYPE_ALL:
                for i in destination_participant:
                    multi_all_person_dict[i] = {}

        return dict(destination_participant_type=destination_participant_type,
                    destination_participant=destination_participant,
                    multi_all_person=multi_all_person_dict)

    @classmethod
    def ticket_handle_permission_check(cls, ticket: Ticket, user: User) -> dict:
        if ticket.in_add_node:
            return dict(permission=False, msg="工单当前处于加签中,请加签完成后操作", need_accept=False)
        transitions = cls.get_state_transitions(ticket.state)
        if not transitions:
            return dict(permission=True, msg="工单当前状态无需操作")
        participant = ticket.participant
        state = ticket.state
        if type(participant) == list:
            if user.id not in participant:
                    return dict(permission=False, msg="非当前处理人", need_accept=False)
            if len(participant) > 1 and state.distribute_type == State.STATE_DISTRIBUTE_TYPE_ACTIVE:
                return dict(permission=False, msg="需要先接单再处理", need_accept=True)
        else:
            if user.id != participant:
                return dict(permission=False, msg="非当前处理人", need_accept=False)
        return dict(permission=True, msg="", need_accept=False)

    @classmethod
    def check_dict_has_all_same_value(cls, dict_obj: object) -> tuple:
        """
        check whether all key are equal in a dict
        :param dict_obj:
        :return:
        """
        value_list = []
        for key, value in dict_obj.items():
            value_list.append(value)
        value_0 = value_list[0]
        for value in value_list:
            if value_0 != value:
                return False
        return True

    @classmethod
    def get_ticket_all_field_value(cls, ticket: Ticket) -> dict:
        """
        工单所有字段的值
        get ticket's all field value
        :param ticket:
        :return:
        """
        # 获取工单基础表中的字段中的字段信息
        field_info_dict = TicketSimpleSerializer(instance=ticket).data
        # 获取自定义字段的值
        custom_fields_queryset = cls.get_workflow_custom_fields(ticket.workflow)
        for i in custom_fields_queryset:
            field_info_dict[i.field_key] = ticket.ticket_data.get(i.field_key, None)
        return field_info_dict

    @classmethod
    def handle_ticket(cls, ticket: Ticket, transition: Transition, new_ticket_data: dict = {}, handler: User = None,
                      suggestion: str = '', created: bool = False, by_timer: bool = False,
                      by_task: bool = False, by_hook: bool = False):

        source_state = ticket.state
        source_ticket_data = ticket.ticket_data

        if transition.source_state != source_state:
            raise ParseError('非该工单节点状态下的流转')
        
        # 提交时可能进行的操作
        if transition.on_submit_func:
            module, func = transition.on_submit_func.rsplit(".", 1)
            m = importlib.import_module(module)
            f = getattr(m, func)
            f(ticket=ticket, transition=transition, new_ticket_data=new_ticket_data)

        # 校验处理权限
        if handler is not None and created is False:  # 有处理人意味着系统触发校验处理权限
            result = WfService.ticket_handle_permission_check(ticket, handler)
            if result.get('permission') is False:
                raise PermissionDenied(result.get('msg'))

        # 校验表单必填项目
        if transition.field_require_check or not created:
            for key, value in ticket.state.state_fields.items():
                if int(value) == State.STATE_FIELD_REQUIRED:
                    if key not in new_ticket_data or not new_ticket_data[key]:
                        raise ValidationError('字段{}必填'.format(key))

        destination_state = cls.get_next_state_by_transition_and_ticket_info(ticket, transition, new_ticket_data)
        multi_all_person = ticket.multi_all_person
        if multi_all_person:
            multi_all_person[handler.id] = dict(transition=transition.id)
            # 判断所有人处理结果是否一致
            if WfService.check_dict_has_all_same_value(multi_all_person):
                participant_info = WfService.get_ticket_state_participant_info(
                    destination_state, ticket, new_ticket_data)
                destination_participant_type = participant_info.get('destination_participant_type', 0)
                destination_participant = participant_info.get('destination_participant', 0)
                multi_all_person = {}
            else:
                # 处理人没有没有全部处理完成或者处理动作不一致
                destination_participant_type = ticket.participant_type
                destination_state = ticket.state  # 保持原状态
                destination_participant = []
                for key, value in multi_all_person.items():
                    if not value:
                        destination_participant.append(key)
        else:
            # 当前处理人类型非全部处理
            participant_info = WfService.get_ticket_state_participant_info(destination_state, ticket, new_ticket_data)
            destination_participant_type = participant_info.get('destination_participant_type', 0)
            destination_participant = participant_info.get('destination_participant', 0)
            multi_all_person = participant_info.get('multi_all_person', {})

        # 更新工单信息：基础字段及自定义字段， add_relation字段 需要下个处理人是部门、角色等的情况
        ticket.state = destination_state
        ticket.participant_type = destination_participant_type
        ticket.participant = destination_participant
        ticket.multi_all_person = multi_all_person
        if destination_state.type == State.STATE_TYPE_END:
            ticket.act_state = Ticket.TICKET_ACT_STATE_FINISH
        elif destination_state.type == State.STATE_TYPE_START:
            ticket.act_state = Ticket.TICKET_ACT_STATE_DRAFT
        else:
            ticket.act_state = Ticket.TICKET_ACT_STATE_ONGOING

        if transition.attribute_type == Transition.TRANSITION_ATTRIBUTE_TYPE_REFUSE:
            ticket.act_state = Ticket.TICKET_ACT_STATE_BACK

        # 只更新必填和可选的字段
        if not created and transition.field_require_check:
            for key, value in source_state.state_fields.items():
                if value in (State.STATE_FIELD_REQUIRED, State.STATE_FIELD_OPTIONAL):
                    if key in new_ticket_data:
                        source_ticket_data[key] = new_ticket_data[key]
            ticket.ticket_data = source_ticket_data
        ticket.save()

        # 更新工单流转记录
        if not by_task:
            TicketFlow.objects.create(ticket=ticket, state=source_state,
                                      ticket_data=WfService.get_ticket_all_field_value(ticket),
                                      suggestion=suggestion, participant_type=State.PARTICIPANT_TYPE_PERSONAL,
                                      participant=handler, transition=transition)

        if created:
            if source_state.participant_cc:
                TicketFlow.objects.create(ticket=ticket, state=source_state,
                                          participant_type=0, intervene_type=Transition.TRANSITION_INTERVENE_TYPE_CC,
                                          participant=None, participant_cc=source_state.participant_cc)

        # 目标状态需要抄送
        if destination_state.participant_cc:
            TicketFlow.objects.create(ticket=ticket, state=destination_state,
                                      participant_type=0, intervene_type=Transition.TRANSITION_INTERVENE_TYPE_CC,
                                      participant=None, participant_cc=destination_state.participant_cc)

        if destination_state.type == State.STATE_TYPE_END:
            TicketFlow.objects.create(ticket=ticket, state=destination_state,
                                      participant_type=0, intervene_type=0,
                                      participant=None)

        cls.task_ticket(ticket=ticket)

        return ticket

    @classmethod
    def update_ticket_state(cls, ticket: Ticket, new_state: State, suggestion: str, handler: User, need_log:bool):
        participant_info = cls.get_ticket_state_participant_info(
            new_state, ticket, {})
        source_state = ticket.state
        ticket.state = new_state
        ticket.participant_type = participant_info.get('destination_participant_type', 0)
        ticket.participant = participant_info.get('destination_participant', 0)
        ticket.multi_all_person = {}
        ticket.save()
        if need_log:
            TicketFlow.objects.create(ticket=ticket, state=source_state,
                                    ticket_data=WfService.get_ticket_all_field_value(ticket),
                                    suggestion=suggestion, participant_type=State.PARTICIPANT_TYPE_PERSONAL,
                                    intervene_type=Transition.TRANSITION_INTERVENE_TYPE_ALTER_STATE,
                                    participant=handler)
        cls.task_ticket(ticket=ticket)

    @classmethod
    def task_ticket(cls, ticket: Ticket):
        """
        执行任务(自定义任务和通知)
        """
        state = ticket.state
        # 如果目标状态有func,由func执行额外操作(比如发送通知)
        if state.on_reach_func:
            module, func = state.on_reach_func.rsplit(".", 1)
            m = importlib.import_module(module)
            f = getattr(m, func)
            f(ticket=ticket)  # 同步执行

        # wf默认只发送通知
        last_log = TicketFlow.objects.filter(ticket=ticket).order_by('-create_time').first()
        if (last_log.state != state or
            last_log.intervene_type == Transition.TRANSITION_INTERVENE_TYPE_DELIVER or
                ticket.in_add_node):
            # 如果状态变化或是转交加签的情况再发送通知
            Thread(target=send_ticket_notice_t, args=(ticket,), daemon=True).start()

        # 如果目标状态是脚本则异步执行
        if state.participant_type == State.PARTICIPANT_TYPE_ROBOT:
            run_task.delay(ticket_id=ticket.id)

    @classmethod
    def close_by_task(cls, ticket: Ticket, suggestion: str):
        # 定时任务触发的工单关闭
        end_state = WfService.get_workflow_end_state(ticket.workflow)
        ticket.state = end_state
        ticket.participant_type = 0
        ticket.participant = 0
        ticket.act_state = Ticket.TICKET_ACT_STATE_CLOSED
        ticket.save()
        # 更新流转记录
        TicketFlow.objects.create(ticket=ticket, state=ticket.state,
                                    ticket_data=WfService.get_ticket_all_field_value(ticket),
                                    suggestion=suggestion, participant_type=State.PARTICIPANT_TYPE_ROBOT,
                                    intervene_type=Transition.TRANSITION_INTERVENE_TYPE_CLOSE, transition=None)

def send_ticket_notice_t(ticket: Ticket):
    """
    发送通知
    """
    params = {'workflow': ticket.workflow.name, 'state': ticket.state.name}
    if ticket.participant_type == 1:
        # 发送短信通知
        pt = User.objects.filter(id=ticket.participant).first()
        if pt and pt.phone:
            send_sms(pt.phone, 1002, params)
    elif ticket.participant_type == 2:
        pts = User.objects.filter(id__in=ticket.participant)
        for i in pts:
            if i.phone:
                send_sms(i.phone, 1002, params)
