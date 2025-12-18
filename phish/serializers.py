from rest_framework import serializers

from people.serializers import SimpleEmployeeSerializer
from phish.models import PhishReport

class PhishReportSerializer(serializers.HyperlinkedModelSerializer):
    
    class Meta:
        model = PhishReport
        fields = [
            'url', 'pk', 'employee', 'timestamp', 'message', 'organic'
        ]

    employee = SimpleEmployeeSerializer(required=False)