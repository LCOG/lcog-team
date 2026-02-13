from rest_framework import serializers

from people.serializers import SimpleEmployeeSerializer
from phish.models import (
    PhishReport, SyntheticPhish, SyntheticPhishTemplate, TrainingAssignment,
    TrainingTemplate
)
    

class PhishReportSerializer(serializers.HyperlinkedModelSerializer):
    
    class Meta:
        model = PhishReport
        fields = [
            'pk', 'employee', 'created_at', 'message', 'processed'
        ]

    employee = SimpleEmployeeSerializer(required=False)


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

    class Meta:
        model = TrainingAssignment
        fields = [
            'pk', 'employee', 'training_name', 'assigned_at', 'completed',
            'completed_at'
        ]

    employee = SimpleEmployeeSerializer(required=True)