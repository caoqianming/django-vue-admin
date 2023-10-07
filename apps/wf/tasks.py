# Create your tasks here
from __future__ import absolute_import, unicode_literals
import importlib
import logging
import traceback
from apps.system.models import User
from apps.utils.sms import send_sms
from apps.utils.tasks import CustomTask
from celery import shared_task
from apps.wf.models import State, Ticket, TicketFlow, Transition
from apps.wf.serializers import TicketDetailSerializer
import time
from apps.utils.tasks import send_mail_task
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

myLogger = logging.getLogger('log')

@shared_task(base=CustomTask)
def ticket_push(ticketId, userId):
    ticket = Ticket.objects.get(id=ticketId)
    channel_layer = get_channel_layer()
    data = {
        'type': 'ticket',
        'ticket': TicketDetailSerializer(instance=ticket).data,
        'msg': ''
    }
    async_to_sync(channel_layer.group_send)(f"user_{userId}", data)

@shared_task(base=CustomTask)
def send_ticket_notice(ticket_id):
    """
    发送通知
    """
    ticket = Ticket.objects.filter(id=ticket_id).first()
    params = {'workflow': ticket.workflow.name, 'state': ticket.state.name}
    if ticket:
        if ticket.participant_type == 1:
            # ws推送
            # 发送短信通知
            pt = User.objects.filter(id=ticket.participant).first()
            ticket_push.delay(ticket.id, pt.id)
            if pt and pt.phone:
                send_sms(pt.phone, 1002, params)
        elif ticket.participant_type == 2:
            pts = User.objects.filter(id__in=ticket.participant)
            for i in pts:
                ticket_push.delay(ticket.id, i.id)
                if i.phone:
                    send_sms(i.phone, 1002, params)


@shared_task(base=CustomTask)
def run_task(ticket_id: str, retry_num=1):
    ticket = Ticket.objects.get(id=ticket_id)
    transition_obj = Transition.objects.filter(
        source_state=ticket.state, is_deleted=False).first()
    script_result = True
    script_result_msg = ''
    script_str = ticket.participant
    try:
        module, func = script_str.rsplit(".", 1)
        m = importlib.import_module(module)
        f = getattr(m, func)
        f(ticket)
    except Exception:
        retry_num_new = retry_num - 1
        err_detail = traceback.format_exc()
        myLogger.error('工作流脚本执行失败', exc_info=True)
        script_result = False
        script_result_msg = err_detail
        if retry_num_new >= 0:
            time.sleep(10)
            run_task.delay(ticket_id, retry_num_new)
            return
        send_mail_task.delay(subject='wf_task_error', message=err_detail)   # run_task执行失败发送邮件
    ticket = Ticket.objects.filter(id=ticket_id).first()
    if not script_result:
        ticket.script_run_last_result = False
        ticket.save()
    # 记录日志
    TicketFlow.objects.create(ticket=ticket, state=ticket.state,
                              participant_type=State.PARTICIPANT_TYPE_ROBOT,
                              participant_str='func:{}'.format(script_str),
                              transition=transition_obj,
                              suggestion=script_result_msg)
    # 自动流转
    if script_result and transition_obj:
        from apps.wf.services import WfService
        WfService.handle_ticket(ticket=ticket, transition=transition_obj,
                                new_ticket_data=ticket.ticket_data, by_task=True)
