from typing import Tuple

from django.db import transaction
from django.db.models import Q, Exists, OuterRef, Sum, Max, Min, Avg, Count
from django.http import HttpResponse
from django.utils.timezone import localtime
from rest_framework import serializers as rest_serializers
from rest_framework.decorators import action
from rest_framework.response import Response

from core import exceptions, serializer_params, serializers


class HistoryViewSetMixin:

    @staticmethod
    def make_history_records(instance, history_records):
        offset = 0
        for record in history_records:
            if record.history_type == '~':
                new_record, old_record = instance.history.order_by('-history_date')[offset:offset + 2]
                delta = new_record.diff_against(old_record)
                changes = []
                for change in delta.changes:
                    changes.append({
                        'field': change.field,
                        'old': change.old,
                        'new': change.new
                    })
                for change in changes:
                    result = filter(
                        lambda item: getattr(item, 'name') == change['field'],
                        getattr(new_record.instance, '_meta').fields
                    )
                    try:
                        field = next(result)
                        if field.is_relation:
                            new = getattr(new_record, getattr(field, 'name', '-')).__str__()
                            old = getattr(old_record, getattr(field, 'name', '-')).__str__()

                            change['new'] = '-' if new == 'None' else new
                            change['old'] = '-' if old == 'None' else old

                        if field.choices and getattr(old_record, getattr(field, 'name')):
                            change['new'] = dict(field.choices)[getattr(new_record, getattr(field, 'name', '-'))]
                            change['old'] = dict(field.choices)[getattr(old_record, getattr(field, 'name', '-'))]
                    except StopIteration:
                        pass
                setattr(record, 'changes', changes)
            else:
                history = instance.history.get(pk=record.history_id)
                fields = getattr(history.instance, '_meta').fields
                changes = []
                for field in fields:
                    if not field.is_relation:
                        if field.choices and getattr(history, getattr(field, 'name', '-')):
                            changes.append(
                                {
                                    'field': getattr(field, 'name', '-'),
                                    'new': dict(field.choices)[getattr(history, getattr(field, 'name', '-'))]
                                }
                            )
                        else:
                            changes.append(
                                {
                                    'field': getattr(field, 'name', '-'),
                                    'new': getattr(history, getattr(field, 'name', '-'))
                                }
                            )
                    else:
                        new = getattr(history, getattr(field, 'name', '-')).__str__()
                        changes.append(
                            {
                                'field': getattr(field, 'name', '-'),
                                'new': '-' if new == 'None' else new
                            }
                        )
                setattr(record, 'changes', changes)
            offset += 1
        return history_records

    @action(detail=True, methods=['GET'])
    def history(self, request, pk, *args, **kwargs):
        instance = self.get_object()
        queryset = instance.history.select_related('history_user').order_by('-history_date')

        context = self.get_serializer_context()
        serializer_class = serializers.HistoryListSerializer

        page = self.paginate_queryset(queryset)
        if page is not None:
            results = self.make_history_records(instance=instance, history_records=page)
            serializer = serializer_class(results, many=True, context=context)
            return self.get_paginated_response(serializer.data)

        results = self.make_history_records(instance=instance, history_records=queryset)
        serializer = serializer_class(results, many=True, context=context)
        return Response(data=serializer.data)

    @action(detail=True, methods=['GET'])
    def associate_history(self, request, *args, **kwargs):
        from django.apps import apps
        serializer = serializer_params.AssociateHistoryParamSerialzier(
            data=request.query_params, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        associate_model = serializer.validated_data.get('associate_model')
        instance = apps.get_model(associate_model)

        parameters = {
            self.basename: getattr(self.get_object(), 'id'),
            'history_type__in': ['+', '-', '~']
        }

        queryset = instance.history.select_related('history_user').filter(**parameters).order_by('-history_date')
        context = self.get_serializer_context()
        serializer_class = serializers.HistoryListSerializer

        page = self.paginate_queryset(queryset)
        if page is not None:
            results = self.make_history_records(instance=instance, history_records=page)
            serializer = serializer_class(results, many=True, context=context)
            return self.get_paginated_response(serializer.data)

        results = self.make_history_records(instance=instance, history_records=queryset)
        serializer = serializer_class(results, many=True, context=context)
        return Response(data=serializer.data)


class ReorderViewSetMixin:
    reorder_root_field = None
    reorder_child_field = None
    reorder_serializer_class = None

    def order_on_create(self, root):
        order = 1

        children = getattr(root, self.reorder_child_field)
        item = children.order_by('order')
        if item:
            order = item.last().order + 1
        return order

    def order_on_delete(self, item):
        root = getattr(item, self.reorder_root_field)
        children = getattr(root, self.reorder_child_field)
        next_item = children.filter(
            order__gt=item.order
        ).order_by('order')

        if next_item.exists():
            order = item.order
            for it in next_item:
                it.order = order
                it.save()
                order += 1

    def order_on_update(self, item, item_to_move):
        if item_to_move.order > item.order:
            filters = Q(order__gte=item.order) & Q(
                order__lte=item_to_move.order)
            asc = True
        else:
            filters = Q(order__gte=item_to_move.order) & Q(
                order__lte=item.order)
            asc = False

        root = getattr(item, self.reorder_root_field)
        children = getattr(root, self.reorder_child_field)
        items = children.filter(filters)

        if items.exists():
            for it in items:
                it.order = it.order + 1 if asc else it.order - 1
                it.save()

        item_to_move.order = item.order
        item_to_move.save()

    def perform_create(self, serializer):
        order = self.order_on_create(
            root=serializer.validated_data[self.reorder_root_field])
        serializer.validated_data['order'] = order
        return super().perform_create(serializer=serializer)

    def perform_destroy(self, instance):
        self.order_on_delete(item=instance)
        return super().perform_destroy(instance=instance)

    @action(detail=True, methods=['PATCH'])
    def reorder(self, request, *args, **kwargs):
        rs = self.reorder_serializer_class(data=request.data)
        rs.is_valid(raise_exception=True)

        self.order_on_update(item=self.get_object(),
                             item_to_move=rs.validated_data['item_move'])
        return Response({'detail': True})


class AssociativeViewSetMixin:
    associate_model = None
    associate_fields = None

    def _get_associated_model(self):
        from django.apps import apps
        return apps.get_model(self.associate_model)

    def associated_queryset(self, **kwargs):
        if not self.associate_model or not self.associate_fields:
            raise NotImplementedError(
                'You must subclass and implement the controller validation')

        fields = dict()
        fields['%s_id' % self.associate_fields[0]] = OuterRef('pk')
        fields['%s_id' % self.associate_fields[1]] = kwargs['target']

        _model = self._get_associated_model()
        subquery = _model.objects.filter(**fields)
        return self.queryset.annotate(associated=Exists(subquery))

    @transaction.atomic
    def _associate_to_target(self, **kwargs):
        _model = self._get_associated_model()

        def _associate(source_id: int):
            fields = dict()
            fields['%s_id' % self.associate_fields[0]] = source_id
            fields['%s_id' % self.associate_fields[1]] = kwargs['target']

            instance, created = _model.objects.get_or_create(**fields)
            if not created and not kwargs['associated']:
                instance.delete()

        if kwargs['source'] > 0:
            _associate(source_id=kwargs['source'])
        else:
            self.queryset = self.associated_queryset(target=kwargs['target'])
            queryset = self.filter_queryset(self.queryset)
            for i in queryset.all():
                _associate(source_id=i.id)

    @action(detail=False, methods=['GET'])
    def find_associated(self, request, *args, **kwargs):
        rs = FindAssociatedSerializerMixin(data=request.query_params)
        rs.is_valid(raise_exception=True)

        self.queryset = self.associated_queryset(
            target=rs.validated_data['target'])
        return super().list(request, *args, **kwargs)

    @action(detail=False, methods=['POST'])
    def associate(self, request, *args, **kwargs):
        rs = AssociativeSerializerMixin(data=request.data)
        rs.is_valid(raise_exception=True)

        self._associate_to_target(**rs.validated_data)
        return Response(data={'detail': True})


class ReorderSerializerMixin(rest_serializers.Serializer):
    item_move = None


class FindAssociatedSerializerMixin(rest_serializers.Serializer):
    target = rest_serializers.IntegerField(required=True)


class AssociativeSerializerMixin(rest_serializers.Serializer):
    source = rest_serializers.IntegerField(required=True)
    target = rest_serializers.IntegerField(required=True)
    associated = rest_serializers.BooleanField(required=True)


class ViewSetExportMixin:
    export_fields = None
    export_fields_filters = True

    def _get_fields(self):
        fields = []
        columns = {}
        for field in self.export_fields:
            if isinstance(field, str):
                fields.append(field)
                columns[field] = field
            elif isinstance(field, tuple) or isinstance(field, list):
                fields.append(field[0])
                columns[field[0]] = field[1]

        return fields, columns

    @action(detail=False, methods=['POST'])
    def export(self, request, *args, **kwargs):
        if not self.export_fields:
            raise exceptions.ActionFailedException

        try:
            self.make_queryset_expandable(request)
        except Exception as e:
            print(e)
            pass

        # get fields to export
        fields, columns = self._get_fields()

        # get export fields values
        if self.export_fields_filters:
            queryset = self.filter_queryset(self.get_queryset())
        else:
            queryset = self.get_queryset()

        # no records found
        if not queryset.exists():
            raise exceptions.NoRecordFoundException

        # get fields from queryset
        queryset = queryset.values(*fields)

        # create data frame
        df = DataFrame.from_records(queryset, columns=fields)
        df = df.rename(index=str, columns=columns)

        # make csv name
        csv_name = '%s_%s.csv' % (
            self.basename, localtime().strftime('%d%m%y_%H%M%S'))

        # create response
        response = HttpResponse(content_type='text/csv', status=200)
        response['Content-Disposition'] = 'attachment; filename=' + csv_name
        response['file-name'] = csv_name

        df.to_csv(
            response,
            header=True,
            sep=';',
            index=None,
            float_format='%.2f',
            decimal=',',
            encoding='utf-8'
        )
        return response


class GroupByMixin:
    AGGREGATE_FUNCTIONS = {
        'sum': Sum,
        'max': Max,
        'min': Min,
        'avg': Avg,
        'count': Count
    }

    def _make_expression_aggregate(self, aggregates) -> Tuple[list, dict]:
        columns_names = []
        expressions = {}
        for aggregate in aggregates:
            column = aggregate.get('column')
            function = aggregate.get('function')
            distinct = aggregate.get('distinct', None)
            column_name_annotate = f'{function}_{column}'
            expressions[column_name_annotate] = self.AGGREGATE_FUNCTIONS[function](column) if distinct is None \
                else self.AGGREGATE_FUNCTIONS[function](column, distinct=distinct)
            columns_names.append(column_name_annotate)
        return columns_names, expressions

    def _make_ordering(self, request):
        ordering = request.query_params.get('ordering', [])
        if isinstance(ordering, str):
            ordering = ordering.split(',')
        return ordering

    def _generate_script_python(self, data: dict, url) -> dict:
        template_script = f"""
            import requests
            from requests.auth import HTTPBasicAuth

            data = {data}

            url = '{url}'

            basic = HTTPBasicAuth('Seu usuário', 'Sua senha')
            content = requests.get(url=url, data=json.dumps(data), params=params, auth=basic)
            result = content.json()
        """
        return {'script': template_script}

    @action(methods=['GET'], detail=False)
    def group_by(self, request, *args, **kwargs):
        result_serializer = serializer_params.GroupByParamSerializer(data=request.data, context={'request': request})
        result_serializer.is_valid(raise_exception=True)
        groups = result_serializer.validated_data.get('groups')

        if result_serializer.validated_data.get('generate_script'):
            result_serializer.validated_data.pop('generate_script')
            result = self._generate_script_python(
                data=result_serializer.initial_data,
                url=request.build_absolute_uri()
            )
            import mimetypes
            import tempfile

            with tempfile.NamedTemporaryFile(suffix='.py') as tmp:
                tmp.write(bytes(result['script'], 'utf-8'))
                tmp.seek(0)
                mime_type, _ = mimetypes.guess_type(tmp.name)
                response = HttpResponse(tmp.read(), content_type=mime_type)

                response['Content-Disposition'] = "attachment; filename=%s" % 'script.py'
                return response

        filter_instance = self.filterset_class(request.GET, queryset=self.get_queryset())
        column_names, expressions = self._make_expression_aggregate(result_serializer.validated_data.get('aggregates'))
        ordering_fields = self._make_ordering(request)

        try:
            if len(groups):
                queryset = filter_instance.qs.values(*groups) \
                    .annotate(**expressions) \
                    .values(*groups, *column_names)
                queryset = queryset.order_by(*ordering_fields)

            else:
                queryset = filter_instance.qs.aggregate(**expressions)

        except Exception as e:
            raise exceptions.ExecuteQueryException(cause=str(e))

        return Response(data=queryset, status=200)
