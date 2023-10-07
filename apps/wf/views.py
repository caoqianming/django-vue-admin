from django.utils import timezone
from django.db import transaction
from rest_framework.views import APIView
from apps.system.models import User
from apps.utils.viewsets import CustomGenericViewSet, CustomModelViewSet
from apps.wf.filters import TicketFilterSet
from rest_framework.response import Response
from rest_framework.mixins import CreateModelMixin, DestroyModelMixin, ListModelMixin, \
    RetrieveModelMixin, UpdateModelMixin
from apps.wf.serializers import CustomFieldCreateUpdateSerializer, CustomFieldSerializer, StateSerializer, \
    TicketAddNodeEndSerializer, TicketAddNodeSerializer, TicketCloseSerializer, \
    TicketCreateSerializer, TicketDeliverSerializer, TicketDestorySerializer, TicketFlowSerializer, \
    TicketHandleSerializer, TicketRetreatSerializer, \
    TicketSerializer, TransitionSerializer, WorkflowSerializer, \
    TicketListSerializer, TicketDetailSerializer, WorkflowCloneSerializer, TicketStateUpateSerializer, TicketFlowSimpleSerializer
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework.decorators import action
from apps.wf.models import CustomField, Ticket, Workflow, State, Transition, TicketFlow
from apps.utils.mixins import CreateUpdateCustomMixin, CreateUpdateModelAMixin
from apps.wf.services import WfService
from rest_framework.exceptions import ParseError, NotFound
from rest_framework import status
from django.db.models import Count
from rest_framework.serializers import Serializer
from apps.utils.snowflake import idWorker
import importlib
from apps.wf.tasks import run_task

# Create your views here.


class WorkflowKeyInitView(APIView):
    perms_map = {'get': '*'}

    def get(self, request, key=None):
        """
        新建工单初始化-通过key

        新建工单初始化
        """
        ret = {}
        try:
            wf = Workflow.objects.get(key=key)
        except Exception:
            raise NotFound('获取工作流失败')
        start_state = WfService.get_workflow_start_state(wf)
        transitions = WfService.get_state_transitions(start_state)
        ret['workflow'] = wf.id
        ret['transitions'] = TransitionSerializer(instance=transitions, many=True).data
        field_list = CustomFieldSerializer(instance=WfService.get_workflow_custom_fields(wf), many=True).data
        for i in field_list:
            if i['field_key'] in start_state.state_fields:
                i['field_attribute'] = start_state.state_fields[i['field_key']]
            else:
                i['field_attribute'] = State.STATE_FIELD_READONLY
        ret['field_list'] = field_list
        return Response(ret)


class WorkflowViewSet(CustomModelViewSet):
    queryset = Workflow.objects.all()
    serializer_class = WorkflowSerializer
    search_fields = ['name', 'description']
    filterset_fields = []
    ordering_fields = ['create_time']
    ordering = ['key', '-create_time']

    @action(methods=['get'], detail=True, perms_map={'get': 'workflow.update'},
            pagination_class=None, serializer_class=StateSerializer)
    def states(self, request, pk=None):
        """
        工作流下的状态节点
        """
        wf = self.get_object()
        serializer = self.serializer_class(instance=WfService.get_worlflow_states(wf), many=True)
        return Response(serializer.data)

    @action(methods=['get'], detail=True, perms_map={'get': 'workflow.update'},
            pagination_class=None, serializer_class=TransitionSerializer)
    def transitions(self, request, pk=None):
        """
        工作流下的流转规则
        """
        wf = self.get_object()
        serializer = self.serializer_class(instance=WfService.get_workflow_transitions(wf), many=True)
        return Response(serializer.data)

    @action(methods=['get'], detail=True, perms_map={'get': 'workflow.update'},
            pagination_class=None, serializer_class=CustomFieldSerializer)
    def customfields(self, request, pk=None):
        """
        工作流下的自定义字段
        """
        wf = self.get_object()
        serializer = self.serializer_class(instance=CustomField.objects.filter(
            workflow=wf, is_deleted=False).order_by('sort'), many=True)
        return Response(serializer.data)

    @action(methods=['get'], detail=True, perms_map={'get': '*'})
    def init(self, request, pk=None):
        """
        新建工单初始化

        新建工单初始化
        """
        ret = {}
        wf = self.get_object()
        start_state = WfService.get_workflow_start_state(wf)
        transitions = WfService.get_state_transitions(start_state)
        ret['workflow'] = wf.id
        ret['transitions'] = TransitionSerializer(instance=transitions, many=True).data
        field_list = CustomFieldSerializer(instance=WfService.get_workflow_custom_fields(wf), many=True).data
        for i in field_list:
            if i['field_key'] in start_state.state_fields:
                i['field_attribute'] = start_state.state_fields[i['field_key']]
            else:
                i['field_attribute'] = State.STATE_FIELD_READONLY
        ret['field_list'] = field_list
        return Response(ret)

    @action(methods=['post'], detail=True, perms_map={'post': 'workflow.clone'},
            pagination_class=None, serializer_class=WorkflowCloneSerializer)
    @transaction.atomic
    def clone(self, request, pk=None):
        """工作流复制

        工作流复制
        """
        wf = self.get_object()
        sr = WorkflowCloneSerializer(data=request.data)
        sr.is_valid(raise_exception=True)
        vdata = sr.validated_data
        wf_new = Workflow()
        for f in Workflow._meta.fields:
            if f.name not in ['id', 'create_by', 'update_by', 'key', 'name', 'create_time', 'update_time']:
                setattr(wf_new, f.name, getattr(wf, f.name, None))
        wf_new.id = idWorker.get_id()
        wf_new.key = vdata['key']
        wf_new.name = vdata['name']
        wf_new.create_by = request.user
        wf_new.save()
        stas_dict = {}
        for s in State.objects.filter(workflow=wf):
            sta = State()
            sta.id = idWorker.get_id()
            sta.workflow = wf_new
            for f in State._meta.fields:
                if f.name not in ['workflow', 'create_time', 'update_time', 'id']:
                    setattr(sta, f.name, getattr(s, f.name))
            sta.save()
            stas_dict[s.id] = sta  # 保存一下, 后续备用
        for c in CustomField.objects.filter(workflow=wf):
            cf = CustomField()
            cf.id = idWorker.get_id()
            cf.workflow = wf_new
            for f in CustomField._meta.fields:
                if f.name not in ['workflow', 'create_time', 'update_time', 'id']:
                    setattr(sta, f.name, getattr(s, f.name))
            cf.save()
        for t in Transition.objects.filter(workflow=wf):
            tr = Transition()
            tr.id = idWorker.get_id()
            tr.workflow = wf_new
            for f in Transition._meta.fields:
                if f.name not in ['workflow', 'create_time', 'update_time', 'id']:
                    setattr(tr, f.name, getattr(t, f.name))
            tr.source_state = stas_dict[t.source_state.id]
            tr.destination_state = stas_dict[t.destination_state.id]
            ce = tr.condition_expression
            for i in ce:
                i['target_state'] = stas_dict[i['target_state']].id
            tr.condition_expression = ce
            tr.save()
        return Response()


class StateViewSet(CreateModelMixin, UpdateModelMixin, RetrieveModelMixin, DestroyModelMixin, CustomGenericViewSet):
    perms_map = {'get': '*', 'post': 'workflow.update',
                 'put': 'workflow.update', 'delete': 'workflow.update'}
    queryset = State.objects.all()
    serializer_class = StateSerializer
    search_fields = ['name']
    filterset_fields = ['workflow']
    ordering = ['sort']


class TransitionViewSet(CreateModelMixin, UpdateModelMixin, RetrieveModelMixin, DestroyModelMixin, CustomGenericViewSet):
    perms_map = {'get': '*', 'post': 'workflow.update',
                 'put': 'workflow.update', 'delete': 'workflow.update'}
    queryset = Transition.objects.all()
    serializer_class = TransitionSerializer
    select_related_fields = ['source_state', 'destination_state']
    search_fields = ['name']
    filterset_fields = ['workflow']
    ordering = ['id']


class CustomFieldViewSet(CreateModelMixin, UpdateModelMixin, RetrieveModelMixin, DestroyModelMixin, CustomGenericViewSet):
    perms_map = {'get': '*', 'post': 'workflow.update',
                 'put': 'workflow.update', 'delete': 'workflow.update'}
    queryset = CustomField.objects.all()
    serializer_class = CustomFieldSerializer
    search_fields = ['field_name']
    filterset_fields = ['workflow', 'field_type']
    ordering = ['sort']

    def get_serializer_class(self):
        if self.action in ['create', 'update']:
            return CustomFieldCreateUpdateSerializer
        return super().get_serializer_class()


class TicketViewSet(CreateUpdateCustomMixin, CreateModelMixin, ListModelMixin, RetrieveModelMixin, CustomGenericViewSet):
    perms_map = {'get': '*', 'post': '*'}
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    search_fields = ['title']
    select_related_fields = ['workflow', 'state']
    filterset_class = TicketFilterSet
    ordering = ['-create_time']

    def get_serializer_class(self):
        if self.action == 'create':
            return TicketCreateSerializer
        elif self.action == 'handle':
            return TicketHandleSerializer
        elif self.action == 'retreat':
            return TicketRetreatSerializer
        elif self.action == 'list':
            return TicketListSerializer
        elif self.action == 'retrieve':
            return TicketDetailSerializer
        elif self.action == 'deliver':
            return TicketDeliverSerializer
        return super().get_serializer_class()

    def filter_queryset(self, queryset):
        if not self.detail and not self.request.query_params.get('category', None):
            raise ParseError('请指定查询分类')
        return super().filter_queryset(queryset)

    def create(self, request, *args, **kwargs):
        """
        新建工单
        """
        rdata = request.data
        serializer = self.get_serializer(data=rdata)
        serializer.is_valid(raise_exception=True)
        vdata = serializer.validated_data  # 校验之后的数据
        start_state = WfService.get_workflow_start_state(vdata['workflow'])
        transition = vdata.pop('transition')
        ticket_data = vdata['ticket_data']

        save_ticket_data = {}
        # 校验必填项
        if transition.field_require_check:
            for key, value in start_state.state_fields.items():
                if int(value) == State.STATE_FIELD_REQUIRED:
                    if key not in ticket_data and not ticket_data[key]:
                        raise ParseError('字段{}必填'.format(key))
                    save_ticket_data[key] = ticket_data[key]
                elif int(value) == State.STATE_FIELD_OPTIONAL:
                    save_ticket_data[key] = ticket_data[key]
        else:
            save_ticket_data = ticket_data
        with transaction.atomic():
            ticket = serializer.save(state=start_state,
                                     create_by=request.user,
                                     create_time=timezone.now(),
                                     act_state=Ticket.TICKET_ACT_STATE_DRAFT,
                                     belong_dept=request.user.belong_dept,
                                     ticket_data=save_ticket_data)  # 先创建出来
            # 更新title和sn
            title = vdata.get('title', '')
            title_template = ticket.workflow.title_template
            if title_template:
                all_ticket_data = {**rdata, **ticket_data}
                title = title_template.format(**all_ticket_data)
            sn = WfService.get_ticket_sn(ticket.workflow)  # 流水号
            ticket.sn = sn
            ticket.title = title
            ticket.save()
            ticket = WfService.handle_ticket(ticket=ticket, transition=transition, new_ticket_data=ticket_data,
                                             handler=request.user, created=True)
        return Response(TicketSerializer(instance=ticket).data)

    @action(methods=['get'], detail=False, perms_map={'get': '*'})
    def duty_agg(self, request, pk=None):
        """
        工单待办聚合
        """
        ret = {}
        queryset = Ticket.objects.filter(participant__contains=request.user.id, is_deleted=False)\
            .exclude(act_state__in=[Ticket.TICKET_ACT_STATE_FINISH, Ticket.TICKET_ACT_STATE_CLOSED])
        ret['total_count'] = queryset.count()
        ret['details'] = list(queryset.values('workflow', 'workflow__name').annotate(count=Count('workflow')))
        return Response(ret)

    @action(methods=['post'], detail=True, perms_map={'post': '*'})
    def handle(self, request, pk=None):
        """
        处理工单
        """
        ticket = self.get_object()
        serializer = TicketHandleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        vdata = serializer.validated_data
        new_ticket_data = ticket.ticket_data
        new_ticket_data.update(**vdata['ticket_data'])
        with transaction.atomic():
            ticket = WfService.handle_ticket(ticket=ticket, transition=vdata['transition'],
                                             new_ticket_data=new_ticket_data, handler=request.user,
                                             suggestion=vdata.get('suggestion', ''))
        return Response(TicketSerializer(instance=ticket).data)

    @action(methods=['post'], detail=True, perms_map={'post': '*'})
    def deliver(self, request, pk=None):
        """
        转交工单
        """
        ticket = self.get_object()
        rdata = request.data
        serializer = self.get_serializer(data=rdata)
        serializer.is_valid(raise_exception=True)
        vdata = serializer.validated_data  # 校验之后的数据
        if not ticket.state.enable_deliver:
            raise ParseError('不允许转交')
        with transaction.atomic():
            ticket.participant_type = State.PARTICIPANT_TYPE_PERSONAL
            ticket.participant = vdata['target_user']
            ticket.save()
            TicketFlow.objects.create(ticket=ticket, state=ticket.state,
                                      ticket_data=WfService.get_ticket_all_field_value(ticket),
                                      suggestion=vdata.get('suggestion', ''), participant_type=State.PARTICIPANT_TYPE_PERSONAL,
                                      intervene_type=Transition.TRANSITION_INTERVENE_TYPE_DELIVER,
                                      participant=request.user, transition=None)
        return Response()

    @action(methods=['get'], detail=True, perms_map={'get': '*'})
    def flowsteps(self, request, pk=None):
        """
        工单流转step, 用于显示当前状态的step图(线性结构)
        """
        ticket = self.get_object()
        steps = WfService.get_ticket_steps(ticket)
        data = StateSerializer(instance=steps, many=True).data
        for i in data:
            if i['id'] == ticket.state.id:
                i['checked'] = True
        return Response(data)

    @action(methods=['get'], detail=True, perms_map={'get': '*'})
    def flowlogs(self, request, pk=None):
        """
        工单流转记录
        """
        ticket = self.get_object()
        flowlogs = TicketFlow.objects.filter(ticket=ticket).order_by('-create_time')
        serializer = TicketFlowSimpleSerializer(instance=flowlogs.select_related('participant', 'state', 'transition', 'participant__employee'), many=True)
        return Response(serializer.data)

    @action(methods=['get'], detail=True, perms_map={'get': '*'})
    def transitions(self, request, pk=None):
        """
        获取工单可执行的操作
        """
        ticket = self.get_object()
        transitions = WfService.get_ticket_transitions(ticket)
        return Response(TransitionSerializer(instance=transitions.select_related('source_state', 'destination_state'), many=True).data)

    @action(methods=['post'], detail=True, perms_map={'post': '*'})
    def accpet(self, request, pk=None):
        """
        接单,当工单当前处理人实际为多个人时(角色、部门、多人都有可能， 注意角色和部门有可能实际只有一人)
        """
        ticket = self.get_object()
        result = WfService.ticket_handle_permission_check(ticket, request.user)
        if result.get('need_accept', False):
            ticket.participant_type = State.PARTICIPANT_TYPE_PERSONAL
            ticket.participant = request.user.id
            ticket.save()
            # 接单日志
            # 更新工单流转记录
            TicketFlow.objects.create(ticket=ticket, state=ticket.state,
                                      ticket_data=WfService.get_ticket_all_field_value(ticket),
                                      suggestion='', participant_type=State.PARTICIPANT_TYPE_PERSONAL,
                                      intervene_type=Transition.TRANSITION_ATTRIBUTE_TYPE_ACCEPT,
                                      participant=request.user, transition=None)
            return Response()
        else:
            raise ParseError('无需接单')

    @action(methods=['post'], detail=True, perms_map={'post': '*'})
    def retreat(self, request, pk=None):
        """
        撤回工单，允许创建人在指定状态撤回工单至初始状态，状态设置中开启允许撤回
        """
        ticket = self.get_object()
        if ticket.create_by != request.user:
            raise ParseError('非创建人不可撤回')
        if not ticket.state.enable_retreat:
            raise ParseError('该状态不可撤回')
        start_state = WfService.get_workflow_start_state(ticket.workflow)
        ticket.state = start_state
        ticket.participant_type = State.PARTICIPANT_TYPE_PERSONAL
        ticket.participant = request.user.id
        ticket.act_state = Ticket.TICKET_ACT_STATE_RETREAT
        ticket.save()
        # 更新流转记录
        suggestion = request.data.get('suggestion', '')  # 撤回原因
        TicketFlow.objects.create(ticket=ticket, state=ticket.state,
                                  ticket_data=WfService.get_ticket_all_field_value(ticket),
                                  suggestion=suggestion, participant_type=State.PARTICIPANT_TYPE_PERSONAL,
                                  intervene_type=Transition.TRANSITION_INTERVENE_TYPE_RETREAT,
                                  participant=request.user, transition=None)
        return Response()

    @action(methods=['post'], detail=True, perms_map={'post': '*'}, serializer_class=TicketAddNodeSerializer)
    def add_node(self, request, pk=None):
        """
        加签
        """
        data = request.data
        sr = TicketAddNodeSerializer(data=data)
        sr.is_valid(raise_exception=True)
        ticket = self.get_object()
        add_user = User.objects.get(pk=data['toadd_user'])
        ticket.participant_type = State.PARTICIPANT_TYPE_PERSONAL
        ticket.participant = add_user.id
        ticket.in_add_node = True
        ticket.add_node_man = request.user
        ticket.save()
        # 更新流转记录
        suggestion = request.data.get('suggestion', '')  # 加签说明
        TicketFlow.objects.create(ticket=ticket, state=ticket.state,
                                  ticket_data=WfService.get_ticket_all_field_value(ticket),
                                  suggestion=suggestion, participant_type=State.PARTICIPANT_TYPE_PERSONAL,
                                  intervene_type=Transition.TRANSITION_INTERVENE_TYPE_ADD_NODE,
                                  participant=request.user, transition=None)
        return Response()

    @action(methods=['post'], detail=True, perms_map={'post': '*'}, serializer_class=TicketAddNodeEndSerializer)
    def add_node_end(self, request, pk=None):
        """
        加签完成
        """
        ticket = self.get_object()
        if ticket.in_add_node is False:
            raise ParseError('该工单不在加签状态中')
        elif ticket.participant != request.user.id:
            raise ParseError('非当前加签人')
        ticket.participant_type = State.PARTICIPANT_TYPE_PERSONAL
        ticket.in_add_node = False
        ticket.participant = ticket.add_node_man.id
        ticket.add_node_man = None
        ticket.save()
        # 更新流转记录
        suggestion = request.data.get('suggestion', '')  # 加签意见
        TicketFlow.objects.create(ticket=ticket, state=ticket.state,
                                  ticket_data=WfService.get_ticket_all_field_value(ticket),
                                  suggestion=suggestion, participant_type=State.PARTICIPANT_TYPE_PERSONAL,
                                  intervene_type=Transition.TRANSITION_INTERVENE_TYPE_ADD_NODE_END,
                                  participant=request.user, transition=None)
        return Response()

    @action(methods=['post'], detail=True, perms_map={'post': '*'},
            serializer_class=TicketCloseSerializer)
    @transaction.atomic
    def close(self, request, pk=None):
        """
        关闭工单(创建人在初始状态)
        """
        ticket = self.get_object()
        if ticket.state.type == State.STATE_TYPE_START and ticket.create_by == request.user:
            end_state = WfService.get_workflow_end_state(ticket.workflow)
            ticket.state = end_state
            ticket.participant_type = 0
            ticket.participant = 0
            ticket.act_state = Ticket.TICKET_ACT_STATE_CLOSED
            ticket.save()
            # 更新流转记录
            suggestion = request.data.get('suggestion', '')  # 关闭原因
            TicketFlow.objects.create(ticket=ticket, state=ticket.state,
                                      ticket_data=WfService.get_ticket_all_field_value(ticket),
                                      suggestion=suggestion, participant_type=State.PARTICIPANT_TYPE_PERSONAL,
                                      intervene_type=Transition.TRANSITION_INTERVENE_TYPE_CLOSE,
                                      participant=request.user, transition=None)
            if end_state.on_reach_func:  # 如果有到达方法还需要进行处理
                module, func = end_state.on_reach_func.rsplit(".", 1)
                m = importlib.import_module(module)
                f = getattr(m, func)
                f(ticket=ticket)  # 同步执行
            return Response()
        else:
            return Response('工单不可关闭', status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['post'], detail=False, perms_map={'post': 'ticket.destorys'},
            serializer_class=TicketDestorySerializer)
    def destorys(self, request, pk=None):
        """
        批量物理删除
        """
        Ticket.objects.filter(id__in=request.data.get('ids', [])).delete(soft=False)
        return Response()

    @action(methods=['post'], detail=True, perms_map={'post': '*'},
            serializer_class=Serializer)
    def retry_script(self, request, pk=None):
        """重试脚本

        重试脚本
        """
        ticket = self.get_object()
        if not ticket.script_run_last_result:
            ticket.script_run_last_result = True
            ticket.save()
            run_task.delay(ticket.id)
        return Response()

    @action(methods=['put'], detail=True, perms_map={'put': 'ticket.state_update'},
            serializer_class=TicketStateUpateSerializer)
    def state(self, request, pk=None):
        """强制修改工单状态

        强制修改工单状态
        """
        sr = TicketStateUpateSerializer(data=request.data)
        sr.is_valid(raise_exception=True)
        vdata = sr.validated_data
        ticket = self.get_object()
        WfService.update_ticket_state(ticket, vdata['state'], vdata.get('suggestion', ''), request.user, vdata['need_log'])
        return Response()


class TicketFlowViewSet(ListModelMixin, RetrieveModelMixin, CustomGenericViewSet):
    """
    工单日志
    """
    perms_map = {'get': '*'}
    queryset = TicketFlow.objects.all()
    list_serializer_class = TicketFlowSimpleSerializer
    serializer_class = TicketFlowSerializer
    search_fields = ['suggestion']
    select_related_fields = ['participant', 'state', 'transition']
    filterset_fields = ['ticket']
    ordering = ['-create_time']
