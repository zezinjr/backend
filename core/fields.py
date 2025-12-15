from django.db import models
from django.utils import timezone
from rest_framework.fields import CharField, DateTimeField


class DateTimeFieldWithTZ(DateTimeField):
    def to_representation(self, value):
        value = timezone.localtime(value)
        return super().to_representation(value)


class NullCharField(CharField):
    def to_representation(self, value):
        if value == '':
            return None
        return super().to_representation(value)


class CustomJsonField(models.JSONField):
    def from_db_value(self, value, expression, connection):
        if isinstance(value, dict):
            return value
        return super().from_db_value(value, expression, connection)
