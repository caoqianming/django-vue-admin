from apps.system.models import User
from apps.wf.models import State, Ticket, TicketFlow, Transition


class GetParticipants:
    """
    获取处理人脚本
    """
    all_funcs = [
        {'func':'get_create_by', 'name':'获取工单创建人'}
    ]

    # def all_funcs(self):
    #     # return list(filter(lambda x: x.startswith('get_') and callable(getattr(self, x)), dir(self)))
    #     return [(func, getattr(self, func).__doc__) for func in dir(self) if callable(getattr(self, func)) and func.startswith('get_')]

    @classmethod
    def get_create_by(cls, state:dict={}, ticket:dict={}, new_ticket_data:dict={}, handler:User={}):
        """工单创建人"""
        participant = ticket.create_by.id
        return participant

class HandleScripts:
    """
    任务处理脚本
    """
    all_funcs = [
        {'func': 'handle_something', 'name':'处理一些工作'}
    ]


    @classmethod
    def to_next(cls, ticket:Ticket, by_timer:bool=False, by_task:bool=False, by_hook:bool=False, script_str:str=''):
        # 获取信息      
        transition_obj = Transition.objects.filter(source_state=ticket.state, is_deleted=False).first()

        TicketFlow.objects.create(ticket=ticket, state=ticket.state,
                            participant_type=State.PARTICIPANT_TYPE_ROBOT,
                            participant_str='func:{}'.format(script_str),
                            transition=transition_obj)
        from .services import WfService

        # 自动执行流转
        WfService.handle_ticket(ticket=ticket, transition=transition_obj, new_ticket_data=ticket.ticket_data, by_task=True)

        return ticket

    @classmethod
    def handle_something(cls, ticket:Ticket):
        """处理一些工作"""
        # 任务处理代码区


        # 调用自动流转
        ticket = cls.to_next(ticket=ticket, by_task=True, script_str= 'handle_something')
        
