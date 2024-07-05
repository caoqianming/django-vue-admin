import threading
from apps.utils.decorators import auto_log

class MyThread(threading.Thread):

    @auto_log('MyThread', raise_exception=True, send_mail=True)
    def run(self) -> None:
        return super().run()
    