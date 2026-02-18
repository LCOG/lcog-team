import re

from django.db.models import Count, F, Q, Value
from django.db.models.functions import Concat
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from mainsite.helpers import send_email
from people.models import Employee
from phish.models import (
    PhishReport, SyntheticPhish, SyntheticPhishTemplate, TrainingAssignment,
    TrainingTemplate
)
from phish.serializers import (
    PhishReportSerializer, SyntheticPhishSerializer,
    SyntheticPhishTemplateSerializer, TrainingAssignmentSerializer,
    TrainingTemplateSerializer
)


class PhishReportViewSet(viewsets.ModelViewSet):
    queryset = PhishReport.objects.all().order_by('-pk')
    serializer_class = PhishReportSerializer

    def get_queryset(self):
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


class PhishTemplateViewSet(viewsets.ModelViewSet):
    queryset = SyntheticPhishTemplate.objects.all()\
        .order_by('name', '-version')
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
        

class PhishAssignmentViewSet(viewsets.ModelViewSet):
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
                    return SyntheticPhish.objects.for_employee(employee)\
                        .order_by('-sent_at')
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
                {'error': 'Requested Synthetic Phish Template does not exist'},
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

    @action(detail=False, methods=['get'])
    def team_stats(self, request):
        """
        Fetch aggregated phishing and training stats for all team members.
        Returns employee name, phish reports, synthetic phishes,
        and training assignments.
        """
        user = self.request.user
        employee = getattr(user, 'employee', None)
        
        if not user.is_authenticated or not (
            user.is_superuser or (employee and employee.can_view_phish())
        ):
            return Response(
                {'error': 'You do not have permission to view phishing data'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get organization from current user's employee
        if user.is_superuser:
            # If superuser, get all employees
            employees_qs = Employee.objects.all()
        else:
            # Otherwise, get employees from current user's organization
            employees_qs = \
                Employee.objects.filter(organization=employee.organization)
        
        # Annotate with aggregated counts
        team_stats = employees_qs.annotate(
            name=Concat(
                F('user__first_name'), Value(' '), F('user__last_name')
            ),
            phish_reports_count=Count(
                'phishreport',
                filter=Q(phishreport__processed=False)
            ),
            synthetic_phishes_sent=Count('syntheticphish'),
            synthetic_phishes_clicked=Count(
                'syntheticphish',
                filter=Q(syntheticphish__clicked=True)
            ),
            synthetic_phishes_reported=Count(
                'syntheticphish',
                filter=Q(syntheticphish__reported=True)
            ),
            training_assigned=Count('trainingassignment'),
            training_completed=Count(
                'trainingassignment',
                filter=Q(trainingassignment__completed=True)
            )
        ).values(
            'pk', 'name', 'phish_reports_count', 'synthetic_phishes_sent',
            'synthetic_phishes_clicked', 'synthetic_phishes_reported',
            'training_assigned', 'training_completed'
        ).order_by('name')
        
        return Response(list(team_stats))


class TrainingTemplateViewSet(viewsets.ModelViewSet):
    queryset = TrainingTemplate.objects.all().order_by('name', '-version')
    serializer_class = TrainingTemplateSerializer

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
                    return TrainingTemplate.objects\
                        .for_employee(employee).filter(active=True)
                else:
                    return TrainingTemplate.objects.none()
        else:
            return TrainingTemplate.objects.none()


class TrainingAssignmentViewSet(viewsets.ModelViewSet):
    queryset = TrainingAssignment.objects.all().order_by('-assigned_at')
    serializer_class = TrainingAssignmentSerializer

    def get_queryset(self):
        user = self.request.user
        employee = getattr(user, 'employee', None)
        if user.is_authenticated:
            if user.is_superuser:
                return super().get_queryset()
            else:
                if employee and employee.can_view_phish():
                    return TrainingAssignment.objects.for_employee(employee)
                else:
                    return TrainingAssignment.objects.none()
        else:
            return TrainingAssignment.objects.none()
    
    def create(self, request, *args, **kwargs):
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
            template = TrainingTemplate.objects.get(pk=template_pk)
        except TrainingTemplate.DoesNotExist:
            return Response(
                {'error': 'Training Template with this ID does not exist'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        training_assignment = TrainingAssignment.objects.create(
            employee=employee,
            template=template
        )

        serializer = self.get_serializer(training_assignment)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def partial_update(self, request, *args, **kwargs):
        """
        Mark a training assignment as completed.
        """
        from django.utils import timezone
        
        instance = self.get_object()
        
        # Verify the current user is the assigned employee
        user = request.user
        employee = getattr(user, 'employee', None)
        
        if not employee or instance.employee != employee:
            return Response(
                {'error': 'You can only update your own training assignments'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # If marking as completed, set completed_at timestamp
        if request.data.get('completed') is True and not instance.completed:
            instance.completed = True
            instance.completed_at = timezone.now()
            instance.save()
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)