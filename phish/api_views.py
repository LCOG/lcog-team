import re
import traceback

from django.db.models import Count, F, Q, Value
from django.db.models.functions import Concat
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from mainsite.helpers import record_error, send_email
from people.models import Employee
from phish.models import (
    PhishConfiguration, PhishReport, PhishReportTask, PhishTask,
    SyntheticPhish, SyntheticPhishTemplate, TrainingAssignment, TrainingTemplate
)
from phish.serializers import (
    PhishReportSerializer, PhishReportTaskSerializer, PhishTaskSerializer,
    SyntheticPhishSerializer, SyntheticPhishTemplateSerializer,
    TrainingAssignmentSerializer, TrainingTemplateSerializer
)


class PhishReportViewSet(viewsets.ModelViewSet):
    queryset = PhishReport.objects.all().order_by('-pk')
    serializer_class = PhishReportSerializer

    def get_queryset(self):
        user = self.request.user

        # Accept optional employee prop to get phish assignments
        # for a specific employee
        employee_pk = self.request.query_params.get('employee')
        if employee_pk:
            try:
                employee = Employee.objects.get(pk=employee_pk)
                return PhishReport.objects.for_employee(employee)\
                    .filter(employee=employee).order_by('-pk')
            except Employee.DoesNotExist:
                return PhishReport.objects.none()

        # If no employee specified, return all phish reports user can view
        if user.is_authenticated:
            if user.is_superuser:
                return super().get_queryset()
            else:
                employee = getattr(user, 'employee', None)
                if employee and employee.can_view_phish():
                    return PhishReport.objects.for_employee(employee)
                else:
                    return PhishReport.objects.none()
        else:
            queryset = PhishReport.objects.none()
        return queryset

    def create(self, request, *args, **kwargs):
        """
        Process a phishing email report.
        If the email contains X-Synthetic-Phish-ID header, mark that
        synthetic phish as reported (don't create a PhishReport).
        Otherwise, create a PhishReport for a genuine phishing attempt.
        """

        employee_email = request.data.get('employee_email')
        email_message = request.data.get('email_message')
        additional_info = request.data.get('additional_info')
        
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
        
        # Check if this report corresponds to a synthetic phish
        # Look for X-Synthetic-Phish-ID in the email message headers
        synthetic_phish_id = None
        if isinstance(email_message, dict):
            # If message is already parsed as dict with headers
            headers = email_message.get('internetMessageHeaders', {})
            # Convert list of headers to dict for easier lookup
            headers = {h['name']: h['value'] for h in headers if 'name' in h \
                       and 'value' in h}
            synthetic_phish_id = headers.get('X-Synthetic-Phish-ID')
        elif isinstance(email_message, str):
            # Try to extract header from raw email string
            match = re.search(
                r'X-Synthetic-Phish-ID:\s*(\d+)',
                email_message,
                re.IGNORECASE
            )
            if match:
                synthetic_phish_id = match.group(1)
        
        # If we found a synthetic phish ID, mark it as reported
        # and don't create a PhishReport (this is an expected test report)
        if synthetic_phish_id:
            try:
                synthetic_phish = SyntheticPhish.objects.get(
                    pk=int(synthetic_phish_id),
                    employee=employee
                )
                if not synthetic_phish.reported:
                    synthetic_phish.reported = True
                    synthetic_phish.reported_at = timezone.now()
                    synthetic_phish.save()
                
                # Return success without creating a PhishReport
                return Response(
                    {
                        'message': 'Synthetic phish correctly reported',
                        'synthetic_phish_id': synthetic_phish.pk
                    },
                    status=status.HTTP_200_OK
                )
            except (SyntheticPhish.DoesNotExist, ValueError):
                # If synthetic phish not found or invalid ID, treat as organic
                pass
        
        # No synthetic phish found - create a PhishReport and send email for
        # organic reports
        phish_report = PhishReport.objects.create(
            employee=employee,
            message=email_message,
            additional_info=additional_info
        )

        # Send notification email if configured for this organization
        try:
            config = employee.organization.phish_configuration
            record_error(f'PHISH_REPORT_TEST: {employee_email} - {phish_report.pk} - {config} - {config.phish_report_notification_email}', None, None, None)
            if config.phish_report_notification_email:
                record_error(f'PHISH_REPORT_TEST: 1', None, None, None)
                reporter_name = (
                    f'{employee.first_name} {employee.last_name}'
                ).strip() or employee_email
                record_error(f'PHISH_REPORT_TEST: {reporter_name}', None, None, None)
                subject = 'Phishing Report Submitted'
                body = (
                    f'{reporter_name} ({employee_email}) has submitted a '
                    f'phishing report.\n\n'
                    f'Report ID: {phish_report.pk}\n'
                )
                html_body = (
                    f'<p><strong>{reporter_name}</strong> '
                    f'(<a href="mailto:{employee_email}">{employee_email}</a>)'
                    f' has submitted a phishing report.</p>'
                    f'<p><a href="/phish/admin/reports/{phish_report.pk}/">'
                    f'Report ID: {phish_report.pk}</a></p>'
                )
                record_error(f'PHISH_REPORT_TEST: 2', None, None, None)
                send_email(
                    config.phish_report_notification_email,
                    subject,
                    body,
                    html_body,
                )
                record_error(f'PHISH_REPORT_TEST: 3', None, None, None)
        except PhishConfiguration.DoesNotExist:
            pass
        except Exception as e:
            record_error('Error sending phishing report notification email', e, request, traceback.format_exc())

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
        
        # Accept optional employee prop to get phish assignments
        # for a specific employee
        employee_pk = self.request.query_params.get('employee')
        if employee_pk:
            try:
                employee = Employee.objects.get(pk=employee_pk)
                return SyntheticPhish.objects.for_employee(employee)\
                    .filter(employee=employee).order_by('-sent_at')
            except Employee.DoesNotExist:
                return SyntheticPhish.objects.none()
        
        # If no employee specified, return all phish assignments user can view
        if user.is_authenticated:
            if user.is_superuser:
                return super().get_queryset()
            else:
                employee = getattr(user, 'employee', None)
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

        # Send email with custom header containing synthetic phish ID
        text_body = re.sub('<[^<]+?>', '', template.body)
        send_email(
            to_address=employee.user.email,
            subject=template.subject,
            body=text_body,
            html_body=template.body,
            headers={
                'X-Synthetic-Phish-ID': str(synthetic_phish.pk),
                'X-Synthetic-Phish-Template': template.name,
            }
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
        # Use distinct=True to prevent duplicate counting when multiple
        # relationships are aggregated
        team_stats = employees_qs.annotate(
            name=Concat(
                F('user__first_name'), Value(' '), F('user__last_name')
            ),
            phish_reports_count=Count('phishreport', distinct=True),
            synthetic_phishes_sent=Count('syntheticphish', distinct=True),
            synthetic_phishes_clicked=Count(
                'syntheticphish',
                filter=Q(syntheticphish__clicked=True),
                distinct=True
            ),
            synthetic_phishes_reported=Count(
                'syntheticphish',
                filter=Q(syntheticphish__reported=True),
                distinct=True
            ),
            training_assigned=Count('trainingassignment', distinct=True),
            training_completed=Count(
                'trainingassignment',
                filter=Q(trainingassignment__completed=True),
                distinct=True
            )
        ).values(
            'pk', 'name', 'phish_reports_count', 'synthetic_phishes_sent',
            'synthetic_phishes_clicked', 'synthetic_phishes_reported',
            'training_assigned', 'training_completed'
        ).order_by('name')
        
        return Response(list(team_stats))


class PhishTaskViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PhishTask.objects.all().order_by('order', 'name')
    serializer_class = PhishTaskSerializer

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return PhishTask.objects.none()
        if user.is_superuser:
            return super().get_queryset()

        employee = getattr(user, 'employee', None)
        if employee and employee.can_view_phish():
            return PhishTask.objects.filter(
                organization=employee.organization
            ).order_by('order', 'name')
        return PhishTask.objects.none()


class PhishReportTaskViewSet(viewsets.ModelViewSet):
    queryset = PhishReportTask.objects.all().order_by('-completed_at')
    serializer_class = PhishReportTaskSerializer
    http_method_names = ['get', 'post', 'delete', 'head', 'options']

    def get_queryset(self):
        user = self.request.user
        report_pk = self.request.query_params.get('report')

        if not user.is_authenticated:
            return PhishReportTask.objects.none()

        if user.is_superuser:
            queryset = super().get_queryset()
        else:
            employee = getattr(user, 'employee', None)
            if not employee or not employee.can_view_phish():
                return PhishReportTask.objects.none()
            queryset = PhishReportTask.objects.filter(
                report__employee__organization=employee.organization
            ).order_by('-completed_at')

        if report_pk:
            queryset = queryset.filter(report_id=report_pk)
        return queryset

    def create(self, request, *args, **kwargs):
        report_pk = request.data.get('report')
        task_pk = request.data.get('task')
        user = request.user
        employee = getattr(user, 'employee', None)

        if not report_pk or not task_pk:
            return Response(
                {'error': 'report and task are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if not user.is_superuser and (
            not employee or not employee.can_view_phish()
        ):
            return Response(
                {'error': 'You do not have permission to update checklist tasks'},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            report = PhishReport.objects.get(pk=report_pk)
            task = PhishTask.objects.get(pk=task_pk)
        except (PhishReport.DoesNotExist, PhishTask.DoesNotExist):
            return Response(
                {'error': 'Report or task not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        if report.employee.organization_id != task.organization_id:
            return Response(
                {'error': 'Report and task must belong to the same organization'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if (
            not user.is_superuser
            and employee.organization_id != report.employee.organization_id
        ):
            return Response(
                {'error': 'You do not have permission to update this report'},
                status=status.HTTP_403_FORBIDDEN
            )

        report_task, _ = PhishReportTask.objects.get_or_create(
            report=report,
            task=task,
            defaults={'completed_by': employee if employee else None}
        )

        if not report_task.completed_by and employee:
            report_task.completed_by = employee
            report_task.save(update_fields=['completed_by'])

        serializer = self.get_serializer(report_task)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


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

        # Accept optional employee prop to get training assignments
        # for a specific employee
        employee_pk = self.request.query_params.get('employee')
        if employee_pk:
            try:
                employee = Employee.objects.get(pk=employee_pk)
                return TrainingAssignment.objects.for_employee(employee)\
                    .filter(employee=employee).order_by('-assigned_at')
            except Employee.DoesNotExist:
                return TrainingAssignment.objects.none()

        # If no employee specified, return all assignments user can view
        if user.is_authenticated:
            if user.is_superuser:
                return super().get_queryset()
            else:
                employee = getattr(user, 'employee', None)
                if employee and employee.can_view_phish():
                    return TrainingAssignment.objects.for_employee(employee)\
                        .order_by('-assigned_at')
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