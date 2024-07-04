import threading
import logging
from apps.utils.tasks import send_mail_task
import traceback

logger = logging.getLogger('log')

class MyThread(threading.Thread):
    def __init__(self, log_err=False, send_err=False):
        super().__init__()
        self.send_err = send_err
        self.log_err = log_err

    def run(self):
        try:
            if self._target:
                self._target(*self._args, **self._kwargs)
        except Exception as e:
            if self.log_err:
                logger.error(f"Thread error: {e}", exc_info=False)
            if self.send_err:
                send_mail_task.delay(message=traceback.format_exc())
            raise