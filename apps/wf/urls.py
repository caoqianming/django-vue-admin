from apps.wf.views import CustomFieldViewSet, StateViewSet, TicketFlowViewSet, \
                        TicketViewSet, TransitionViewSet, WorkflowKeyInitView, WorkflowViewSet
from django.urls import path, include
from rest_framework.routers import DefaultRouter

API_BASE_URL = 'api/wf/'
HTML_BASE_URL = 'wf/'

router = DefaultRouter()
router.register('workflow', WorkflowViewSet, basename='workflow')
router.register('state', StateViewSet, basename='state')
router.register('transition', TransitionViewSet, basename='transition')
router.register('customfield', CustomFieldViewSet, basename='customfield')
router.register('ticket', TicketViewSet, basename='ticket')
router.register('ticketflow', TicketFlowViewSet, basename='ticketflow')
urlpatterns = [
    path(API_BASE_URL, include(router.urls)),
    path(API_BASE_URL + 'workflow/<str:key>/init_key/', WorkflowKeyInitView.as_view())
]
