from rest_framework import serializers

from core import exceptions


class AssociateHistoryParamSerialzier(serializers.Serializer):
    associate_model = serializers.CharField(max_length=104, required=True)


class AggregateSerializer(serializers.Serializer):
    FUNCTIONS = (
        ('sum', 'Sum'),
        ('min', 'Min'),
        ('max', 'Max'),
        ('avg', 'Avg'),
        ('count', 'Count'),
    )
    column = serializers.CharField(required=True, max_length=256)
    function = serializers.ChoiceField(choices=FUNCTIONS, required=True)
    distinct = serializers.BooleanField(required=False)


class GroupByParamSerializer(serializers.Serializer):
    groups = serializers.ListSerializer(child=serializers.CharField(), required=True, allow_empty=True)
    aggregates = serializers.ListSerializer(child=AggregateSerializer())
    generate_script = serializers.BooleanField(default=False)

    def validate(self, attrs):
        parameters = ['limit', 'offset']
        if any(item in parameters for item in self.context['request'].query_params):
            raise exceptions.InvalidPaginatedParametersException
        return super().validate(attrs)
