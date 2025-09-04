from datetime import timedelta

from django.apps import apps
from django.contrib.auth.models import Group, User
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils import timezone

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import RetrieveAPIView
from rest_framework.permissions import BasePermission, SAFE_METHODS
from rest_framework.response import Response

from mainsite.api_views import LargeResultsSetPagination
from mainsite.models import SecurityMessage
from mainsite.helpers import (
    is_true_string, send_completed_email_to_hr_manager,
    send_evaluation_written_email_to_employee,
    send_signature_email_to_executive_director,
    send_signature_email_to_hr_manager, send_signature_email_to_manager
)
from mainsite.serializers import FileUploadSerializer
from people.models import (
    Employee, JobTitle, PerformanceReview, ReviewNote, Signature,
    TeleworkApplication, TeleworkSignature, UnitOrProgram,
    ViewedSecurityMessage, WorkflowOptions
)
from people.serializers import (
    EmployeeSerializer, EmployeeEmailSerializer, GroupSerializer,
    JobTitleSerializer, PerformanceReviewSerializer,
    PerformanceReviewSimpleSerializer, ReviewNoteSerializer,
    SignatureSerializer, SimpleEmployeeSerializer,
    TeleworkApplicationFileUploadSerializer, TeleworkApplicationSerializer,
    TeleworkSignatureSerializer, UnitSerializer, UserSerializer,
    ViewedSecurityMessageSerializer
)


class IsAdminOrReadOnly(BasePermission):
    """
    The request is an authenticated admin user, or is a read-only request.
    """

    def has_permission(self, request, view):
        import pdb; pdb.set_trace()
        return bool(
            request.method in SAFE_METHODS or
            request.user and
            request.user.is_staff
        )


class IsAdmin(BasePermission):
    """
    The request is an authenticated admin user
    """

    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_staff
        )


class JobTitleViewSet(viewsets.ModelViewSet):
    queryset = JobTitle.active_objects.all()
    serializer_class = JobTitleSerializer
    pagination_class = LargeResultsSetPagination

    def get_queryset(self):
        """
        Show nothing to unauthenticated users.
        """
        user = self.request.user
        if user.is_authenticated:
            queryset = JobTitle.active_objects.all()
        else:
            queryset = JobTitle.objects.none()
        return queryset


class UnitViewSet(viewsets.ModelViewSet):
    queryset = UnitOrProgram.objects.all()
    serializer_class = UnitSerializer

    def get_queryset(self):
        """
        Show nothing to unauthenticated users.
        """
        user = self.request.user
        if user.is_authenticated:
            queryset = UnitOrProgram.objects.all()
        else:
            queryset = UnitOrProgram.objects.none()
        return queryset


class CurrentUserView(RetrieveAPIView):
    serializer_class = EmployeeSerializer
    queryset = Employee.objects.all()

    def get_object(self):
        return getattr(self.request.user, 'employee', None)


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [IsAdmin]


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [IsAdmin]


class EmployeeViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer

    def get_queryset(self):
        """
        Return a list of all employees to admins. Filter by direct reports for
        everyone else.
        """
        user = self.request.user
        if user.is_authenticated:
            if user.is_staff:
                queryset = Employee.objects.all()
            else:
                # Filter to just direct reports, or else them and all their
                # descendants
                direct_reports = self.request.query_params.get(
                    'direct-reports', None
                )
                if direct_reports is not None and direct_reports == "True":
                    queryset = Employee.objects.filter(manager__user=user)
                else:
                    queryset = user.employee.get_direct_reports_descendants(
                        include_self=True
                    )
        else:
            queryset = Employee.objects.none()
        return queryset
    
    def partial_update(self, request, pk=None):
        """
        Updates the employee's display name and other preferences.
        """
        employee = Employee.objects.get(pk=pk)
        employee.display_name = request.data['display_name']
        employee.email_opt_out_all = request.data['email_opt_out_all']
        employee.email_opt_out_timeoff_all = request.data[
            'email_opt_out_timeoff_all'
        ]
        employee.email_opt_out_timeoff_weekly = request.data[
            'email_opt_out_timeoff_weekly'
        ]
        employee.email_opt_out_timeoff_daily = request.data[
            'email_opt_out_timeoff_daily'
        ]
        employee.email_opt_out_workflows_all = request.data[
            'email_opt_out_workflows_all'
        ]
        employee.email_opt_out_workflows_transitions = request.data[
            'email_opt_out_workflows_transitions'
        ]
        employee.email_opt_out_workflows_processes = request.data[
            'email_opt_out_workflows_processes'
        ]
        employee.email_opt_out_expenses_all = request.data[
            'email_opt_out_expenses_all'
        ]
        # Just set workflow options
        new_wfos = request.data['workflow_display_options']
        # All previously set workflow options
        curr_wfos = WorkflowOptions.objects.filter(employee=employee)
        # Get all the relevant workflows just once
        workflows = apps.get_model('workflows.Workflow').objects\
            .filter(name__in=map(lambda x: x['name'], new_wfos))
        # Update or create workflow options for the employee
        for idx, option in enumerate(new_wfos):
            try:
                wfo = curr_wfos.get(
                    workflow=workflows.get(name=option['name'])
                )
                wfo.display = option['display']
                wfo.order = idx+1
                wfo.save()
            except WorkflowOptions.DoesNotExist:
                wfo = WorkflowOptions.objects.create(
                    employee=employee,
                    workflow=workflows.get(name=option['name']),
                    display=option['display'],
                    order=idx+1
                )
        employee.save()
        serialized_employee = EmployeeSerializer(employee,
             context={'request': request})
        return Response(serialized_employee.data)

    @action(detail=True, methods=['get'])
    def employee_next_performance_review(self, request, pk=None):
        next_review = request.user.employee.employee_next_review()
        serialized_review = PerformanceReviewSerializer(next_review,
            context={'request': request})
        return Response(serialized_review.data)
    
    # A simple list of employees for populating dropdowns
    @action(detail=False, methods=['get'])
    def simple_list(self, request):
        employees = self.get_queryset()
        serializer = SimpleEmployeeSerializer(employees, many=True)
        return Response(serializer.data)

    # A simple list of a user's direct reports
    @action(detail=True, methods=['get'])
    def direct_reports(self, request, pk):
        employees = self.get_queryset().filter(manager__pk=pk)
        serializer = SimpleEmployeeSerializer(employees, many=True)
        return Response(serializer.data)

    # A simple list of employee emails for populating dropdowns
    @action(detail=False, methods=['get'])
    def email_list(self, request):
        employees = self.get_queryset()
        serializer = EmployeeEmailSerializer(employees, many=True)
        return Response(serializer.data)
    
    # Retrieve the name of an employee from pk
    @action(detail=True, methods=['get'])
    def simple_detail(self, request, pk):
        employee = self.get_queryset().filter(pk=pk)
        if not employee:
            return Response(status=status.HTTP_404_NOT_FOUND)
        else:
            serializer = SimpleEmployeeSerializer(employee[0], many=False)
            return Response(serializer.data)


class PerformanceReviewPermission(BasePermission):
    """
    Manager or employee may update the Performance Review.
    Others may read only.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.user.is_staff:
            return True
        else:
            if request.method in SAFE_METHODS:
                return True
            # Write permissions are only allowed to the owners of the PR.
            return request.user in [
                obj.employee.manager.user, obj.employee.user
            ]


class PerformanceReviewViewSet(viewsets.ModelViewSet):
    queryset = PerformanceReview.objects.all()
    permission_classes = [PerformanceReviewPermission]

    def get_serializer_class(self):
        if self.action == 'list':
            return PerformanceReviewSimpleSerializer
        return PerformanceReviewSerializer

    def get_queryset(self):
        """
        Return a list of all performance reviews to admins. Filter by direct
        reports for everyone else.
        """
        user = self.request.user
        if user.is_authenticated:
            if user.is_superuser:
                queryset = PerformanceReview.objects.all()\
                    .order_by('period_end_date')
            else:
                employee = self.request.query_params.get('employee', None)
                manager = self.request.query_params.get('manager', None)
                if employee is not None:
                    # All PRs for a given employee
                    employee = Employee.objects.get(pk=int(employee))
                    queryset = PerformanceReview.objects\
                        .for_employee(employee).filter(employee=employee)
                elif manager is not None:
                    employee = user.employee
                    is_ed = employee.is_executive_director if employee else False
                    is_hrm = employee.is_hr_manager if employee else False
                    if is_ed or is_hrm:
                        # Superusers, EDs, and HR managers can see all reviews
                        queryset = PerformanceReview.objects\
                            .for_employee(employee).order_by('period_end_date')
                    else:
                        # All PRs managed by a given employee.
                        # TODO: We used to also include descendants, but that
                        # caused weird recursion issues and long load times for
                        # people like Stephanie. Restore descendant employees?
                        manager_employee = Employee.objects.get(
                            pk=int(manager)
                        )
                        # descendant_employees = manager_employee.\
                        #     get_direct_reports_descendants(include_self=False)
                        employees = manager_employee.get_direct_reports()
                        queryset = PerformanceReview.objects\
                            .for_employee(employee)\
                            .filter(employee__in=employees)
                else:
                    # All PRs for the current user and their direct reports
                    employees = user.employee.get_direct_reports(
                        include_self=True
                    )
                    queryset = PerformanceReview.objects.filter(
                        employee__in=employees
                    )
                
                # Filter to either complete or incomplete reviews
                complete = self.request.query_params.get('complete', None)
                incomplete = self.request.query_params.get('incomplete', None)
                if is_true_string(complete):
                    queryset = queryset.filter(
                        status=PerformanceReview.EVALUATION_ED_APPROVED
                    )
                elif is_true_string(incomplete):
                    queryset = queryset.exclude(
                        status=PerformanceReview.EVALUATION_ED_APPROVED
                    ).exclude(period_end_date__gte=\
                              timezone.now() + timedelta(days=60))
        else:
            queryset = PerformanceReview.objects.none()
        return queryset

    def retrieve(self, request, pk=None):
        user = self.request.user
        queryset = self.get_queryset()
        pr = get_object_or_404(queryset, pk=pk)

        if user.is_superuser:
            # Superusers can see all reviews
            pass
        else:
            employee = user.employee if user.is_authenticated else None
            if employee is None:
                # If the user is not an employee, return 403
                return Response(status=403)
            else:
                if any([
                    employee.is_hr_employee,
                    employee.is_hr_manager,
                    employee.is_division_director,
                    employee.is_executive_director
                ]):
                    # HR and directors can see all reviews
                    pass
                else:
                    # Check if the user is the employee or manager of the PR
                    self_and_descendants = \
                        employee.get_direct_reports_descendants(
                            include_self=True
                        )
                    if pr.employee not in self_and_descendants:
                        return Response(status=403)

        serializer = PerformanceReviewSerializer(pr,
            context={'request': request})
        return Response(serializer.data)

    def update(self, request, pk=None):
        pr = PerformanceReview.objects.get(pk=pk)
        pr.evaluation_type = request.data['evaluation_type']
        pr.probationary_evaluation_type = \
            request.data['probationary_evaluation_type']
        pr.step_increase = request.data['step_increase']
        pr.top_step_bonus = request.data['top_step_bonus']
        pr.action_other = request.data['action_other']
        pr.data = request.data['data']
        pr.evaluation_comments_employee = \
            request.data['evaluation_comments_employee']
        if pr.status == PerformanceReview.NEEDS_EVALUATION and all([
            (pr.evaluation_type == 'A' or
                (pr.evaluation_type == 'P' and
                    pr.probationary_evaluation_type != None
                )
            ),
            pr.step_increase != None,
            pr.top_step_bonus != None,
            # Make sure all factors are filled out
            all(pr.data.get(factor) is not None for factor in pr.form.factors.values_list('name', flat=True)),
            # Make sure all long responses are filled out
            all(pr.data.get(long_response[0]) is not None for long_response in pr.form.long_responses),
            # TODO: Add this back once uploader done
            # pr.signed_position_description.name != ''
        ]):
            pr.status = PerformanceReview.EVALUATION_WRITTEN
            send_evaluation_written_email_to_employee(pr.employee, pr)
        pr.save()
        serialized_review = PerformanceReviewSerializer(pr,
            context={'request': request})
        return Response(serialized_review.data)
    
    def partial_update(self, request, pk=None):
        """
        Currently just updates the employee's comments. This might need to be
        more general to accept any partial updates.
        """
        pr = PerformanceReview.objects.get(pk=pk)
        pr.evaluation_comments_employee = \
            request.data['evaluation_comments_employee']
        pr.save()
        serialized_review = PerformanceReviewSerializer(pr,
            context={'request': request})
        return Response(serialized_review.data)


class TeleworkApplicationFileUploadViewSet(viewsets.ModelViewSet):
    queryset = TeleworkApplication.objects.all()
    serializer_class = FileUploadSerializer
    # permission_classes = [IsAuthenticated]

    def list(self, request):
        user = self.request.user
        if user.is_authenticated:
            if user.is_staff:
                queryset = TeleworkApplication.objects.all()
            else:
                queryset = TeleworkApplication.objects.filter(
                    Q(employee__manager__user=user) |
                    Q(employee__user=user)
                )
        else:
            queryset = TeleworkApplication.objects.none()
        serializer = TeleworkApplicationFileUploadSerializer(
            queryset, many=True, context={'request': request}
        )
        return Response(serializer.data)
    
    def retrieve(self, request, pk=None):
        user = self.request.user
        if user.is_authenticated:
            if user.is_staff:
                queryset = TeleworkApplication.objects.all()
            else:
                queryset = TeleworkApplication.objects.filter(
                    Q(employee__manager__user=user) |
                    Q(employee__user=user)
                )
        else:
            queryset = TeleworkApplication.objects.none()
        application = get_object_or_404(queryset, pk=pk)
        serializer = TeleworkApplicationFileUploadSerializer(
            application, context={'request': request}
        )
        return Response(serializer.data)
    
    def create(self, request):
        file_upload = request.FILES.get('file')
        if not file_upload:
            return Response(data="Missing file", status=400)
        application_pk = request.data.get('pk')
        if not application_pk:
            return Response(data="Missing application PK", status=400)
        try:
            application = TeleworkApplication.objects.get(pk=application_pk)
        except TeleworkApplication.DoesNotExist:
            return Response(data="Invalid application PK", status=400)
        application.dependent_care_documentation = file_upload
        application.save()
        return Response(
            data=request.build_absolute_uri(
                application.dependent_care_documentation.url
            ),
            status=200
        )


class SignatureViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows signatures to be created.
    """
    queryset = Signature.objects.all()
    serializer_class = SignatureSerializer
    # permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        This view should return a list of all signatures made by this user.
        """
        user = self.request.user
        if user.is_authenticated:
            # TODO: Don't do this.
            # TODO: There is an issue where the detail view doesn't have the user
            if user.is_anonymous:
                return Signature.objects.all()
            else:
                return Signature.objects.filter(employee__user=user)
        else:
            return Signature.objects.none()
    
    def create(self, request):
        pr = PerformanceReview.objects.get(pk=request.data['review_pk'])
        employee = Employee.objects.get(pk=request.data['employee_pk'])
        new_signature = Signature.objects.create(review=pr, employee=employee)
        
        def send_to_next_manager(employee):
            if employee.is_division_director:
                # Send notification to next manager in the chain (HR manager)
                send_signature_email_to_hr_manager(pr)
            else:
                send_signature_email_to_manager(employee.manager, pr)

        # Send notification to next manager in the chain
        if pr.status == PerformanceReview.EVALUATION_WRITTEN:
            pr_employee_has_signed = Signature.objects.filter(
                review=pr, employee=pr.employee
            ).count()
            pr_manager_has_signed = Signature.objects.filter(
                review=pr, employee=pr.employee.manager
            ).count()
            if pr_employee_has_signed and pr_manager_has_signed:
                # If the PR manager is the division director, mark as approved
                # now that both manager and employee have signed
                if (
                    pr.employee.manager.is_division_director or \
                        employee.is_division_director
                ):
                    pr.status = PerformanceReview.EVALUATION_APPROVED
                    pr.save()
                if pr.employee.manager.is_hr_manager or employee.is_hr_manager:
                    pr.status = PerformanceReview.EVALUATION_HR_PROCESSED
                    pr.save()
                if employee == pr.employee:
                    send_to_next_manager(employee.manager)
                else:
                    send_to_next_manager(employee)
        elif pr.status == PerformanceReview.EVALUATION_APPROVED:
            if employee.is_hr_manager:
                pr.status = PerformanceReview.EVALUATION_HR_PROCESSED
                pr.save()
                # Send notification to next manager in the chain
                # (executive director)
                send_signature_email_to_executive_director(pr)
        elif pr.status == PerformanceReview.EVALUATION_HR_PROCESSED:
            if employee.is_executive_director:
                pr.status = PerformanceReview.EVALUATION_ED_APPROVED
                pr.save()
                # Send notification to HR manager
                send_completed_email_to_hr_manager(pr)
                # Create new Performance Review for employee
                # NOTE: We don't currently do this, but just wait for the
                # next review export from Caselle
                # pr.create_next_review_for_employee()
        
        serialized_signature = SignatureSerializer(new_signature,
            context={'request': request})
        return Response(serialized_signature.data)


class ReviewNoteViewSet(viewsets.ModelViewSet):
    queryset = ReviewNote.objects.all()
    serializer_class = ReviewNoteSerializer
    # permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        This view should return a list of all review notes written by this
        user.
        """
        user = self.request.user
        # TODO: Don't do this.
        # There is an issue where the detail view doesn't have the user
        if user.is_authenticated:
            if user.is_superuser:
                return ReviewNote.objects.all()
            elif user.is_anonymous:
                return ReviewNote.objects.all()
            else:
                return ReviewNote.objects.filter(author__user=user)
        else:
            return ReviewNote.objects.none()

    def create(self, request):
        employee = Employee.objects.get(pk=request.data['employee_pk'])
        author = request.user.employee  
        note = request.data['note']
        new_review_note = ReviewNote.objects.create(author=author,
            employee=employee, note=note)
        serialized_note = ReviewNoteSerializer(new_review_note,
            context={'request': request})
        return Response(serialized_note.data)
    
    def update(self, request, pk=None):
        employee = Employee.objects.get(pk=request.data['employee_pk'])
        review_note = ReviewNote.objects.get(pk=pk)
        review_note.employee = employee
        review_note.note = request.data['note']
        review_note.save()
        serialized_note = ReviewNoteSerializer(review_note,
            context={'request': request})
        return Response(serialized_note.data)
      
    # TODO: Detail false?
    @action(detail=True, methods=['get'])
    def notes_for_employee(self, request, pk=None):
        six_months_ago = timezone.now() - timedelta(days=180)
        review_notes = self.get_queryset().filter(
            employee=pk, created_at__gte=six_months_ago
        )
        serialized_notes = [ReviewNoteSerializer(note,
            context={'request': request}).data for note in review_notes]
        return Response(serialized_notes)


class ViewedSecurityMessageViewSet(viewsets.ModelViewSet):
    """
    API endpoint to mark Security Messages as viewed
    """
    queryset = ViewedSecurityMessage.objects.all()
    serializer_class = ViewedSecurityMessageSerializer
    # permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        This view should return a list of all viewed security messages for
        which the currently authenticated user is the employee.
        """
        user = self.request.user
        if user.is_authenticated:
            if user.is_staff:
                queryset = ViewedSecurityMessage.objects.all()
            else:
                queryset = ViewedSecurityMessage.objects.filter(
                    employee__user=user)
        else:
            queryset = ViewedSecurityMessage.objects.none()
        return queryset

    @action(detail=False)
    def employee_viewed_latest_security_message(self, request):
        if not SecurityMessage.objects.count():
            return Response(False)
        latest_security_message = SecurityMessage.objects.filter(
            active=True
        ).latest()
        viewed_security_message = ViewedSecurityMessage.objects.filter(
            employee=request.user.employee,
            security_message=latest_security_message
        )
        if viewed_security_message.count():
            return Response(True)
        else:
            return Response(False)
    
    @action(detail=True, methods=['get'])
    def employee_viewed_security_message(self, request, pk=None):
        viewed_security_message = ViewedSecurityMessage.objects.filter(
            employee=request.user.employee,
            security_message=pk
        )
        if viewed_security_message.count():
            return Response(True)
        else:
            return Response(False)

    def create(self, request):
        security_message = SecurityMessage.objects.latest()
        employee = Employee.objects.get(pk=request.data['employee_pk'])
        viewed_security_message = ViewedSecurityMessage.objects.create(
            security_message=security_message, employee=employee
        )
        
        serialized_object = ViewedSecurityMessageSerializer(
            viewed_security_message, context={'request': request}
        )
        return Response(serialized_object.data)


class TeleworkApplicationPermission(BasePermission):
    """
    Manager or employee may update the Telework Application until it is
    approved. Others may read only.
    """

    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.user.is_staff:
            return True
        else:
            if request.method in SAFE_METHODS:
                return True
            # Write permissions are only allowed to the owners of the PR.
            return request.user in [
                obj.employee.manager.user, obj.employee.user
            ]


class TeleworkApplicationViewSet(viewsets.ModelViewSet):
    queryset = TeleworkApplication.objects.all()
    serializer_class = TeleworkApplicationSerializer
    permission_classes = [TeleworkApplicationPermission]

    def get_queryset(self):
        """
        This view should return a list of all telework applications for which
        the currently authenticated user is the manager.
        """
        user = self.request.user
        if user.is_authenticated:
            if user.is_staff:
                queryset = TeleworkApplication.objects.all()
            else:
                manager_prs = TeleworkApplication.objects.filter(
                    employee__manager__user=user)
                employee_prs = TeleworkApplication.objects.filter(
                    employee__user=user)
                queryset = manager_prs | employee_prs # Default queryset
                if hasattr(user, 'employee'):
                    signature = self.request.query_params.get(
                        'signature', None
                    )
                    if signature is not None:
                        if is_true_string(signature):
                            queryset = TeleworkApplication\
                                .applications_signature_required\
                                .get_queryset(user)
                        else:
                            queryset = TeleworkApplication\
                                .applications_signature_not_required\
                                .get_queryset(user)
                    else:
                        # Use default queryset
                        pass
                else:
                    # Use default queryset
                    pass
        else:
            queryset = TeleworkApplication.objects.none()
        return queryset

    def retrieve(self, request, pk=None):
        by_employee = request.query_params.get('by_employee', None)
        if is_true_string(by_employee):
            try:
                application = TeleworkApplication.objects.get(employee__pk=pk)
            except TeleworkApplication.DoesNotExist:
                employee = Employee.objects.get(pk=pk)
                application = TeleworkApplication.objects.create(
                    employee=employee
                )
        else:
            queryset = TeleworkApplication.objects.all()
            application = get_object_or_404(queryset, pk=pk)
        serializer = TeleworkApplicationSerializer(application, 
            context={'request': request})
        return Response(serializer.data)

    def update(self, request, pk=None):
        application = TeleworkApplication.objects.get(pk=pk)
        application.date = request.data['date']
        application.program_manager_approve = \
            request.data['program_manager_approve']
        application.hours_onsite = request.data['hours_onsite']
        application.telework_location = request.data['telework_location']
        application.hours_working = request.data['hours_working']
        application.duties = request.data['duties']
        application.communication_when = request.data['communication_when']
        application.communication_time = request.data['communication_time']
        application.communication_how = request.data['communication_how']
        application.equipment_provided_phone = \
            request.data['equipment_provided_phone']
        application.equipment_provided_laptop = \
            request.data['equipment_provided_laptop']
        application.equipment_provided_desktop = \
            request.data['equipment_provided_desktop']
        application.equipment_provided_monitor = \
            request.data['equipment_provided_monitor']
        application.equipment_provided_access = \
            request.data['equipment_provided_access']
        application.equipment_provided_other = \
            request.data['equipment_provided_other']
        application.equipment_provided_other_value = \
            request.data['equipment_provided_other_value']
        application.workspace_checklist_1 = \
            request.data['workspace_checklist_1']
        application.workspace_checklist_2 = \
            request.data['workspace_checklist_2']
        application.workspace_checklist_3 = \
            request.data['workspace_checklist_3']
        application.workspace_checklist_4 = \
            request.data['workspace_checklist_4']
        application.workspace_checklist_5 = \
            request.data['workspace_checklist_5']
        application.workspace_checklist_6 = \
            request.data['workspace_checklist_6']
        application.workspace_checklist_7 = \
            request.data['workspace_checklist_7']
        application.workspace_checklist_8 = \
            request.data['workspace_checklist_8']
        application.workspace_checklist_9 = \
            request.data['workspace_checklist_9']
        application.workspace_checklist_10 = \
            request.data['workspace_checklist_10']
        application.workspace_checklist_11 = \
            request.data['workspace_checklist_11']
        application.workspace_checklist_12 = \
            request.data['workspace_checklist_12']
        application.emergency_checklist_1 = \
            request.data['emergency_checklist_1']
        application.emergency_checklist_2 = \
            request.data['emergency_checklist_2']
        application.emergency_checklist_3 = \
            request.data['emergency_checklist_3']
        application.ergonomics_checklist_1 = \
            request.data['ergonomics_checklist_1']
        application.ergonomics_checklist_2 = \
            request.data['ergonomics_checklist_2']
        application.ergonomics_checklist_3 = \
            request.data['ergonomics_checklist_3']
        application.ergonomics_checklist_4 = \
            request.data['ergonomics_checklist_4']
        application.ergonomics_checklist_5 = \
            request.data['ergonomics_checklist_5']
        application.teleworker_comments = request.data['teleworker_comments']
        application.manager_comments = request.data['manager_comments']
        application.dependent_care_checklist_1 = \
            request.data['dependent_care_checklist_1']

        application.save()
        serialized_application = TeleworkApplicationSerializer(application,
            context={'request': request})
        return Response(serialized_application.data)
    
    # def partial_update(self, request, pk=None):
    #     """
    #     Currently just updates the employee's comments. This might need to be
    #     more general to accept any partial updates.
    #     """
    #     pr = PerformanceReview.objects.get(pk=pk)
    #     pr.evaluation_comments_employee = \
    #         request.data['evaluation_comments_employee']
    #     pr.save()
    #     serialized_review = PerformanceReviewSerializer(pr,
    #         context={'request': request})
    #     return Response(serialized_review.data)


class TeleworkSignatureViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows telework signatures to be created.
    """
    queryset = TeleworkSignature.objects.all()
    serializer_class = TeleworkSignatureSerializer
    # permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        This view should return a list of all signatures made by this user.
        """
        user = self.request.user
        if user.is_authenticated:
            if user.is_staff:
                queryset = TeleworkSignature.objects.all()
            else:
                queryset = TeleworkSignature.objects.filter(employee__user=user)
        else:
            queryset = TeleworkSignature.objects.none()
        return queryset
    
    def create(self, request):
        application = TeleworkApplication.objects.get(
            pk=request.data['application_pk']
        )
        employee = Employee.objects.get(pk=request.data['employee_pk'])
        new_signature = TeleworkSignature.objects.create(
            application=application,
            employee=employee,
            index=request.data['index']
        )
        
        # Send notification to next manager in the chain
        # pr_employee_has_signed = Signature.objects.filter(
        #     employee=pr.employee
        # ).count() == 1
        # pr_manager_has_signed = Signature.objects.filter(
        #     employee=pr.employee.manager
        # ).count() == 1
        # if all(
        #     pr_employee_has_signed,
        #     pr_manager_has_signed,
        #     pr.status == PerformanceReview.EVALUATION_WRITTEN
        # ):
        #     if employee == pr.employee:
        #         send_signature_email_to_manager(employee.manager.manager, pr)
        #     else:
        #         send_signature_email_to_manager(employee.manager, pr)
        
        serialized_signature = TeleworkSignatureSerializer(new_signature,
            context={'request': request})
        return Response(serialized_signature.data)
