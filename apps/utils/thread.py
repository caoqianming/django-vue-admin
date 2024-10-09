import threading
from apps.utils.decorators import auto_log
from concurrent.futures import ThreadPoolExecutor

# 创建全局线程池
global_executor = ThreadPoolExecutor(max_workers=20)
class MyThread(threading.Thread):

    @auto_log('MyThread', raise_exception=True, send_mail=True)
    def run(self) -> None:
        return super().run()

    def start_p(self):
        """
        使用线程池启动
        """
        global_executor.submit(self.run)