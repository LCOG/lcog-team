import re
from rest_framework.permissions import AllowAny
import traceback

from django.conf import settings
from django.contrib.sites.models import Site
from django.db.models import (
    Case, CharField, Count, F, OuterRef, Q, Subquery, Value, When
)
from django.db.models.functions import Concat
from django.shortcuts import redirect
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from mainsite.helpers import record_error, send_email
from people.models import Employee
from phish.models import (
    PhishConfiguration, PhishReport, PhishReportTask, PhishRiskProfile,
    PhishTask, SyntheticPhish, SyntheticPhishTemplate, TrainingAssignment,
    TrainingTemplate
)
from phish.serializers import (
    PhishGroupSerializer, PhishReportSerializer, PhishReportSimpleSerializer,
    PhishReportTaskSerializer, PhishRiskProfileSerializer, PhishTaskSerializer,
    SyntheticPhishSerializer, SyntheticPhishTemplateSerializer,
    TrainingAssignmentSerializer, TrainingTemplateSerializer
)


class PhishReportViewSet(viewsets.ModelViewSet):
    queryset = PhishReport.objects.all().order_by('-pk')
    serializer_class = PhishReportSerializer

    def get_serializer_class(self):
        if self.action == 'list':
            return PhishReportSimpleSerializer
        else:
            return super().get_serializer_class()

    def get_queryset(self):
        user = self.request.user

        def get_phishreport_objects():
            # For listviews, defer loading the 'message' field to improve
            # performance as they can be large and tax the server memory
            if self.action == 'list':
                return PhishReport.objects.defer('message')
            else:
                return PhishReport.objects

        # Accept optional employee prop to get phish assignments
        # for a specific employee
        employee_pk = self.request.query_params.get('employee')
        if employee_pk:
            try:
                employee = Employee.objects.get(pk=employee_pk)
                return get_phishreport_objects().for_employee(employee)\
                    .filter(employee=employee).order_by('-pk')
            except Employee.DoesNotExist:
                return get_phishreport_objects().none()

        # If no employee specified, return all phish reports user can view
        if user.is_authenticated:
            if user.is_superuser:
                return super().get_queryset()
            else:
                employee = getattr(user, 'employee', None)
                if employee and employee.can_view_secure_admin():
                    return get_phishreport_objects().for_employee(employee)
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
        
        address = None
        sender = email_message.get('sender', {})
        if sender: 
            email_address = sender.get('emailAddress')
            if email_address:
                address = email_address.get('address')
            
        phish_report = PhishReport.objects.create(
            employee=employee,
            sender=address,
            has_attachments=email_message.get('hasAttachments', False),
            message=email_message,
            additional_info=additional_info
        )
        report_url = f'{Site.objects.get_current().domain}/phish/' + \
                     f'admin/reports/{phish_report.pk}'

        # Send notification email if configured for this organization
        try:
            config = employee.organization.phish_configuration
            if config.phish_report_notification_email:
                subject = 'Phishing Report Submitted'
                body = (
                    f'{employee.name} ({employee_email}) has submitted a '
                    f'phishing report.\n\n'
                    f'Report URL: {report_url}\n'
                )
                html_body = (
                    f'<p><strong>{employee.name}</strong> '
                    f'(<a href="mailto:{employee_email}">{employee_email}</a>)'
                    f' has submitted a phishing report.</p>'
                    f'<p>Report URL: <a href="{report_url}">'
                    f'{report_url}</a></p>'
                )
                send_email(
                    config.phish_report_notification_email,
                    subject,
                    body,
                    html_body,
                )
        except PhishConfiguration.DoesNotExist:
            pass
        except Exception as e:
            record_error(
                'Error sending phishing report notification email',
                e, request, traceback.format_exc()
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
                if employee and employee.can_view_secure_admin():
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
                if employee and employee.can_view_secure_admin():
                    return SyntheticPhish.objects.for_employee(employee)\
                        .order_by('-sent_at')
                else:
                    return SyntheticPhish.objects.none()
        else:
            return SyntheticPhish.objects.none()
    
    def _get_target_employees(self, request):
        user = request.user
        current_employee = getattr(user, 'employee', None)

        if not user.is_authenticated:
            return None, Response(
                {'error': 'Authentication required'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        if not user.is_superuser and (
            not current_employee or not current_employee.can_view_secure_admin()
        ):
            return None, Response(
                {'error': 'You do not have permission to assign phish tests'},
                status=status.HTTP_403_FORBIDDEN
            )

        target_employee = request.data.get('employee')
        target_employees = request.data.get('employees')
        target_group = request.data.get('group')
        target_risk_profile = request.data.get('risk_profile')

        selectors = [
            target_employee is not None,
            isinstance(target_employees, list) and len(target_employees) > 0,
            bool(target_group),
            bool(target_risk_profile),
        ]
        if sum(selectors) != 1:
            return None, Response(
                {
                    'error': (
                        'Provide exactly one target selector: employee, '
                        'employees, group, or risk_profile'
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        organization = getattr(current_employee, 'organization', None)
        if not organization:
            return None, Response(
                {
                    'error':
                        'Current user is not associated with an organization'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        employees_qs = Employee.active_objects.filter(
            organization=organization
        )

        if target_employee is not None:
            employees_qs = employees_qs.filter(pk=target_employee)
        elif isinstance(target_employees, list) and len(target_employees) > 0:
            employees_qs = employees_qs.filter(pk__in=target_employees)
            if employees_qs.count() != len(set(target_employees)):
                return None, Response(
                    {'error': 'One or more employees do not exist'},
                    status=status.HTTP_404_NOT_FOUND
                )
        elif target_group:
            employees_qs = employees_qs.filter(
                phish_groups__name=target_group,
                phish_groups__organization=organization
            )
        else:
            employees_qs = employees_qs.filter(
                phish_risk_profiles__name=target_risk_profile,
                phish_risk_profiles__organization=organization
            )

        employees = list(employees_qs.distinct())
        if not employees:
            return None, Response(
                {'error': 'No employees found for the selected target'},
                status=status.HTTP_404_NOT_FOUND
            )

        return employees, None

    def create(self, request, *args, **kwargs):
        """
        Create one or more SyntheticPhish assignments from a template.
        """
        template_pk = request.data.get('template')

        if not template_pk:
            return Response(
                {'error': 'template is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        target_employees, error_response = self._get_target_employees(request)
        if error_response is not None:
            return error_response

        try:
            template = SyntheticPhishTemplate.objects.get(pk=template_pk)
        except SyntheticPhishTemplate.DoesNotExist:
            return Response(
                {'error': 'Requested Synthetic Phish Template does not exist'},
                status=status.HTTP_404_NOT_FOUND
            )

        current_employee = getattr(request.user, 'employee', None)
        if current_employee and (
            template.organization_id != current_employee.organization_id
        ):
            return Response(
                {'error': 'Template is not in your organization'},
                status=status.HTTP_403_FORBIDDEN
            )

        phish_link_domain = current_employee.organization.phish_configuration\
            .phish_link_domain if current_employee else None

        created_assignments = []
        for employee in target_employees:
            synthetic_phish = SyntheticPhish.objects.create(
                employee=employee,
                template=template
            )
            created_assignments.append(synthetic_phish)

            # Insert message context
            html_body = template.body\
                .replace('{{user_email}}', employee.user.email)\
                .replace('{{user_first_name}}', employee.user.first_name)\
                .replace('{{user_last_name}}', employee.user.last_name)\
                .replace('{{user_name}}', employee.name)\
                .replace('{{org_name}}', employee.organization.name)

            if phish_link_domain:
                click_url = (
                    f'{phish_link_domain}?token={synthetic_phish.click_token}'
                )
                html_body = html_body.replace(
                    '{{click_url}}', click_url
                )

            text_body = re.sub('<[^<]+?>', '', html_body)
            send_email(
                to_address=employee.user.email,
                subject=template.subject,
                body=text_body,
                html_body=html_body,
                headers={
                    'X-Synthetic-Phish-ID': str(synthetic_phish.pk),
                    'X-Synthetic-Phish-Template': template.name,
                }
            )

        if len(created_assignments) == 1:
            serializer = self.get_serializer(created_assignments[0])
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        serializer = self.get_serializer(created_assignments, many=True)
        return Response(
            {
                'created_count': len(created_assignments),
                'assignments': serializer.data,
            },
            status=status.HTTP_201_CREATED
        )

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
            user.is_superuser or 
            (employee and employee.can_view_secure_admin())
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
                Employee.active_objects.filter(
                    organization=employee.organization
                )
        
        # Annotate with aggregated counts
        # Use distinct=True to prevent duplicate counting when multiple
        # relationships are aggregated
        team_stats = employees_qs.annotate(
            name=Case(
                When(
                    Q(user__employee__display_name=None),
                    then=Concat(
                        F('user__first_name'), Value(' '), F('user__last_name')
                    )
                ),
                default=F('user__employee__display_name'),
                output_field=CharField()
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
            ),
            risk_profile_name=Subquery(
                PhishRiskProfile.objects.filter(
                    members=OuterRef('pk')
                ).order_by('order', 'pk').values('name')[:1]
            ),
            risk_profile_color=Subquery(
                PhishRiskProfile.objects.filter(
                    members=OuterRef('pk')
                ).order_by('order', 'pk').values('color')[:1]
            ),
            risk_profile_order=Subquery(
                PhishRiskProfile.objects.filter(
                    members=OuterRef('pk')
                ).order_by('order', 'pk').values('order')[:1]
            )
        ).values(
            'pk', 'name', 'phish_reports_count', 'synthetic_phishes_sent',
            'synthetic_phishes_clicked', 'synthetic_phishes_reported',
            'training_assigned', 'training_completed', 'risk_profile_name',
            'risk_profile_color', 'risk_profile_order'
        ).order_by('name')
        
        return Response(list(team_stats))

    @action(
        detail=False,
        methods=['get'],
        url_path=r'link-click/?',
        url_name='link-click',
        permission_classes=[AllowAny],
        authentication_classes=[],
    )
    def link_click(self, request):
        token = request.GET.get('token', None)
        phish = SyntheticPhish.objects.filter(click_token=token).first()
        if not phish:
            return Response(
                {'error': 'Synthetic phish not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        else:
            phish.clicked=True
            phish.clicked_at=timezone.now()
            phish.save()
            frontendUrl = settings.FRONTEND_DOMAIN if \
                hasattr(settings, 'FRONTEND_DOMAIN') else '/'
            return redirect(f'{frontendUrl}/phish-clicked?token={token}')

    @action(
        detail=False,
        methods=['get'],
        url_path=r'phish-message/?',
        url_name='phish-message',
        permission_classes=[AllowAny],
        authentication_classes=[],
    )
    def phish_message_by_token(self, request):
        token = request.GET.get('token', None)
        phish = SyntheticPhish.objects.filter(click_token=token).first()
        if not phish:
            return Response(
                {'error': 'Synthetic phish not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        else:
            message = phish.template.failure_message
            return Response({'message': message})


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
        if employee and employee.can_view_secure_admin():
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
            if not employee or not employee.can_view_secure_admin():
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
            not employee or not employee.can_view_secure_admin()
        ):
            return Response(
                {
                    'error':
                        'You do not have permission to update checklist tasks'
                },
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
                {
                    'error':
                    'Report and task must belong to the same organization'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if (
            not user.is_superuser
            and employee.organization_id != report.employee.organization_id
        ):
            return Response(
                {
                    'error':
                    'You do not have permission to update this report'
                },
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
                if employee and employee.can_view_secure_admin():
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
                if employee:
                    if employee.can_view_secure_admin():
                        return TrainingAssignment.objects\
                            .for_employee(employee)\
                            .order_by('-assigned_at')
                    elif employee.can_view_secure():
                        return TrainingAssignment.objects\
                            .for_employee(employee)\
                            .filter(employee=employee)\
                            .order_by('-assigned_at')
                else:
                    return TrainingAssignment.objects.none()
        else:
            return TrainingAssignment.objects.none()
    
    def _get_target_employees(self, request):
        user = request.user
        current_employee = getattr(user, 'employee', None)

        if not user.is_authenticated:
            return None, Response(
                {'error': 'Authentication required'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        if not user.is_superuser and (
            not current_employee or
            not current_employee.can_view_secure_admin()
        ):
            return None, Response(
                {
                    'error': (
                        'You do not have permission to assign training modules'
                    )
                },
                status=status.HTTP_403_FORBIDDEN
            )

        target_employee = request.data.get('employee')
        target_employees = request.data.get('employees')
        target_group = request.data.get('group')
        target_risk_profile = request.data.get('risk_profile')

        selectors = [
            target_employee is not None,
            isinstance(target_employees, list) and len(target_employees) > 0,
            bool(target_group),
            bool(target_risk_profile),
        ]
        if sum(selectors) != 1:
            return None, Response(
                {
                    'error': (
                        'Provide exactly one target selector: employee, '
                        'employees, group, or risk_profile'
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        organization = getattr(current_employee, 'organization', None)
        if not organization:
            return None, Response(
                {
                    'error':
                        'Current user is not associated with an organization'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        employees_qs = Employee.active_objects.filter(
            organization=organization
        )

        if target_employee is not None:
            employees_qs = employees_qs.filter(pk=target_employee)
        elif isinstance(target_employees, list) and len(target_employees) > 0:
            employees_qs = employees_qs.filter(pk__in=target_employees)
            if employees_qs.count() != len(set(target_employees)):
                return None, Response(
                    {'error': 'One or more employees do not exist'},
                    status=status.HTTP_404_NOT_FOUND
                )
        elif target_group:
            employees_qs = employees_qs.filter(
                phish_groups__name=target_group,
                phish_groups__organization=organization
            )
        else:
            employees_qs = employees_qs.filter(
                phish_risk_profiles__name=target_risk_profile,
                phish_risk_profiles__organization=organization
            )

        employees = list(employees_qs.distinct())
        if not employees:
            return None, Response(
                {'error': 'No employees found for the selected target'},
                status=status.HTTP_404_NOT_FOUND
            )

        return employees, None

    def create(self, request, *args, **kwargs):
        template_pk = request.data.get('template')

        if not template_pk:
            return Response(
                {'error': 'template is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        target_employees, error_response = self._get_target_employees(request)
        if error_response is not None:
            return error_response

        try:
            template = TrainingTemplate.objects.get(pk=template_pk)
        except TrainingTemplate.DoesNotExist:
            return Response(
                {'error': 'Training Template with this ID does not exist'},
                status=status.HTTP_404_NOT_FOUND
            )

        current_employee = getattr(request.user, 'employee', None)
        if current_employee and (
            template.organization_id != current_employee.organization_id
        ):
            return Response(
                {'error': 'Template is not in your organization'},
                status=status.HTTP_403_FORBIDDEN
            )

        created_assignments = []
        for employee in target_employees:
            created_assignments.append(
                TrainingAssignment.objects.create(
                    employee=employee,
                    template=template
                )
            )

        if len(created_assignments) == 1:
            serializer = self.get_serializer(created_assignments[0])
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        serializer = self.get_serializer(created_assignments, many=True)
        return Response(
            {
                'created_count': len(created_assignments),
                'assignments': serializer.data,
            },
            status=status.HTTP_201_CREATED
        )
    
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


class PhishDataViewSet(viewsets.ViewSet):

    def list(self, request):
        user = request.user
        employee_pk = request.query_params.get('employee')
        default_data = {'risk_profiles': [], 'groups': []}

        if not user.is_authenticated or not employee_pk:
            return Response(default_data)

        employee = getattr(user, 'employee', None)
        if not user.is_superuser and (
            not employee or not employee.can_view_secure_admin()
        ):
            return Response(default_data)

        try:
            if user.is_superuser:
                target_employee = Employee.objects.get(pk=employee_pk)
            else:
                target_employee = Employee.objects.get(
                    pk=employee_pk, organization=employee.organization
                )
        except Employee.DoesNotExist:
            return Response(default_data)

        org_risk_profiles = \
            target_employee.organization.phish_risk_profiles.all()
        org_groups = target_employee.organization.phish_groups.all()
        risk_profiles = target_employee.phish_risk_profiles.all()
        groups = target_employee.phish_groups.all()

        # Should return employee.phish_risk_profiles and employee.phish_groups
        data = {
            'org_risk_profiles':
                PhishRiskProfileSerializer(org_risk_profiles, many=True).data,
            'org_groups': PhishGroupSerializer(org_groups, many=True).data,
            'risk_profiles':
                PhishRiskProfileSerializer(risk_profiles, many=True).data,
            'groups': PhishGroupSerializer(groups, many=True).data
        }
        
        return Response(data)

    @action(detail=False, methods=['get'], url_path='assignment-targets')
    def assignment_targets(self, request):
        user = request.user
        employee = getattr(user, 'employee', None)

        if not user.is_authenticated:
            return Response(
                {'error': 'Authentication required'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        if not user.is_superuser and (
            not employee or not employee.can_view_secure_admin()
        ):
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )

        organization = getattr(employee, 'organization', None)
        if not organization:
            return Response(
                {
                    'error':
                        'Current user is not associated with an organization'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        org_risk_profiles = organization.phish_risk_profiles.order_by(
            'order', 'name'
        )
        org_groups = organization.phish_groups.order_by('order', 'name')

        return Response(
            {
                'org_risk_profiles': PhishRiskProfileSerializer(
                    org_risk_profiles, many=True
                ).data,
                'org_groups': PhishGroupSerializer(org_groups, many=True).data,
            }
        )

    @action(detail=True, methods=['patch'], url_path='update-risk-level')
    def update_risk_level(self, request, pk=None):
        user = request.user
        if not user.is_authenticated:
            return Response(
                {'error': 'Authentication required'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        employee = getattr(user, 'employee', None)
        if not user.is_superuser and (
            not employee or not employee.can_view_secure_admin()
        ):
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            target_employee = Employee.objects.get(
                pk=pk, organization=employee.organization
            )
        except Employee.DoesNotExist:
            return Response(
                {'error': 'Employee not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        new_risk_level = request.data.get('risk_level')

        organization_risk_levels = \
            target_employee.organization.phish_risk_profiles.values_list(
                'name', flat=True
            )
        if new_risk_level not in organization_risk_levels:
            return Response(
                {'error': 'Invalid risk level'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Remove employee from all current risk profiles and add to the new one
        target_employee.phish_risk_profiles.clear()
        target_employee.phish_risk_profiles.add(
            target_employee.organization.phish_risk_profiles.get(
                name=new_risk_level
            )
        )

        return Response({
            'message': 'Risk level updated successfully',
            'risk_level': new_risk_level
        })

    @action(detail=True, methods=['patch'], url_path='update-groups')
    def update_groups(self, request, pk=None):
        user = request.user
        if not user.is_authenticated:
            return Response(
                {'error': 'Authentication required'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        employee = getattr(user, 'employee', None)
        if not user.is_superuser and (
            not employee or not employee.can_view_secure_admin()
        ):
            return Response(
                {'error': 'Permission denied'},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            target_employee = Employee.objects.get(
                pk=pk, organization=employee.organization
            )
        except Employee.DoesNotExist:
            return Response(
                {'error': 'Employee not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        new_groups = request.data.get('groups', [])

        # Validate that the provided groups exist in the organization
        valid_groups = target_employee.organization.phish_groups.filter(
            name__in=new_groups
        )
        if valid_groups.count() != len(new_groups):
            return Response(
                {'error': 'One or more groups are invalid'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Clear existing groups and add the new ones
        target_employee.phish_groups.set(valid_groups)

        return Response({
            'message': 'Groups updated successfully',
            'groups': [g.name for g in valid_groups]
        })