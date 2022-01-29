from random import choice
from django.db import models
from django.db.models.base import Model
import django.utils.timezone as timezone
from django.db.models.query import QuerySet
from apps.system.models import CommonAModel, CommonBModel, Organization, User, Dict, File
from utils.model import SoftModel, BaseModel
from simple_history.models import HistoricalRecords


class Workflow(CommonAModel):
    """
    工作流
    """
    name = models.CharField('名称', max_length=50)
    key = models.CharField('工作流标识', unique=True, max_length=20, null=True, blank=True)
    sn_prefix = models.CharField('流水号前缀', max_length=50, default='hb')
    description = models.CharField('描述', max_length=200, null=True, blank=True)
    view_permission_check = models.BooleanField('查看权限校验', default=True, help_text='开启后，只允许工单的关联人(创建人、曾经的处理人)有权限查看工单')
    limit_expression = models.JSONField('限制表达式', default=dict, blank=True, help_text='限制周期({"period":24} 24小时), 限制次数({"count":1}在限制周期内只允许提交1次), 限制级别({"level":1} 针对(1单个用户 2全局)限制周期限制次数,默认特定用户);允许特定人员提交({"allow_persons":"zhangsan,lisi"}只允许张三提交工单,{"allow_depts":"1,2"}只允许部门id为1和2的用户提交工单，{"allow_roles":"1,2"}只允许角色id为1和2的用户提交工单)')
    display_form_str = models.JSONField('展现表单字段', default=list, blank=True, help_text='默认"[]"，用于用户只有对应工单查看权限时显示哪些字段,field_key的list的json,如["days","sn"],内置特殊字段participant_info.participant_name:当前处理人信息(部门名称、角色名称)，state.state_name:当前状态的状态名,workflow.workflow_name:工作流名称')
    title_template = models.CharField('标题模板', max_length=50, default='{title}', null=True, blank=True, help_text='工单字段的值可以作为参数写到模板中，格式如：你有一个待办工单:{title}')
    content_template = models.CharField('内容模板', max_length=1000, default='标题:{title}, 创建时间:{create_time}', null=True, blank=True, help_text='工单字段的值可以作为参数写到模板中，格式如：标题:{title}, 创建时间:{create_time}')

class State(CommonAModel):
    """
    状态记录
    """
    STATE_TYPE_START = 1
    STATE_TYPE_END = 2
    type_choices = (
        (0, '普通'),
        (STATE_TYPE_START, '开始'),
        (STATE_TYPE_END, '结束')
    )
    PARTICIPANT_TYPE_PERSONAL = 1
    PARTICIPANT_TYPE_MULTI = 2
    PARTICIPANT_TYPE_DEPT = 3
    PARTICIPANT_TYPE_ROLE = 4
    PARTICIPANT_TYPE_VARIABLE = 5
    PARTICIPANT_TYPE_ROBOT = 6
    PARTICIPANT_TYPE_FIELD = 7
    PARTICIPANT_TYPE_PARENT_FIELD = 8
    PARTICIPANT_TYPE_FORMCODE = 9
    state_participanttype_choices = (
        (0, '无处理人'),
        (PARTICIPANT_TYPE_PERSONAL, '个人'),
        (PARTICIPANT_TYPE_MULTI, '多人'),
        # (PARTICIPANT_TYPE_DEPT, '部门'),
        (PARTICIPANT_TYPE_ROLE, '角色'),
        # (PARTICIPANT_TYPE_VARIABLE, '变量'),
        (PARTICIPANT_TYPE_ROBOT, '脚本'),
        (PARTICIPANT_TYPE_FIELD, '工单的字段'),
        # (PARTICIPANT_TYPE_PARENT_FIELD, '父工单的字段'),
        (PARTICIPANT_TYPE_FORMCODE, '代码获取')
    )
    STATE_DISTRIBUTE_TYPE_ACTIVE = 1 # 主动接单
    STATE_DISTRIBUTE_TYPE_DIRECT = 2 # 直接处理(当前为多人的情况，都可以处理，而不需要先接单)
    STATE_DISTRIBUTE_TYPE_RANDOM = 3 # 随机分配
    STATE_DISTRIBUTE_TYPE_ALL = 4 # 全部处理
    state_distribute_choices=(
        (STATE_DISTRIBUTE_TYPE_ACTIVE, '主动接单'),
        (STATE_DISTRIBUTE_TYPE_DIRECT, '直接处理'),
        (STATE_DISTRIBUTE_TYPE_RANDOM, '随机分配'),
        (STATE_DISTRIBUTE_TYPE_ALL, '全部处理'),
    )

    STATE_FIELD_READONLY= 1 # 字段只读
    STATE_FIELD_REQUIRED = 2 # 字段必填
    STATE_FIELD_OPTIONAL = 3 # 字段可选
    STATE_FIELD_HIDDEN = 4 # 字段隐藏
    state_filter_choices=(
        (0, '无'),
        (1, '和工单同属一及上级部门'),
        (2, '和创建人同属一及上级部门'),
        (3, '和上步处理人同属一及上级部门'),
    )
    name = models.CharField('名称', max_length=50)
    workflow = models.ForeignKey(Workflow, on_delete=models.CASCADE, verbose_name='所属工作流')
    is_hidden = models.BooleanField('是否隐藏', default=False, help_text='设置为True时,获取工单步骤api中不显示此状态(当前处于此状态时除外)')
    sort = models.IntegerField('状态顺序', default=0, help_text='用于工单步骤接口时，step上状态的顺序(因为存在网状情况，所以需要人为设定顺序),值越小越靠前')
    type = models.IntegerField('状态类型', default=0, choices=type_choices, help_text='0.普通类型 1.初始状态(用于新建工单时,获取对应的字段必填及transition信息) 2.结束状态(此状态下的工单不得再处理，即没有对应的transition)')
    enable_retreat = models.BooleanField('允许撤回', default=False, help_text='开启后允许工单创建人在此状态直接撤回工单到初始状态')
    participant_type = models.IntegerField('参与者类型', choices=state_participanttype_choices, default=1, blank=True, help_text='0.无处理人,1.个人,2.多人,3.部门,4.角色,5.变量(支持工单创建人,创建人的leader),6.脚本,7.工单的字段内容(如表单中的"测试负责人"，需要为用户名或者逗号隔开的多个用户名),8.父工单的字段内容。 初始状态请选择类型5，参与人填create_by')
    participant = models.JSONField('参与者', default=list, blank=True, help_text='可以为空(无处理人的情况，如结束状态)、userid、userid列表\部门id\角色id\变量(create_by,create_by_tl)\脚本记录的id等，包含子工作流的需要设置处理人为loonrobot')
    state_fields = models.JSONField('表单字段', default=dict, help_text='json格式字典存储,包括读写属性1：只读，2：必填，3：可选, 4:隐藏 示例：{"create_time":1,"title":2, "sn":1}, 内置特殊字段participant_info.participant_name:当前处理人信息(部门名称、角色名称)，state.state_name:当前状态的状态名,workflow.workflow_name:工作流名称')  # json格式存储,包括读写属性1：只读，2：必填，3：可选，4：不显示, 字典的字典
    distribute_type = models.IntegerField('分配方式', default=1, choices=state_distribute_choices, help_text='1.主动接单(如果当前处理人实际为多人的时候，需要先接单才能处理) 2.直接处理(即使当前处理人实际为多人，也可以直接处理) 3.随机分配(如果实际为多人，则系统会随机分配给其中一个人) 4.全部处理(要求所有参与人都要处理一遍,才能进入下一步)')
    filter_policy = models.IntegerField('参与人过滤策略', default=0, choices=state_filter_choices)
    participant_cc = models.JSONField('抄送给', default=list, blank=True, help_text='抄送给(userid列表)')

class Transition(CommonAModel):
    """
    工作流流转，定时器，条件(允许跳过)， 条件流转与定时器不可同时存在
    """
    TRANSITION_ATTRIBUTE_TYPE_ACCEPT = 1  # 同意
    TRANSITION_ATTRIBUTE_TYPE_REFUSE = 2  # 拒绝
    TRANSITION_ATTRIBUTE_TYPE_OTHER = 3  # 其他
    attribute_type_choices = (
        (1, '同意'),
        (2, '拒绝'),
        (3, '其他')
    )
    TRANSITION_INTERVENE_TYPE_DELIVER = 1  # 转交操作
    TRANSITION_INTERVENE_TYPE_ADD_NODE = 2  # 加签操作
    TRANSITION_INTERVENE_TYPE_ADD_NODE_END = 3  # 加签处理完成
    TRANSITION_INTERVENE_TYPE_ACCEPT = 4  # 接单操作
    TRANSITION_INTERVENE_TYPE_COMMENT = 5  # 评论操作
    TRANSITION_INTERVENE_TYPE_DELETE = 6  # 删除操作
    TRANSITION_INTERVENE_TYPE_CLOSE = 7  # 强制关闭操作
    TRANSITION_INTERVENE_TYPE_ALTER_STATE = 8  # 强制修改状态操作
    TRANSITION_INTERVENE_TYPE_HOOK = 9  # hook操作
    TRANSITION_INTERVENE_TYPE_RETREAT = 10  # 撤回
    TRANSITION_INTERVENE_TYPE_CC = 11 # 抄送

    intervene_type_choices = (
        (0, '正常处理'),
        (TRANSITION_INTERVENE_TYPE_DELIVER, '转交'),
        (TRANSITION_INTERVENE_TYPE_ADD_NODE, '加签'),
        (TRANSITION_INTERVENE_TYPE_ADD_NODE_END, '加签处理完成'),
        (TRANSITION_INTERVENE_TYPE_ACCEPT, '接单'),
        (TRANSITION_INTERVENE_TYPE_COMMENT, '评论'),
        (TRANSITION_INTERVENE_TYPE_DELETE, '删除'),
        (TRANSITION_INTERVENE_TYPE_CLOSE, '强制关闭'),
        (TRANSITION_INTERVENE_TYPE_ALTER_STATE, '强制修改状态'),
        (TRANSITION_INTERVENE_TYPE_HOOK, 'hook操作'),
        (TRANSITION_INTERVENE_TYPE_RETREAT, '撤回'),
        (TRANSITION_INTERVENE_TYPE_CC, '抄送')
    )

    name = models.CharField('操作', max_length=50)
    workflow = models.ForeignKey(Workflow, on_delete=models.CASCADE, verbose_name='所属工作流')
    timer = models.IntegerField('定时器(单位秒)', default=0, help_text='单位秒。处于源状态X秒后如果状态都没有过变化则自动流转到目标状态。设置时间有效')
    source_state = models.ForeignKey(State, on_delete=models.CASCADE, verbose_name='源状态', related_name='sstate_transition')
    destination_state = models.ForeignKey(State, on_delete=models.CASCADE, verbose_name='目的状态', related_name='dstate_transition')
    condition_expression = models.JSONField('条件表达式', max_length=1000, default=list, help_text='流转条件表达式，根据表达式中的条件来确定流转的下个状态，格式为[{"expression":"{days} > 3 and {days}<10", "target_state":11}] 其中{}用于填充工单的字段key,运算时会换算成实际的值，当符合条件下个状态将变为target_state_id中的值,表达式只支持简单的运算或datetime/time运算.loonflow会以首次匹配成功的条件为准，所以多个条件不要有冲突' )
    attribute_type = models.IntegerField('属性类型', default=1, choices=attribute_type_choices, help_text='属性类型，1.同意，2.拒绝，3.其他')
    field_require_check = models.BooleanField('是否校验必填项', default=True, help_text='默认在用户点击操作的时候需要校验工单表单的必填项,如果设置为否则不检查。用于如"退回"属性的操作，不需要填写表单内容')


class CustomField(CommonAModel):
    """自定义字段, 设定某个工作流有哪些自定义字段"""
    field_type_choices = (
        ('string', '字符串'),
        ('int', '整型'),
        ('float', '浮点'),
        ('boolean', '布尔'),
        ('date', '日期'),
        ('datetime', '日期时间'),
        ('radio', '单选'),
        ('checkbox', '多选'),
        ('select', '单选下拉'),
        ('selects', '多选下拉'),
        ('cascader', '单选级联'),
        ('cascaders', '多选级联'),
        ('select_dg', '弹框单选'),
        ('select_dgs', '弹框多选'),
        ('textarea', '文本域'),
        ('file', '附件')
    )
    workflow = models.ForeignKey(Workflow, on_delete=models.CASCADE, verbose_name='所属工作流')
    field_type = models.CharField('类型', max_length=50, choices=field_type_choices, 
    help_text='string, int, float, date, datetime, radio, checkbox, select, selects, cascader, cascaders, select_dg, select_dgs,textarea, file')
    field_key = models.CharField('字段标识', max_length=50, help_text='字段类型请尽量特殊，避免与系统中关键字冲突')
    field_name = models.CharField('字段名称', max_length=50)
    sort = models.IntegerField('排序', default=0, help_text='工单基础字段在表单中排序为:流水号0,标题20,状态id40,状态名41,创建人80,创建时间100,更新时间120.前端展示工单信息的表单可以根据这个id顺序排列')
    default_value = models.CharField('默认值', null=True, blank=True, max_length=100, help_text='前端展示时，可以将此内容作为表单中的该字段的默认值')
    description = models.CharField('描述', max_length=100, blank=True, null=True, help_text='字段的描述信息，可用于显示在字段的下方对该字段的详细描述')
    placeholder = models.CharField('占位符', max_length=100, blank=True, null=True, help_text='用户工单详情表单中作为字段的占位符显示')
    field_template = models.TextField('文本域模板', null=True, blank=True, help_text='文本域类型字段前端显示时可以将此内容作为字段的placeholder')
    boolean_field_display = models.JSONField('布尔类型显示名', default=dict, blank=True,
                                             help_text='当为布尔类型时候，可以支持自定义显示形式。{"1":"是","0":"否"}或{"1":"需要","0":"不需要"}，注意数字也需要引号')
    
    field_choice = models.JSONField('选项值', default=list, blank=True,
                                    help_text='选项值，格式为list, 例["id":1, "name":"张三"]')
    
    label = models.CharField('标签', max_length=1000, default='', help_text='处理特殊逻辑使用,比如sys_user用于获取用户作为选项')
    # hook = models.CharField('hook', max_length=1000, default='', help_text='获取下拉选项用于动态选项值')
    is_hidden = models.BooleanField('是否隐藏', default=False, help_text='可用于携带不需要用户查看的字段信息')

class Ticket(CommonBModel):
    """
    工单
    """
    TICKET_ACT_STATE_DRAFT = 0  # 草稿中
    TICKET_ACT_STATE_ONGOING = 1  # 进行中
    TICKET_ACT_STATE_BACK = 2  # 被退回
    TICKET_ACT_STATE_RETREAT = 3  # 被撤回
    TICKET_ACT_STATE_FINISH = 4  # 已完成
    TICKET_ACT_STATE_CLOSED = 5  # 已关闭

    act_state_choices =(
        (TICKET_ACT_STATE_DRAFT, '草稿中'),
        (TICKET_ACT_STATE_ONGOING, '进行中'),
        (TICKET_ACT_STATE_BACK, '被退回'),
        (TICKET_ACT_STATE_RETREAT, '被撤回'),
        (TICKET_ACT_STATE_FINISH, '已完成'),
        (TICKET_ACT_STATE_CLOSED, '已关闭')
    )
    category_choices =(
        ('all', '全部'),
        ('owner', '我创建的'),
        ('duty', '待办'),
        ('worked', '我处理的'),
        ('cc', '抄送我的')
    )
    title = models.CharField('标题', max_length=500, null=True, blank=True, help_text="工单标题")
    workflow = models.ForeignKey(Workflow, on_delete=models.CASCADE, verbose_name='关联工作流')
    sn = models.CharField('流水号', max_length=25, help_text="工单的流水号")
    state = models.ForeignKey(State, on_delete=models.CASCADE, verbose_name='当前状态', related_name='ticket_state')
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, verbose_name='父工单')
    parent_state = models.ForeignKey(State, null=True, blank=True, on_delete=models.CASCADE, verbose_name='父工单状态', related_name='ticket_parent_state')
    ticket_data = models.JSONField('工单数据', default=dict, help_text='工单自定义字段内容')
    in_add_node = models.BooleanField('加签状态中', default=False, help_text='是否处于加签状态下')
    add_node_man = models.ForeignKey(User, verbose_name='加签人', on_delete=models.SET_NULL, null=True, blank=True, help_text='加签操作的人，工单当前处理人处理完成后会回到该处理人，当处于加签状态下才有效')
    script_run_last_result = models.BooleanField('脚本最后一次执行结果', default=True)
    participant_type = models.IntegerField('当前处理人类型', default=0, help_text='0.无处理人,1.个人,2.多人', choices=State.state_participanttype_choices)
    participant = models.JSONField('当前处理人', default=list, blank=True, help_text='可以为空(无处理人的情况，如结束状态)、userid、userid列表')
    act_state = models.IntegerField('进行状态', default=1, help_text='当前工单的进行状态', choices=act_state_choices)
    multi_all_person = models.JSONField('全部处理的结果', default=dict, blank=True, help_text='需要当前状态处理人全部处理时实际的处理结果，json格式')


class TicketFlow(BaseModel):
    """
    工单流转日志
    """
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, verbose_name='关联工单', related_name='ticketflow_ticket')
    transition = models.ForeignKey(Transition, verbose_name='流转id', help_text='与worklow.Transition关联， 为空时表示认为干预的操作', on_delete=models.CASCADE, null=True, blank=True)
    suggestion = models.CharField('处理意见', max_length=10000, default='', blank=True)
    participant_type = models.IntegerField('处理人类型', default=0, help_text='0.无处理人,1.个人,2.多人等', choices=State.state_participanttype_choices)
    participant = models.ForeignKey(User, verbose_name='处理人', on_delete=models.SET_NULL, null=True, blank=True, related_name='ticketflow_participant')
    participant_str = models.CharField('处理人', max_length=200, null=True, blank=True, help_text='非人工处理的处理人相关信息')
    state = models.ForeignKey(State, verbose_name='当前状态', default=0, blank=True, on_delete=models.CASCADE)
    ticket_data = models.JSONField('工单数据', default=dict, blank=True, help_text='可以用于记录当前表单数据，json格式')
    intervene_type = models.IntegerField('干预类型', default=0, help_text='流转类型', choices=Transition.intervene_type_choices)
    participant_cc = models.JSONField('抄送给', default=list, blank=True, help_text='抄送给(userid列表)')

