from django.contrib import admin
from .models import User, Dept, Role, Permission, DictType, Dictionary, File
# Register your models here.
admin.site.register(User)
admin.site.register(Dept)
admin.site.register(Role)
admin.site.register(Permission)
admin.site.register(DictType)
admin.site.register(Dictionary)
admin.site.register(File)
