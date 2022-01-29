from django.db.models import base
from rest_framework import urlpatterns
from apps.wf.views import CustomFieldViewSet, FromCodeListView, StateViewSet, TicketFlowViewSet, TicketViewSet, TransitionViewSet, WorkflowViewSet
from django.urls import path, include
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('workflow', WorkflowViewSet, basename='wf')
router.register('state', StateViewSet, basename='wf_state')
router.register('transition', TransitionViewSet, basename='wf_transitions')
router.register('customfield', CustomFieldViewSet, basename='wf_customfield')
router.register('ticket', TicketViewSet, basename='wf_ticket')
router.register('ticketflow', TicketFlowViewSet, basename='wf_ticketflow')
urlpatterns = [
    path('participant_from_code', FromCodeListView.as_view()),
    path('', include(router.urls)),
]

