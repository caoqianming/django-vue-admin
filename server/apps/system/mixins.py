from rest_framework import status
from rest_framework.response import Response
from rest_framework.settings import api_settings

class CreateModelAMixin:
    """
    业务用基本表A用
    """
    def perform_create(self, serializer):
        serializer.save(create_by = self.request.user)

class UpdateModelAMixin:
    """
    业务用基本表A用
    """
    def perform_update(self, serializer):
        serializer.save(update_by = self.request.user)

class CreateModelBMixin:
    """
    业务用基本表B用
    """
    def perform_create(self, serializer):
        serializer.save(create_by = self.request.user, belong_dept=self.request.user.dept)

class UpdateModelBMixin:
    """
    业务用基本表B用
    """
    def perform_update(self, serializer):
        serializer.save(update_by = self.request.user)