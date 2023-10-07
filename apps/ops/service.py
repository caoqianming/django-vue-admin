import psutil

class ServerService:
    @classmethod
    def get_memory_dict(cls):
        ret = {}
        memory = psutil.virtual_memory()
        ret['total'] = round(memory.total/1024/1024/1024, 2)
        ret['used'] = round(memory.used/1024/1024/1024, 2)
        ret['percent'] = memory.percent
        return ret

    @classmethod
    def get_cpu_dict(cls):
        ret = {}
        ret['lcount'] = psutil.cpu_count()
        ret['count'] = psutil.cpu_count(logical=False)
        ret['percent'] = psutil.cpu_percent(interval=1)
        return ret
    
    @classmethod
    def get_disk_dict(cls):
        ret = {}
        disk = psutil.disk_usage('/')
        ret['total'] = round(disk.total/1024/1024/1024, 2)
        ret['used'] = round(disk.used/1024/1024/1024, 2)
        ret['percent'] = disk.percent
        return ret

    @classmethod
    def get_full(cls):
        return {'cpu': cls.get_cpu_dict(), 'memory': cls.get_memory_dict(), 'disk': cls.get_disk_dict()}
