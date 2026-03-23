from rest_framework import serializers

from people.serializers import SimpleEmployeeSerializer
from phish.models import (
    PhishReport, PhishReportTask, PhishTask, SyntheticPhish,
    SyntheticPhishTemplate, TrainingAssignment, TrainingTemplate
)
    

class PhishReportSerializer(serializers.HyperlinkedModelSerializer):
    
    class Meta:
        model = PhishReport
        fields = [
            'pk', 'employee', 'created_at', 'message', 'additional_info',
            'status', 'processed'
        ]

    employee = SimpleEmployeeSerializer(required=False)


class PhishTaskSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = PhishTask
        fields = ['pk', 'name', 'order']


class PhishReportTaskSerializer(serializers.HyperlinkedModelSerializer):

    completed_by = SimpleEmployeeSerializer(read_only=True)
    report_pk = serializers.IntegerField(source='report_id', read_only=True)
    task_pk = serializers.IntegerField(source='task_id', read_only=True)
    report = serializers.PrimaryKeyRelatedField(
        queryset=PhishReport.objects.all(), write_only=True
    )
    task = serializers.PrimaryKeyRelatedField(
        queryset=PhishTask.objects.all(), write_only=True
    )

    class Meta:
        model = PhishReportTask
        fields = [
            'pk', 'report_pk', 'task_pk', 'report', 'task',
            'completed_at', 'completed_by'
        ]


class SyntheticPhishTemplateSerializer(serializers.HyperlinkedModelSerializer):
    
    class Meta:
        model = SyntheticPhishTemplate
        fields = [
            'pk', 'name', 'version', 'subject', 'body', 'difficulty', 'active'
        ]


class SyntheticPhishSerializer(serializers.HyperlinkedModelSerializer):
    
    template_name = serializers.CharField(source='template.name', read_only=True)

    class Meta:
        model = SyntheticPhish
        fields = [
            'pk', 'employee', 'template_name', 'sent_at', 'clicked',
            'reported', 'reported_at'
        ]

    employee = SimpleEmployeeSerializer(required=True)


class TrainingTemplateSerializer(serializers.HyperlinkedModelSerializer):
    
    class Meta:
        model = TrainingTemplate
        fields = [
            'pk', 'name', 'version', 'content', 'active'
        ]


class TrainingAssignmentSerializer(serializers.HyperlinkedModelSerializer):
    
    training_name = serializers.CharField(source='template.name', read_only=True)
    template = TrainingTemplateSerializer(read_only=True)

    class Meta:
        model = TrainingAssignment
        fields = [
            'pk', 'employee', 'template', 'training_name', 'assigned_at',
            'completed', 'completed_at'
        ]

    employee = SimpleEmployeeSerializer(required=True)