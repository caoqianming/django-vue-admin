from django.contrib import admin
from apps.wf.models import State, Transition, Workflow
# Register your models here.


@admin.register(Workflow)
class WorkflowAdmin(admin.ModelAdmin):
    date_hierarchy = 'create_time'


@admin.register(State)
class StateAdmin(admin.ModelAdmin):
    date_hierarchy = 'create_time'


@admin.register(Transition)
class TransitionAdmin(admin.ModelAdmin):
    date_hierarchy = 'create_time'