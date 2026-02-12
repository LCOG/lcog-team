import re

from django.contrib.auth.models import User
from rest_framework import status, viewsets
from rest_framework.response import Response

from mainsite.helpers import send_email
from people.models import Employee
from phish.models import PhishReport, SyntheticPhish, SyntheticPhishTemplate
from phish.serializers import (
    PhishReportSerializer, SyntheticPhishSerializer,
    SyntheticPhishTemplateSerializer
)


class PhishReportViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Phish Reports to be viewed or edited.
    """
    queryset = PhishReport.objects.all().order_by('-pk')
    serializer_class = PhishReportSerializer

    def get_queryset(self):
        """
        Show nothing to unauthenticated users.
        """
        user = self.request.user
        employee = getattr(user, 'employee', None)
        if user.is_authenticated:
            if user.is_superuser:
                return super().get_queryset()
            else:
                if employee and employee.can_view_phish():
                    return PhishReport.objects.for_employee(employee)
                else:
                    return PhishReport.objects.none()
        else:
            queryset = PhishReport.objects.none()
        return queryset

    def create(self, request, *args, **kwargs):
        """
        Create a PhishReport with employee email and email message.
        """
        employee_email = request.data.get('employee_email')
        email_message = request.data.get('email_message')
        
        if not employee_email or not email_message:
            return Response(
                {'error': 'employee_email and email_message are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get employee
        try:
            employee = Employee.objects.get(user__email=employee_email)
        except Employee.DoesNotExist:
            return Response(
                {'error': 'Employee with this email does not exist'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        phish_report = PhishReport.objects.create(
            employee=employee,
            message=email_message
        )
        
        serializer = self.get_serializer(phish_report)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class SyntheticPhishTemplateViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Synthetic Phish Templates to be viewed or edited.
    """
    queryset = SyntheticPhishTemplate.objects.all().order_by('name', '-version')
    serializer_class = SyntheticPhishTemplateSerializer

    def get_queryset(self):
        """
        Show active templates to authenticated users.
        """
        user = self.request.user
        employee = getattr(user, 'employee', None)
        if user.is_authenticated:
            if user.is_superuser:
                return super().get_queryset()
            else:
                if employee and employee.can_view_phish():
                    return SyntheticPhishTemplate.objects\
                        .for_employee(employee).filter(active=True)
                else:
                    return SyntheticPhishTemplate.objects.none()
        else:
            return SyntheticPhishTemplate.objects.none()
        

class SyntheticPhishViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Synthetic Phish instances to be viewed or edited.
    """
    queryset = SyntheticPhish.objects.all().order_by('-sent_at')
    serializer_class = SyntheticPhishSerializer

    def get_queryset(self):
        """
        Show synthetic phishes related to the employee or all if superuser.
        """
        user = self.request.user
        employee = getattr(user, 'employee', None)
        if user.is_authenticated:
            if user.is_superuser:
                return super().get_queryset()
            else:
                if employee and employee.can_view_phish():
                    return SyntheticPhish.objects.for_employee(employee)
                else:
                    return SyntheticPhish.objects.none()
        else:
            return SyntheticPhish.objects.none()
    
    def create(self, request, *args, **kwargs):
        """
        Create a SyntheticPhish instance for an employee based on a template.
        """
        employee_pk = request.data.get('employee')
        template_pk = request.data.get('template')
        
        if not employee_pk or not template_pk:
            return Response(
                {'error': 'employee and template are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get employee
        try:            
            employee = Employee.objects.get(pk=employee_pk)
        except Employee.DoesNotExist:
            return Response(
                {'error': 'Employee with this ID does not exist'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get template
        try:
            template = SyntheticPhishTemplate.objects.get(pk=template_pk)
        except SyntheticPhishTemplate.DoesNotExist:
            return Response(
                {'error': 'Synthetic Phish Template with this ID does not exist'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        synthetic_phish = SyntheticPhish.objects.create(
            employee=employee,
            template=template
        )

        # Send email
        text_body = re.sub('<[^<]+?>', '', template.body)
        send_email(
            employee.user.email, template.subject, text_body, template.body
        )
        
        serializer = self.get_serializer(synthetic_phish)
        return Response(serializer.data, status=status.HTTP_201_CREATED)