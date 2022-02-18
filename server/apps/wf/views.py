from django.utils import timezone
from django.db import transaction
from django.db.models import query
from rest_framework.utils import serializer_helpers
from rest_framework.views import APIView
from apps.system.models import User
from apps.wf.filters import TicketFilterSet
from django.core.exceptions import AppRegistryNotReady
from rest_framework.response import Response
from rest_framework import serializers
from rest_framework.mixins import CreateModelMixin, DestroyModelMixin, ListModelMixin, RetrieveModelMixin, UpdateModelMixin
from apps.wf.serializers import CustomFieldCreateUpdateSerializer, CustomFieldSerializer, StateSerializer, TicketAddNodeEndSerializer, TicketAddNodeSerializer, TicketCloseSerializer, TicketCreateSerializer, TicketDestorySerializer, TicketFlowSerializer, TicketFlowSimpleSerializer, TicketHandleSerializer, TicketRetreatSerializer, TicketSerializer, TransitionSerializer, WorkflowSerializer, TicketListSerializer, TicketDetailSerializer
from django.shortcuts import get_object_or_404, render
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework.decorators import action, api_view
from apps.wf.models import CustomField, Ticket, Workflow, State, Transition, TicketFlow
from apps.system.mixins import CreateUpdateCustomMixin, CreateUpdateModelAMixin, OptimizationMixin
from apps.wf.services import WfService
from rest_framework.exceptions import APIException, PermissionDenied
from rest_framework import status
from django.db.models import Count
from .scripts import GetParticipants, HandleScripts


# Create your views here.
class FromCodeListView(APIView):
    def get(self, request, format=None):
        """
        获取处理人代码列表
        """
        return Response(GetParticipants.all_funcs)

class WorkflowViewSet(CreateUpdateModelAMixin, ModelViewSet):
    perms_map = {'get': '*', 'post': 'workflow_create',
                 'put': 'workflow_update', 'delete': 'workflow_delete'}
    queryset = Workflow.objects.all()
    serializer_class = WorkflowSerializer
    search_fields = ['name', 'description']
    filterset_fields = []
    ordering_fields = ['create_time']
    ordering = ['-create_time']    

    @action(methods=['get'], detail=True, perms_map={'get':'workflow_update'}, pagination_class=None, serializer_class=StateSerializer)
    def states(self, request, pk=None):
        """
        工作流下的状态节点
        """
        wf = self.get_object()
        serializer = self.serializer_class(instance=WfService.get_worlflow_states(wf), many=True)
        return Response(serializer.data)
    
    @action(methods=['get'], detail=True, perms_map={'get':'workflow_update'}, pagination_class=None, serializer_class=TransitionSerializer)
    def transitions(self, request, pk=None):
        """
        工作流下的流转规则
        """
        wf = self.get_object()
        serializer = self.serializer_class(instance=WfService.get_workflow_transitions(wf), many=True)
        return Response(serializer.data)
    
    @action(methods=['get'], detail=True, perms_map={'get':'workflow_update'}, pagination_class=None, serializer_class=CustomFieldSerializer)
    def customfields(self, request, pk=None):
        """
        工作流下的自定义字段
        """
        wf = self.get_object()
        serializer = self.serializer_class(instance=CustomField.objects.filter(workflow=wf, is_deleted=False).order_by('sort'), many=True)
        return Response(serializer.data)
    
    @action(methods=['get'], detail=True, perms_map={'get':'workflow_init'})
    def init(self, request, pk=None):
        """
        新建工单初始化
        """
        ret={}
        wf = self.get_object()
        start_state = WfService.get_workflow_start_state(wf)
        transitions = WfService.get_state_transitions(start_state)
        ret['workflow'] = pk
        ret['transitions'] = TransitionSerializer(instance=transitions, many=True).data
        field_list = CustomFieldSerializer(instance=WfService.get_workflow_custom_fields(wf), many=True).data
        for i in field_list:
            if i['field_key'] in start_state.state_fields:
                i['field_attribute'] = start_state.state_fields[i['field_key']]
            else:
                i['field_attribute'] = State.STATE_FIELD_READONLY
        ret['field_list'] = field_list
        return Response(ret)

class StateViewSet(CreateModelMixin, UpdateModelMixin, RetrieveModelMixin, DestroyModelMixin, GenericViewSet):
    perms_map = {'get':'*', 'post':'workflow_update',
                'put':'workflow_update', 'delete':'workflow_update'}
    queryset = State.objects.all()
    serializer_class = StateSerializer
    search_fields = ['name']
    filterset_fields = ['workflow']
    ordering = ['sort']

class TransitionViewSet(CreateModelMixin, UpdateModelMixin, RetrieveModelMixin, DestroyModelMixin, GenericViewSet):
    perms_map = {'get':'*', 'post':'workflow_update',
                'put':'workflow_update', 'delete':'workflow_update'}
    queryset = Transition.objects.all()
    serializer_class = TransitionSerializer
    search_fields = ['name']
    filterset_fields = ['workflow']
    ordering = ['id']

class CustomFieldViewSet(CreateModelMixin, UpdateModelMixin, RetrieveModelMixin, DestroyModelMixin, GenericViewSet):
    perms_map = {'get':'*', 'post':'workflow_update',
                'put':'workflow_update', 'delete':'workflow_update'}
    queryset = CustomField.objects.all()
    serializer_class = CustomFieldSerializer
    search_fields = ['field_name']
    filterset_fields = ['workflow', 'field_type']
    ordering = ['sort']

    def get_serializer_class(self):
        if self.action in ['create', 'update']:
            return CustomFieldCreateUpdateSerializer
        return super().get_serializer_class()

class TicketViewSet(OptimizationMixin, CreateUpdateCustomMixin, CreateModelMixin, ListModelMixin, RetrieveModelMixin, GenericViewSet):
    perms_map = {'get':'*', 'post':'ticket_create'}
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer
    search_fields = ['title']
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
        return super().get_serializer_class()
    
    def filter_queryset(self, queryset):
        if not self.detail and not self.request.query_params.get('category', None):
            raise APIException('请指定查询分类')
        return super().filter_queryset(queryset)

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        """
        新建工单
        """
        rdata = request.data
        serializer = self.get_serializer(data=rdata)
        serializer.is_valid(raise_exception=True)
        vdata = serializer.validated_data #校验之后的数据
        start_state = WfService.get_workflow_start_state(vdata['workflow'])
        transition = vdata.pop('transition')
        ticket_data = vdata['ticket_data']

        save_ticket_data = {}
        # 校验必填项
        if transition.field_require_check:
            for key, value in start_state.state_fields.items(): 
                if int(value) == State.STATE_FIELD_REQUIRED:
                    if key not in ticket_data and not ticket_data[key]:
                        raise APIException('字段{}必填'.format(key))
                    save_ticket_data[key] = ticket_data[key]
                elif int(value) == State.STATE_FIELD_OPTIONAL:
                    save_ticket_data[key] = ticket_data[key]

        ticket = serializer.save(state=start_state, 
        create_by=request.user, 
        create_time=timezone.now(),
        act_state=Ticket.TICKET_ACT_STATE_DRAFT, 
        belong_dept=request.user.dept,
        ticket_data=save_ticket_data) # 先创建出来
        # 更新title和sn
        title = vdata.get('title', '')
        title_template = ticket.workflow.title_template
        if title_template:
            all_ticket_data = {**rdata, **ticket_data}
            title = title_template.format(**all_ticket_data)
        sn = WfService.get_ticket_sn(ticket.workflow) # 流水号
        ticket.sn = sn
        ticket.title = title
        ticket.save()
        ticket = WfService.handle_ticket(ticket=ticket, transition=transition, new_ticket_data=ticket_data, 
        handler=request.user, created=True)
        return Response(TicketSerializer(instance=ticket).data)

    @action(methods=['get'], detail=False, perms_map={'get':'*'})
    def duty_agg(self, request, pk=None):
        """
        工单待办聚合
        """
        ret = {}
        queryset = Ticket.objects.filter(participant__contains=request.user.id, is_deleted=False)\
            .exclude(act_state__in=[Ticket.TICKET_ACT_STATE_FINISH, Ticket.TICKET_ACT_STATE_CLOSED])
        ret['total_count'] = queryset.count()
        ret['details'] = list(queryset.values('workflow', 'workflow__name').annotate(count = Count('workflow')))
        return Response(ret)

    @action(methods=['post'], detail=True, perms_map={'post':'*'})
    @transaction.atomic
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

        ticket = WfService.handle_ticket(ticket=ticket, transition=vdata['transition'], 
        new_ticket_data=new_ticket_data, handler=request.user, suggestion=vdata['suggestion'])
        return Response(TicketSerializer(instance=ticket).data)
        

    @action(methods=['get'], detail=True, perms_map={'get':'*'})
    def flowsteps(self, request, pk=None):
        """
        工单流转step, 用于显示当前状态的step图(线性结构)
        """
        ticket = self.get_object()
        steps = WfService.get_ticket_steps(ticket)
        return Response(StateSerializer(instance=steps, many=True).data)

    @action(methods=['get'], detail=True, perms_map={'get':'*'})
    def flowlogs(self, request, pk=None):
        """
        工单流转记录
        """
        ticket = self.get_object()
        flowlogs = TicketFlow.objects.filter(ticket=ticket).order_by('-create_time')
        serializer = TicketFlowSerializer(instance=flowlogs, many=True)
        return Response(serializer.data)
    
    @action(methods=['get'], detail=True, perms_map={'get':'*'})
    def transitions(self, request, pk=None):
        """
        获取工单可执行的操作
        """
        ticket = self.get_object()
        transitions = WfService.get_ticket_transitions(ticket)
        return Response(TransitionSerializer(instance=transitions, many=True).data)

    @action(methods=['post'], detail=True, perms_map={'post':'*'})
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
            TicketFlow.objects.create(ticket=ticket, state=ticket.state, ticket_data=WfService.get_ticket_all_field_value(ticket),
                        suggestion='', participant_type=State.PARTICIPANT_TYPE_PERSONAL, intervene_type=Transition.TRANSITION_ATTRIBUTE_TYPE_ACCEPT,
                        participant=request.user, transition=None)
            return Response()
        else:
            raise APIException('无需接单')
    
    @action(methods=['post'], detail=True, perms_map={'post':'*'})
    def retreat(self, request, pk=None):
        """
        撤回工单，允许创建人在指定状态撤回工单至初始状态，状态设置中开启允许撤回
        """
        ticket = self.get_object()
        if ticket.create_by != request.user:
            raise APIException('非创建人不可撤回')
        if not ticket.state.enable_retreat:
            raise APIException('该状态不可撤回')
        start_state = WfService.get_workflow_start_state(ticket.workflow)
        ticket.state = start_state
        ticket.participant_type = State.PARTICIPANT_TYPE_PERSONAL
        ticket.participant = request.user.id
        ticket.act_state = Ticket.TICKET_ACT_STATE_RETREAT
        ticket.save()
        # 更新流转记录
        suggestion = request.data.get('suggestion', '') # 撤回原因
        TicketFlow.objects.create(ticket=ticket, state=ticket.state, ticket_data=WfService.get_ticket_all_field_value(ticket),
                        suggestion=suggestion, participant_type=State.PARTICIPANT_TYPE_PERSONAL, intervene_type=Transition.TRANSITION_INTERVENE_TYPE_RETREAT,
                        participant=request.user, transition=None)
        return Response()
    
    @action(methods=['post'], detail=True, perms_map={'post':'*'}, serializer_class=TicketAddNodeSerializer)
    def add_node(self, request, pk=None):
        """
        加签
        """
        ticket = self.get_object()
        data = request.data
        add_user = User.objects.get(pk=data['toadd_user'])
        ticket.participant_type = State.PARTICIPANT_TYPE_PERSONAL
        ticket.participant = add_user.id
        ticket.in_add_node = True
        ticket.add_node_man = request.user
        ticket.save()
        # 更新流转记录
        suggestion = request.data.get('suggestion', '') # 加签说明
        TicketFlow.objects.create(ticket=ticket, state=ticket.state, ticket_data=WfService.get_ticket_all_field_value(ticket),
                        suggestion=suggestion, participant_type=State.PARTICIPANT_TYPE_PERSONAL, intervene_type=Transition.TRANSITION_INTERVENE_TYPE_ADD_NODE,
                        participant=request.user, transition=None)
        return Response()

    @action(methods=['post'], detail=True, perms_map={'post':'*'}, serializer_class=TicketAddNodeEndSerializer)
    def add_node_end(self, request, pk=None):
        """
        加签完成
        """
        ticket = self.get_object()
        ticket.participant_type = State.PARTICIPANT_TYPE_PERSONAL
        ticket.in_add_node = False
        ticket.participant = ticket.add_node_man.id
        ticket.add_node_man = None
        ticket.save()
        # 更新流转记录
        suggestion = request.data.get('suggestion', '') # 加签意见
        TicketFlow.objects.create(ticket=ticket, state=ticket.state, ticket_data=WfService.get_ticket_all_field_value(ticket),
                        suggestion=suggestion, participant_type=State.PARTICIPANT_TYPE_PERSONAL, intervene_type=Transition.TRANSITION_INTERVENE_TYPE_ADD_NODE_END,
                        participant=request.user, transition=None)
        return Response()
    

    @action(methods=['post'], detail=True, perms_map={'post':'*'}, serializer_class=TicketCloseSerializer)
    def close(self, request, pk=None):
        """
        关闭工单(创建人在初始状态)
        """
        ticket = self.get_object()
        if ticket.state.type == State.STATE_TYPE_START and ticket.create_by==request.user:
            end_state = WfService.get_workflow_end_state(ticket.workflow)
            ticket.state = end_state
            ticket.participant_type = 0
            ticket.participant = 0
            ticket.act_state = Ticket.TICKET_ACT_STATE_CLOSED
            ticket.save()
            # 更新流转记录
            suggestion = request.data.get('suggestion', '') # 关闭原因
            TicketFlow.objects.create(ticket=ticket, state=ticket.state, ticket_data=WfService.get_ticket_all_field_value(ticket),
                            suggestion=suggestion, participant_type=State.PARTICIPANT_TYPE_PERSONAL, intervene_type=Transition.TRANSITION_INTERVENE_TYPE_CLOSE,
                            participant=request.user, transition=None)
            return Response()
        else:
            return Response('工单不可关闭', status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['post'], detail=False, perms_map={'post':'ticket_deletes'}, serializer_class=TicketDestorySerializer)
    def destory(self, request, pk=None):
        """
        批量物理删除
        """
        Ticket.objects.filter(id__in=request.data.get('ids', [])).delete(soft=False)
        return Response()



class TicketFlowViewSet(ListModelMixin, RetrieveModelMixin, GenericViewSet):
    """
    工单日志
    """
    perms_map = {'get':'*'}
    queryset = TicketFlow.objects.all()
    serializer_class = TicketFlowSerializer
    search_fields = ['suggestion']
    filterset_fields = ['ticket']
    ordering = ['-create_time']