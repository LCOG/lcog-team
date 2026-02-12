from rest_framework import serializers

from people.serializers import SimpleEmployeeSerializer
from phish.models import PhishReport, SyntheticPhish, SyntheticPhishTemplate

class PhishReportSerializer(serializers.HyperlinkedModelSerializer):
    
    class Meta:
        model = PhishReport
        fields = [
            'url', 'pk', 'employee', 'created_at', 'message', 'processed'
        ]

    employee = SimpleEmployeeSerializer(required=False)


class SyntheticPhishTemplateSerializer(serializers.HyperlinkedModelSerializer):
    
    class Meta:
        model = SyntheticPhishTemplate
        fields = [
            'url', 'pk', 'name', 'version', 'subject', 'body', 'difficulty',
            'active'
        ]


class SyntheticPhishSerializer(serializers.HyperlinkedModelSerializer):
    
    template_name = serializers.CharField(source='template.name', read_only=True)

    class Meta:
        model = SyntheticPhish
        fields = [
            'url', 'pk', 'employee', 'template_name', 'sent_at', 'clicked',
            'reported', 'reported_at'
        ]

    employee = SimpleEmployeeSerializer(required=False)