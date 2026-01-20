import datetime
import traceback

from django.apps import apps
from django.contrib.auth.models import Group, User

from rest_framework import serializers

from mainsite.helpers import record_error
from people.models import (
    Employee, JobTitle, PRForm, PerformanceReview, ReviewNote, Signature,
    TeleworkApplication, TeleworkSignature, UnitOrProgram,
    ViewedSecurityMessage, WorkflowOptions
)

from workflows.models import Workflow


class JobTitleSerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = JobTitle
        fields = ['pk', 'name']


class UnitSerializer(serializers.HyperlinkedModelSerializer):
    name = serializers.SerializerMethodField()

    class Meta:
        model = UnitOrProgram
        fields = ['pk', 'name']
    
    @staticmethod
    def get_name(unit):
        if unit.name != '-':
            return f'{unit.division.name} - {unit.name}'
        else:
            return unit.division.name


class UserSerializer(serializers.HyperlinkedModelSerializer):
    name = serializers.CharField(source='get_full_name')
    
    class Meta:
        model = User
        fields = [
            'pk', 'url', 'username', 'email', 'name', 'groups', 'is_staff'
        ]


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    user_usernames = serializers.SerializerMethodField()

    class Meta:
        model = Group
        fields = ['pk', 'url', 'name', 'user_set', 'user_usernames']
    
    @staticmethod
    def get_user_usernames(group):
        return map(lambda user: user.username, group.user_set.all())


class EmployeeSerializer(serializers.HyperlinkedModelSerializer):
    name = serializers.CharField()
    username = serializers.EmailField(source='user.username')
    email = serializers.EmailField(source='user.email')
    title = serializers.CharField(source='job_title')
    division = serializers.CharField(
        source='unit_or_program.division.name', default=''
    )
    manager_name = serializers.CharField(source='manager.name', default='')
    manager_pk = serializers.IntegerField(source='manager.pk', default=None)
    is_manager = serializers.SerializerMethodField()
    has_manager = serializers.SerializerMethodField()
    is_eligible_for_telework_application = serializers.SerializerMethodField()
    can_view_seating_charts = serializers.SerializerMethodField()
    can_edit_seating_charts = serializers.SerializerMethodField()
    can_view_desk_reservation_reports = serializers.SerializerMethodField()
    is_upper_manager = serializers.SerializerMethodField()
    prs_can_view = serializers.SerializerMethodField()
    notes_can_view = serializers.SerializerMethodField()
    time_off_requests_can_view = serializers.SerializerMethodField()
    next_to_sign_prs = serializers.SerializerMethodField()
    workflow_roles = serializers.SerializerMethodField()
    is_expense_submitter = serializers.SerializerMethodField()
    is_expense_approver = serializers.SerializerMethodField()
    can_view_phish = serializers.SerializerMethodField()
    can_view_reviews = serializers.SerializerMethodField()
    can_view_mow_routes = serializers.SerializerMethodField()
    can_manage_mow_stops = serializers.SerializerMethodField()
    workflow_display_options = serializers.SerializerMethodField()
    
    class Meta:
        model = Employee
        fields = [
            'url', 'pk', 'name', 'legal_name', 'user', 'username', 'email',
            'title', 'manager_name', 'manager_pk', 'division', 'is_manager',
            'has_manager', 'is_is_employee', 'is_hr_employee',
            'is_sds_hiring_lead', 'is_fiscal_employee',
            'is_eligible_for_telework_application', 'can_view_seating_charts',
            'can_edit_seating_charts', 'can_view_desk_reservation_reports',
            'is_upper_manager', 'is_hr_manager', 'is_division_director',
            'is_executive_director', 'viewed_security_message', 'prs_can_view',
            'notes_can_view', 'telework_applications_can_view',
            'time_off_requests_can_view', 'next_to_sign_prs',
            'email_opt_out_all', 'email_opt_out_timeoff_all',
            'email_opt_out_timeoff_weekly', 'email_opt_out_timeoff_daily',
            'email_opt_out_workflows_all',
            'email_opt_out_workflows_transitions',
            'email_opt_out_workflows_processes', 'email_opt_out_expenses_all',
            'is_all_workflows_admin', 'admin_of_workflows',
            'admin_of_processes', 'workflow_roles', 'is_expense_submitter',
            'is_expense_approver', 'can_view_phish', 'can_view_reviews',
            'can_view_mow_routes', 'can_manage_mow_stops',
            'workflow_display_options'
        ]

    @staticmethod
    def get_is_manager(employee):
        return employee.get_direct_reports().count() != 0
    
    @staticmethod
    def get_has_manager(employee):
        return bool(employee.manager)

    @staticmethod
    def get_is_eligible_for_telework_application(employee):
        if not employee.manager:
            return False
        return all([ 
            not employee.is_executive_director, # Not the executive director
            # Not anyone who reports to the executive director
            # (e.g. finance manager)
            not employee.manager.is_executive_director,
            # Not anyone who reports to the above (e.g. finance employees)
            employee.manager.manager and \
                not employee.manager.manager.is_executive_director,
            not employee.is_division_director, # No division directors
            not employee.manager.is_division_director, # No program managers
            not employee.is_hr_manager,  # Not the HR manager
            # Not anyone who reports to the HR manager
            not employee.manager.is_hr_manager
        ])
    
    @staticmethod
    def get_can_view_seating_charts(employee):
        return employee.can_view_seating_charts()
    
    @staticmethod
    def get_can_edit_seating_charts(employee):
        return employee.can_edit_seating_charts()

    @staticmethod
    def get_can_view_desk_reservation_reports(employee):
        return employee.can_view_desk_reservation_reports()

    @staticmethod
    def get_is_upper_manager(employee):
        return employee.get_direct_reports_descendants().count() != 0
    
    @staticmethod
    def get_prs_can_view(employee):
        return employee.prs_can_view()

    @staticmethod
    def get_notes_can_view(employee):
        return employee.notes_can_view()

    @staticmethod
    def get_telework_applications_can_view(employee):
        return employee.telework_applications_can_view()

    @staticmethod
    def get_time_off_requests_can_view(employee):
        return employee.time_off_requests_can_view()

    @staticmethod
    def get_next_to_sign_prs(employee):
        """
        Returns the name of the next employee who will sign the PR.
        """
        try:
            if employee.is_executive_director:
                return ""
            elif employee.is_hr_manager:
                return Employee.objects.filter(is_executive_director=True)\
                    .first().name
            elif employee.is_division_director:
                return Employee.objects.filter(is_hr_manager=True).first().name
            elif employee.manager:
                return employee.manager.name
            else:
                return ""
        except Exception as e:
            record_error(
                'Error getting next to sign PRs', e, None,
                traceback.format_exc(), 'Employee: {}'.format(employee)
            )
    
    @staticmethod
    def get_workflow_roles(employee):
        workflow_roles_ids = map(
            lambda role: role.id, employee.workflow_roles.all()
        )
        return list(workflow_roles_ids)

    @staticmethod
    def get_is_all_workflows_admin(employee):
        return employee.is_all_workflows_admin

    @staticmethod
    def get_is_admin_of_workflows(employee):
        return employee.is_admin_of_workflows
    
    @staticmethod
    def get_is_admin_of_processes(employee):
        return employee.is_admin_of_processes

    @staticmethod
    def get_is_expense_submitter(employee):
        return employee.is_expense_submitter()
    
    @staticmethod
    def get_is_expense_approver(employee):
        return employee.is_expense_approver()

    @staticmethod
    def get_can_view_phish(employee):
        return employee.can_view_phish()

    @staticmethod
    def get_can_view_reviews(employee):
        return employee.can_view_reviews()

    @staticmethod
    def get_can_view_mow_routes(employee):
        return employee.can_view_mow_routes()

    @staticmethod
    def get_can_manage_mow_stops(employee):
        return employee.can_manage_mow_stops()

    @staticmethod
    def get_workflow_display_options(employee):
        return employee.workflow_display_options()


class SimpleEmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ['pk', 'name', 'legal_name', 'title', 'is_expense_approver']

    title = serializers.CharField(source='job_title')
    is_expense_approver = serializers.SerializerMethodField()

    @staticmethod
    def get_is_expense_approver(employee):
        return employee.is_expense_approver()


class EmployeeEmailSerializer(serializers.ModelSerializer):
    email = serializers.SerializerMethodField()
    
    class Meta:
        model = Employee
        fields = ['email']
    
    @staticmethod
    def get_email(employee):
        return employee.user.email


class PerformanceReviewBaseSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(
        source='employee.name', required=False, read_only=True
    )
    employee_pk = serializers.IntegerField(
        source='employee.pk', read_only=True
    )
    days_until_review = serializers.SerializerMethodField()
    employee_action_required = serializers.SerializerMethodField()
    status = serializers.CharField(source='get_status_display', required=False)

    @staticmethod
    def get_days_until_review(pr):
        today = datetime.date.today()
        delta = pr.period_end_date - today
        return delta.days
    
    def get_employee_action_required(self, pr):
        user = None
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            user = request.user
        if user and hasattr(user, 'employee'):
            return pr.employee_action_required(user.employee)
        return False


class PerformanceReviewSimpleSerializer(PerformanceReviewBaseSerializer):
    complete = serializers.SerializerMethodField()
    
    class Meta:
        model = PerformanceReview
        fields = [
            'url', 'pk', 'employee_name', 'employee_pk', 'period_start_date',
            'period_end_date', 'days_until_review', 'status',
            'employee_action_required', 'complete'
        ]
    
    @staticmethod
    def get_complete(pr):
        return pr.status == PerformanceReview.EVALUATION_HR_PROCESSED


class PerformanceReviewSerializer(PerformanceReviewBaseSerializer):
    form = serializers.SerializerMethodField()
    form_pk = serializers.PrimaryKeyRelatedField(
        source='form', queryset=PRForm.objects.all(), allow_null=True,
        required=False, write_only=True
    )
    employee = serializers.PrimaryKeyRelatedField(
        queryset=Employee.objects.all(),
        write_only=True
    )
    employee_division = serializers.SerializerMethodField()
    employee_unit_or_program = serializers.SerializerMethodField()
    employee_job_title = serializers.CharField(
        source='employee.job_title.name', required=False
    )
    manager_pk = serializers.IntegerField(
        source='employee.manager.pk', read_only=True
    )
    manager_name = serializers.CharField(
        source='employee.manager.name', required=False, read_only=True
    )
    all_required_signatures = serializers.SerializerMethodField()
    position_description_link = serializers.SerializerMethodField()
    signed_position_description = serializers.FileField(required=False)

    class Meta:
        model = PerformanceReview
        fields = [
            'url', 'pk', 'form_pk', 'form', 'data', 'employee_pk', 'employee',
            'employee_name', 'employee_division', 'employee_unit_or_program',
            'employee_job_title', 'manager_pk', 'manager_name',
            'days_until_review', 'status', 'period_start_date',
            'period_end_date', 'effective_date', 'evaluation_type',
            'probationary_evaluation_type', 'step_increase', 'top_step_bonus',
            'action_other',

            'factor_job_knowledge', 'factor_work_quality',
            'factor_work_quantity', 'factor_work_habits', 'factor_analysis',
            'factor_initiative', 'factor_interpersonal',
            'factor_communication', 'factor_dependability',
            'factor_professionalism', 'factor_management',
            'factor_supervision', 'evaluation_successes',
            'evaluation_opportunities', 'evaluation_goals_manager',
            'evaluation_goals_employee','evaluation_comments_employee',

            'position_description_link', 'description_reviewed_employee',
            'signed_position_description', 'all_required_signatures',
            'employee_action_required'
        ]

    @staticmethod
    def get_form(pr):
        if not pr.form:
            return {
                'longResponses': None,
                'factorsResponseSet': None,
                'factors': [],
                'anyNotApplicable': False
            }
        
        any_not_applicable = False
        factors = []
        for factor in pr.form.factors.all().order_by('order'):
            factors.append({
                'name': factor.name,
                'description': factor.description,
                'notApplicableOption': factor.not_applicable_option
            })
            if factor.not_applicable_option:
                any_not_applicable = True
        return {
            'longResponses': pr.form.long_responses,
            'factorsResponseSet': pr.form.factors_response_set.responses,
            'factors': factors,
            'anyNotApplicable': any_not_applicable
        }

    @staticmethod
    def get_employee_division(pr):
        if all([
            pr.employee.unit_or_program,
            pr.employee.unit_or_program.division
        ]):
            return pr.employee.unit_or_program.division.name
        else:
            return ''
    
    @staticmethod
    def get_employee_unit_or_program(pr):
        if pr.employee.unit_or_program:
            return pr.employee.unit_or_program.name
        else:
            return ''
    
    @staticmethod
    def get_evaluation(pr):
        if hasattr(pr, 'performanceevaluation'):
            return pr.performanceevaluation.evaluation
        else:
            return ""

    @staticmethod
    def get_position_description_link(pr):
        return pr.employee.position_description_link()

    @staticmethod
    def get_discussion_took_place(pr):
        if hasattr(pr, 'performanceevaluation'):
            return "Yes" if pr.performanceevaluation.manager_discussed else "No"
        else:
            return "No"
    
    @staticmethod
    def get_all_required_signatures(pr):
        return pr.all_required_signatures()


class PerformanceReviewFileUploadSerializer(
    serializers.HyperlinkedModelSerializer
):
    signed_position_description = serializers.FileField()

    class Meta:
        model = PerformanceReview
        fields = [
            'url', 'signed_position_description'
        ]


class SignatureSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Signature
        fields = [
            'url', 'pk', 'review', 'employee', 'date'
        ]


class ReviewNoteSerializer(serializers.HyperlinkedModelSerializer):
    pk = serializers.IntegerField()
    employee_pk = serializers.IntegerField(source='employee.pk')
    employee_name = serializers.CharField(source='employee.name')
    author_name = serializers.CharField(source='author.name')
    note = serializers.CharField()
    
    class Meta:
        model = ReviewNote
        fields = [
            'url', 'pk', 'employee_pk', 'employee_name', 'author_name',
            'created_at', 'note'
        ]


class ViewedSecurityMessageSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = ViewedSecurityMessage
        fields = [
            'url', 'pk', 'employee', 'security_message', 'datetime'
        ]


class TeleworkApplicationSerializer(serializers.HyperlinkedModelSerializer):
    employee_name = serializers.CharField(source='employee.name')
    employee_pk = serializers.IntegerField(source='employee.pk')
    manager_pk = serializers.IntegerField(source='employee.manager.pk')
    manager_name = serializers.CharField(source='employee.manager.name')
    status = serializers.CharField(source='get_status_display')
    program_manager_signature_0 = serializers.SerializerMethodField()
    employee_signature_0 = serializers.SerializerMethodField()
    employee_signature_1 = serializers.SerializerMethodField()
    manager_signature = serializers.SerializerMethodField()
    program_manager_signature_1 = serializers.SerializerMethodField()
    division_director_signature = serializers.SerializerMethodField()
    dependent_care_documentation = serializers.FileField()
 
    class Meta:
        model = TeleworkApplication
        fields = [
            'url', 'pk', 'employee_name', 'employee_pk', 'manager_pk',
            'manager_name', 'program_manager_pk', 'program_manager_name',
            'status', 'date', 
            
            'program_manager_approve', 'hours_onsite', 'telework_location',
            'hours_working', 'duties', 'communication_when',
            'communication_time', 'communication_how',
            'equipment_provided_phone', 'equipment_provided_laptop',
            'equipment_provided_desktop', 'equipment_provided_monitor',
            'equipment_provided_access', 'equipment_provided_other',
            'equipment_provided_other_value',

            'workspace_checklist_1', 'workspace_checklist_2',
            'workspace_checklist_3', 'workspace_checklist_4',
            'workspace_checklist_5', 'workspace_checklist_6',
            'workspace_checklist_7', 'workspace_checklist_8',
            'workspace_checklist_9', 'workspace_checklist_10',
            'workspace_checklist_11', 'workspace_checklist_12',
            'emergency_checklist_1', 'emergency_checklist_2',
            'emergency_checklist_3', 'ergonomics_checklist_1',
            'ergonomics_checklist_2', 'ergonomics_checklist_3',
            'ergonomics_checklist_4', 'ergonomics_checklist_5',
            
            'teleworker_comments', 'manager_comments',
            
            'dependent_care_checklist_1', 'dependent_care_documentation',

            'program_manager_signature_0', 'employee_signature_0',
            'employee_signature_1', 'manager_signature',
            'program_manager_signature_1', 'division_director_signature'
        ]

    @staticmethod
    def get_program_manager_signature_0(application):
        return application.program_manager_signature_0()

    @staticmethod
    def get_employee_signature_0(application):
        return application.employee_signature_0()
    
    @staticmethod
    def get_employee_signature_1(application):
        return application.employee_signature_1()
    
    @staticmethod
    def get_manager_signature(application):
        return application.manager_signature()

    @staticmethod
    def get_program_manager_signature_1(application):
        return application.program_manager_signature_1()
    
    @staticmethod
    def get_division_director_signature(application):
        return application.division_director_signature()


class TeleworkApplicationFileUploadSerializer(
    serializers.HyperlinkedModelSerializer
):
    dependent_care_documentation = serializers.FileField()

    class Meta:
        model = TeleworkApplication
        fields = [
            'url', 'dependent_care_documentation'
        ]


class TeleworkSignatureSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = TeleworkSignature
        fields = [
            'url', 'pk', 'application', 'employee', 'index', 'date'
        ]