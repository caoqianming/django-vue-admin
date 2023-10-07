from django.conf import settings
from rest_framework import serializers


class MyFilePathField(serializers.CharField):

    def to_representation(self, value):
        if 'http' in value:
            return str(value)
        return settings.BASE_URL + str(value)
