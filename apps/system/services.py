from apps.system.models import Dept
from django.conf import settings
from apps.third.tapis import dhapis
from apps.third.dahua import dhClient


def sync_dahua_dept(dept: Dept):
    # 同步大华部门信息
    third_info = dept.third_info
    if settings.DAHUA_ENABLED:
        if third_info.get('dh_id', False):
            data = {
            "id": dept.third_info['dh_id'],
            "parentId": 1,
            "name": dept.name
            }
            dhClient.request(**dhapis['dept_update'], json=data)
        else:
            # 如果dh_id 不存在
            data = {
                "parentId": 1,
                "name": dept.name,
                "service": "ehs"
            }
            _, res = dhClient.request(**dhapis['dept_create'], json=data)
            third_info['dh_id'] = res['id']
            dept.third_info = third_info
            dept.save()  
        dhClient.face_bind()
