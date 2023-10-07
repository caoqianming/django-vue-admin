from django.db import models

EXCLUDE_FIELDS_BASE = ['create_time', 'update_time', 'is_deleted']
EXCLUDE_FIELDS = ['create_time', 'update_time', 'is_deleted', 'create_by', 'update_by']
EXCLUDE_FIELDS_DEPT = EXCLUDE_FIELDS + ['belong_dept']
