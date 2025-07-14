import datetime
from mainsite.models import SecurityMessage

from django.apps import apps
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext as _

from mainsite.helpers import (
    send_completed_email_to_hr_manager,
    send_signature_email_to_executive_director,
    send_signature_email_to_hr_manager
)
from mainsite.models import ActiveManager, SecurityMessage


SHOW_REVIEW_TO_MANAGER_DAYS_BEFORE_DUE = 60
# SHOW_REVIEW_TO_MANAGER_DAYS_BEFORE_DUE = 360


class Division(models.Model):
    class Meta:
        verbose_name = _("Division")
        verbose_name_plural = _("Divisions")
        ordering = ["name"]

    organization = models.ForeignKey(
        "mainsite.Organization",
        verbose_name=_("organization"),
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    name = models.CharField(_("name"), max_length=100)

    def __str__(self):
        return self.name


class UnitOrProgram(models.Model):
    class Meta:
        verbose_name = _("Unit/Program")
        verbose_name_plural = _("Units/Programs")
        ordering = ["division__name", "name"]

    division = models.ForeignKey(
        "people.Division",
        verbose_name=_("division"),
        on_delete=models.CASCADE
    )
    name = models.CharField(_("name"), max_length=100)

    def __str__(self):
        return f"{self.division.name} : {self.name}"


class JobTitle(models.Model):
    class Meta:
        verbose_name = _("Job Title")
        verbose_name_plural = _("Job Titles")
        ordering = ["name"]

    objects = models.Manager()
    active_objects = ActiveManager()

    active = models.BooleanField(default=True)
    name = models.CharField(_("name"), max_length=100)
    division = models.ForeignKey(
        "people.Division", on_delete=models.SET_NULL, blank=True, null=True
    )
    position_description_link = models.URLField(
        _("position description link"), blank=True, null=True
    )

    def __str__(self):
        return self.name


class Employee(models.Model):
    class Meta:
        verbose_name = _("Employee")
        verbose_name_plural = _("Employees")
        ordering = ["user__username"]

    objects = models.Manager()
    active_objects = ActiveManager()

    def __str__(self):
        return self.user.username

    def get_absolute_url(self):
        return reverse("employee_detail", kwargs={"pk": self.pk})

    def username(self):
        return self.user.username

    active = models.BooleanField(default=True)
    temporary = models.BooleanField(
        default=False,
        verbose_name=_("temporary employee"),
        help_text=(
            "Employee is temporary or exists for test purposes. They are not "
            "present in the payroll system, but should not be deactivated."
        )
    )
    organization = models.ForeignKey(
        "mainsite.Organization",
        verbose_name=_("organization"),
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    user = models.OneToOneField(
        "auth.User", verbose_name=_("user"), on_delete=models.CASCADE,
        related_name="employee"
    )
    number = models.IntegerField("number", unique=True, blank=True, null=True)
    
    # User Profile Preferences
    display_name = models.CharField(
        _("display name"), max_length=100, blank=True, null=True
    )
    email_opt_out_all = models.BooleanField(default=False)
    email_opt_out_timeoff_all = models.BooleanField(default=False)
    email_opt_out_timeoff_weekly = models.BooleanField(default=False)
    email_opt_out_timeoff_daily = models.BooleanField(default=False)
    email_opt_out_workflows_all = models.BooleanField(default=False)
    email_opt_out_workflows_transitions = models.BooleanField(default=False)
    email_opt_out_workflows_processes = models.BooleanField(default=False)
    email_opt_out_expenses_all = models.BooleanField(default=False)
    workflow_options = models.ManyToManyField(
        "workflows.Workflow", through="WorkflowOptions", 
    )

    manager = models.ForeignKey(
        "self",
        related_name="direct_reports",
        blank=True,
        null=True,
        verbose_name=_("manager"),
        on_delete=models.SET_NULL
    )
    unit_or_program = models.ForeignKey(
        "people.UnitOrProgram",
        verbose_name=_("unit/program"),
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    job_title = models.ForeignKey(
        "people.JobTitle",
        verbose_name=_("job title"),
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    position_description_link_override = models.URLField(
        _("position description link override"), blank=True, null=True
    )

    is_division_director = models.BooleanField(
        _("is a division director"), default=False
    )
    
    # These are UNIQUELY TRUE, enforced in model save
    is_hr_manager = models.BooleanField(_("is the HR manager"), default=False)
    is_executive_director = models.BooleanField(
        _("is the executive director"), default=False
    )

    viewed_security_message = models.BooleanField(
        _("has viewed security message"), default=False
    )

    @property
    def name(self):
        if self.display_name:
            return self.display_name
        else:
            return self.user.get_full_name()
    
    @property
    def legal_name(self):
        return self.user.get_full_name()

    @property
    def initials(self):
        if self.display_name:
            return "".join(
                map(lambda x: x[0], self.display_name.split(' '))
            ).upper()
        elif self.user.get_full_name():
            return "".join(
                map(lambda x: x[0], self.user.get_full_name().split(' '))
            ).upper()
        else:
            return self.user.username

    @property
    def is_is_employee(self):
        return self.user.groups.filter(name='IS Employee').exists()
    
    @property
    def is_hr_employee(self):
        return self.user.groups.filter(name='HR Employee').exists()
    
    @property
    def is_sds_hiring_lead(self):
        return self.user.groups.filter(name='SDS Hiring Lead').exists()

    @property
    def is_fiscal_employee(self):
        return self.user.groups.filter(name='Fiscal Employee').exists()

    @property
    def is_program_manager(self):
        return self.manager and self.manager.is_division_director
    
    @property
    def is_admin_employee(self):
        return self.unit_or_program.division.name == "Administrative Services"

    @property
    def is_gs_employee(self):
        return self.unit_or_program.division.name == "Government Services"
    
    @property
    def is_sds_employee(self):
        return self.unit_or_program.division.name == \
            "Senior & Disability Services"

    @property
    def has_program_manager(self):
        current_employee = self
        if current_employee.is_executive_director:
            return False
        if current_employee.is_division_director:
            return False
        if all([
            current_employee.manager,
            current_employee.manager.is_division_director
        ]):
            # They *are* the program manager
            return False
        while True:
            if all([
                current_employee.manager,
                current_employee.manager.is_division_director
            ]):
                return True
            if current_employee.manager:
                current_employee = current_employee.manager
            else:
                return False

    @property
    def get_program_manager(self):
        current_employee = self
        if current_employee.manager.is_division_director:
            return self
        while True:
            if current_employee.manager.is_division_director:
                return current_employee
            if current_employee.manager:
                current_employee = current_employee.manager
            else:
                return None

    @property
    def has_division_director(self):
        current_employee = self
        if current_employee.is_division_director:
            return False
        while True:
            if current_employee.is_division_director:
                return True
            if current_employee.manager:
                current_employee = current_employee.manager
            else:
                return False

    @property
    def get_division_director(self):
        current_employee = self
        if current_employee.is_division_director:
            return None
        while True:
            if current_employee.is_division_director:
                return current_employee
            if current_employee.manager:
                current_employee = current_employee.manager
            else:
                return None

    def save(self, *args, **kwargs):
        # is_hr_manager can only apply to ONE Employee PER Organization
        if self.is_hr_manager:
            try:
                old_manager = Employee.objects.get(
                    is_hr_manager=True, organization=self.organization
                )
                if self != old_manager:
                    old_manager.is_hr_manager = False
                    old_manager.save()
            except Employee.DoesNotExist:
                pass
        # is_executive_director can only apply to ONE Employee PER Organization
        if self.is_executive_director:
            try:
                old_director = Employee.objects.get(
                    is_executive_director=True, organization=self.organization
                )
                if self != old_director:
                    old_director.is_executive_director = False
                    old_director.save()
            except Employee.DoesNotExist:
                pass
        super().save(*args, **kwargs)

    def should_receive_email_of_type(self, type, subtype):
        if self.email_opt_out_all:
            return False
        if type == 'timeoff':
            if self.email_opt_out_timeoff_all:
                return False
            if subtype == 'weekly' and self.email_opt_out_timeoff_weekly:
                return False
            if subtype == 'daily' and self.email_opt_out_timeoff_daily:
                return False
        if type == 'workflows':
            if self.email_opt_out_workflows_all:
                return False
            if all([
                subtype == 'transitions',
                self.email_opt_out_workflows_transitions
            ]):
                return False
            if all([
                subtype == 'processes',
                self.email_opt_out_workflows_processes
            ]):
                return False
        if type == 'expenses':
            if self.email_opt_out_expenses_all:
                return False
        return True

    def employee_next_review(self):
        return self.performancereview_set.all().order_by("period_end_date")\
            .first()

    def get_direct_reports(self):
        return self.direct_reports.all()
    
    def get_descendants_of_employee(self, employee):
        employee_and_descendants = [employee]
        descendants = employee.direct_reports.filter(active=True)
        for descendant in descendants:
            employee_and_descendants += \
                self.get_descendants_of_employee(descendant)
        return employee_and_descendants

    def get_direct_reports_descendants(self, include_self=False):
        # Return all descendant direct reports, including the user's direct
        # reports.
        direct_reports_descendants = [
            self.get_descendants_of_employee(employee) for employee in \
                self.get_direct_reports()
        ]
        # Flatten the 2-D list
        flat_list = [
            item for sublist in direct_reports_descendants for item in sublist
        ]
        pk_list = [item.pk for item in flat_list]
        if include_self:
            pk_list.append(self.pk)
        unique_descendant_pks = list(set(pk_list))
        return Employee.objects.filter(pk__in=unique_descendant_pks)

    def manager_upcoming_reviews(self):
        reviews = []
        for employee in self.get_direct_reports():
            employee_reviews = employee.performancereview_set.all()
            for review in employee_reviews:
                if (
                    review.days_until_due() < \
                        SHOW_REVIEW_TO_MANAGER_DAYS_BEFORE_DUE
                ):
                    reviews.append(review)
        return sorted(reviews, key=lambda review: review.period_end_date)
    
    def signature_upcoming_reviews(self):
        # Returns all upcoming reviews for a manager's direct reports.
        # HR Manager and Executive Director should see upcoming reviews for all
        # Employees.
        reviews = []
        if self.is_hr_manager:
            employees = Employee.objects.all()
        elif self.is_hr_manager:
            employees = Employee.objects.all()
        else:
            employees = self.get_direct_reports_descendants()
        for employee in employees:
            employee_reviews = employee.performancereview_set.all()
            for review in employee_reviews:
                if (
                    review.days_until_due() < \
                        SHOW_REVIEW_TO_MANAGER_DAYS_BEFORE_DUE
                ):
                    reviews.append(review)
        return sorted(reviews, key=lambda review: review.period_end_date)

    def telework_applications_signature_required(self):
        # Returns all telework applications requiring a user's signature.
        applications = []
        # Division Director
        if self.is_division_director:
            for employee in self.get_direct_reports_descendants():
                if hasattr(employee, 'teleworkapplication') and employee.teleworkapplication.division_director_ready_to_sign():
                    applications.append(employee.teleworkapplication)
        # Program Manager
        elif self.is_program_manager:
            for employee in self.get_direct_reports_descendants():
                if hasattr(employee, 'teleworkapplication') and employee.teleworkapplication.program_manager_ready_to_sign():
                    applications.append(employee.teleworkapplication)    
        # Manager
        else:
            for employee in self.direct_reports.all():
                if hasattr(employee, 'teleworkapplication') and employee.teleworkapplication.manager_ready_to_sign():
                    applications.append(employee.teleworkapplication)
        return sorted(applications, key=lambda application: application.date)
    
    def telework_applications_signature_not_required(self):
        # Returns all telework applications signed by the user
        applications = []
        # Division Director
        if self.is_division_director:
            for employee in self.get_direct_reports_descendants():
                if hasattr(employee, 'teleworkapplication') and employee.teleworkapplication.division_director_signed():
                    applications.append(employee.teleworkapplication)
        # Program Manager
        elif self.is_program_manager:
            for employee in self.get_direct_reports_descendants():
                if hasattr(employee, 'teleworkapplication') and employee.teleworkapplication.program_manager_signed():
                    applications.append(employee.teleworkapplication)
        # Manager
        else:
            for employee in self.direct_reports.all():
                if hasattr(employee, 'teleworkapplication') and employee.teleworkapplication.manager_signed():
                    applications.append(employee.teleworkapplication)
        return sorted(applications, key=lambda application: application.date)

    def prs_can_view(self):
        # You can view all PRs for which either you are the employee or the
        # employee is your direct report or a descendant direct report.
        if self.is_hr_manager or self.is_executive_director:
            return map(lambda pr: pr.id, PerformanceReview.objects.all())
        self_and_direct_reports = self.get_direct_reports_descendants(include_self=True)
        pr_ids = []
        for employee in self_and_direct_reports:
            employee_pr_ids = map(lambda pr: pr.id, PerformanceReview.objects.filter(employee=employee))
            pr_ids += employee_pr_ids
        return list(pr_ids)
    
    def notes_can_view(self):
        # You can view all notes you wrote.
        note_ids = map(lambda note: note.id, ReviewNote.objects.filter(author=self))
        return list(note_ids)

    def telework_applications_can_view(self):
        # You can view all Telework Applications for which either you are the
        # employee or the employee is your direct report or a descendant direct
        # report. Employees with the 'View all telework applications' group
        # role can view all of them.
        view_all_applications = self.user.groups.filter(name='View all telework applications').exists()
        if self.is_hr_manager or self.is_executive_director or view_all_applications:
            return map(lambda pr: pr.id, TeleworkApplication.objects.all())
        self_and_direct_reports = self.get_direct_reports_descendants(include_self=True)
        application_ids = []
        for employee in self_and_direct_reports:
            employee_application_ids = map(lambda pr: pr.id, TeleworkApplication.objects.filter(employee=employee))
            application_ids += employee_application_ids
        return list(application_ids)
    
    def time_off_requests_can_view(self):
        # You can view/edit all requests you made.
        TimeOffRequestModel = apps.get_model('timeoff', 'TimeOffRequest') # Avoid circular import
        tor_ids = map(lambda tor: tor.id, TimeOffRequestModel.objects.filter(employee=self))
        return list(tor_ids)

    def can_view_seating_charts(self):
        # You can view seating charts if you are an ED, HR Manager, or Division
        # Director. Employees with the 'HR Employee' or 'View Seating Charts'
        # group role can also view them.
        hr_employee = self.user.groups.filter(name='HR Employee').exists()
        view_seating_charts = self.user.groups.filter(name='View seating charts').exists()
        if any([
            self.is_executive_director, self.is_hr_manager,
            self.is_division_director, hr_employee, view_seating_charts
        ]):
            return True
        else:
            return False
    
    def can_edit_seating_charts(self):
        # Employees with the 'Edit Seating Charts' group role can edit seating
        # charts.
        edit_seating_charts = self.user.groups.filter(name='Edit seating charts').exists()
        if edit_seating_charts:
            return True
        else:
            return False
    
    def can_view_desk_reservation_reports(self):
        # Employees with the 'View Desk Reservation Reports' group role can
        # view them.
        view_desk_reservation_reports = self.user.groups.filter(name='View Desk Reservation Reports').exists()
        if view_desk_reservation_reports:
            return True
        else:
            return False

    def position_description_link(self):
        # Returns override link if provided, otherwise the link from job title if there is a job title
        if self.position_description_link_override:
            return self.position_description_link_override
        elif self.job_title and self.job_title.position_description_link:
            return self.job_title.position_description_link
        return None

    def is_all_workflows_admin(self):
        role = apps.get_model('workflows', 'Role').objects.get(name="All Workflows Admins")
        return self in role.members.all()

    def is_employee_transition_admin(self):
        role = apps.get_model('workflows', 'Role').objects.get(name="Employee Transition Admins")
        return self in role.members.all()
    
    def can_view_employee_transitions(self):
        return self.is_employee_transition_admin() or self.is_all_workflows_admin()

    def admin_of_workflows(self):
        all_workflows = apps.get_model('workflows', 'Workflow').objects.all().select_related('role')
        if self.is_all_workflows_admin():
            return [workflow.id for workflow in all_workflows]
        return [workflow.id for workflow in list(all_workflows) if workflow.role and self in workflow.role.members.all()]
    
    def admin_of_processes(self):
        all_processes = apps.get_model('workflows', 'Process').objects.all().select_related('role')
        return [process.id for process in list(all_processes) if process.role and self in process.role.members.all()]
    
    def is_expense_submitter(self):
        return self.user.groups.filter(name='Expense Submitter').exists()
    
    def is_expense_approver(self):
        return self.user.groups.filter(name='Expense Approver').exists()

    def can_view_reviews(self):
        return self.user.groups.filter(
            name='View Performance Reviews'
        ).exists()

    def can_view_mow_routes(self):
        view_mow_routes = self.user.groups.filter(name='View Meals on Wheels Routes').exists()
        if view_mow_routes:
            return True
        else:
            return False
    
    def can_manage_mow_stops(self):
        manage_mow_stops = self.user.groups.filter(name='Manage Meals on Wheels Stops').exists()
        if manage_mow_stops:
            return True
        else:
            return False
    
    def workflow_display_options(employee):
        workflows = employee.admin_of_workflows()
        wf_options = WorkflowOptions.objects\
            .filter(employee=employee, workflow__in=workflows)
        set_options = []
        unset_options = []
        for wf_id in workflows:
            try:
                wf_option = wf_options.get(workflow__id=wf_id)
                set_options.append({
                    'id': wf_id,
                    'name': wf_option.workflow.name,
                    'type': wf_option.workflow.type,
                    'icon': wf_option.workflow.icon,
                    'display': wf_option.display,
                    'order': wf_option.order
                })
            except WorkflowOptions.DoesNotExist:
                wf = apps.get_model('workflows.Workflow').objects.get(id=wf_id)
                unset_options.append({
                    'id': wf_id,
                    'name': wf.name,
                    'type': wf.type,
                    'icon': wf.icon,
                    'display': True,
                    'order': 999
                })
        return sorted(set_options, key=lambda x: x['order']) + unset_options


class WorkflowOptions(models.Model):
    class Meta:
        verbose_name = _("Workflow Option")
        verbose_name_plural = _("Workflow Options")

    employee = models.ForeignKey("Employee", on_delete=models.CASCADE)
    workflow = models.ForeignKey(
        "workflows.Workflow", on_delete=models.CASCADE
    )
    display = models.BooleanField(default=True)
    order = models.IntegerField(default=0)


class ManagerUpcomingReviewsManager(models.Manager):
    def get_queryset(self, user):
        queryset = super().get_queryset()
        if hasattr(user, 'employee'):
            desired_pks = [pr.pk for pr in user.employee.manager_upcoming_reviews()]
            queryset = queryset.filter(pk__in=desired_pks)
        return queryset


######################
### PR Base Models ###
######################

class SignatureBase(models.Model):
    class Meta:
        abstract = True

    employee = models.ForeignKey("people.Employee", on_delete=models.CASCADE)
    date = models.DateField(_("signature date"), auto_now=False, auto_now_add=True)


class SignatureReminderBase(models.Model):
    class Meta:
        abstract = True

    employee = models.ForeignKey("people.Employee", on_delete=models.CASCADE)
    date = models.DateField(_("reminder date"), auto_now=False, auto_now_add=True)
    next_date = models.DateField(_("planned next reminder date"))


class PerformanceReview(models.Model):
    class Meta:
        verbose_name = _("Performance Review")
        verbose_name_plural = _("Performance Reviews")
        ordering = ["-pk"]

    def __str__(self):
        return f"Performance review for {self.employee.user.username} on {self.period_end_date}"

    def get_absolute_url(self):
        return reverse("performance_review_detail", kwargs={"pk": self.pk})

    # Managers for filtering PRs
    objects = models.Manager()
    manager_upcoming_reviews = ManagerUpcomingReviewsManager()

    NEEDS_EVALUATION = 'N'
    EVALUATION_WRITTEN = 'EW'
    EVALUATION_APPROVED = 'EA'
    EVALUATION_HR_PROCESSED = 'EP'
    EVALUATION_ED_APPROVED = 'ED'
    STATUS_CHOICE = [
        (NEEDS_EVALUATION, 'Needs evaluation'),
        (EVALUATION_WRITTEN, 'Evaluation written and reviewed with employee'),
        (EVALUATION_APPROVED, 'Evaluation approved up to division director'),
        (EVALUATION_HR_PROCESSED, 'Evaluation processed by HR'),
        (EVALUATION_ED_APPROVED, 'Evaluation approved by executive director'),
    ]

    PROBATIONARY_EVALUATION = 'P'
    ANNUAL_EVALUATION = 'A'
    EVALUATION_TYPE_CHOICE = [
        (PROBATIONARY_EVALUATION, 'Probationary evaluation'),
        (ANNUAL_EVALUATION, 'Annual evaluation'),
    ]

    SEIU_PROBATIONARY_EVALUATION = 'S'
    NON_SEIU_PROBATIONARY_EVALUATION = 'N'
    PROBATIONARY_EVALUATION_TYPE_CHOICE = [
        (NON_SEIU_PROBATIONARY_EVALUATION, 'SEIU (180 day)'),
        (NON_SEIU_PROBATIONARY_EVALUATION, 'Non-SEIU (6 month)'),
    ]

    YES = 'Y'
    NO = 'N'
    NULLABLE_BOOLEAN_CHOICE = [
        (YES, 'Yes'),
        (NO, 'No')
    ]

    NEEDS_IMPROVEMENT = 'N'
    MEETS_JOB_REQUIREMENTS = 'M'
    EXCEEDS_JOB_REQUIREMENTS = 'E'
    NOT_APPLICABLE = 'NA'
    PERFORMANCE_FACTOR_CHOICE = [
        (NEEDS_IMPROVEMENT, 'Needs Improvement'),
        (MEETS_JOB_REQUIREMENTS, 'Meets Job Requirements'),
        (EXCEEDS_JOB_REQUIREMENTS, 'Exceeds Job Requirements'),
        (NOT_APPLICABLE, 'Not Applicable'),
    ]

    form = models.ForeignKey(
        "PRForm", on_delete=models.CASCADE, blank=True, null=True
    )
    data = models.JSONField(blank=True, null=True)

    status = models.CharField(_("review status"), max_length=2, choices=STATUS_CHOICE, default=NEEDS_EVALUATION)

    employee = models.ForeignKey("Employee", verbose_name=_("employee"), on_delete=models.CASCADE)
    period_start_date = models.DateField(_("performance period start date"), auto_now=False, auto_now_add=False)
    period_end_date = models.DateField(_("performance period end date"), auto_now=False, auto_now_add=False)
    effective_date = models.DateField(_("effective date"), auto_now=False, auto_now_add=False)

    evaluation_type = models.CharField(_("evaluation type"), max_length=1, choices=EVALUATION_TYPE_CHOICE, default=ANNUAL_EVALUATION, blank=True, null=True)
    probationary_evaluation_type = models.CharField(_("probationary evaluation type"), max_length=1, choices=PROBATIONARY_EVALUATION_TYPE_CHOICE, blank=True, null=True)

    step_increase = models.CharField(_("step increase"), max_length=1, choices=NULLABLE_BOOLEAN_CHOICE, blank=True, null=True)
    top_step_bonus = models.CharField(_("top step bonus"), max_length=1, choices=NULLABLE_BOOLEAN_CHOICE, blank=True, null=True)
    action_other = models.CharField(_("action other"), max_length=255, blank=True)
    
    factor_job_knowledge = models.CharField(_("job knowledge"), max_length=2, choices=PERFORMANCE_FACTOR_CHOICE, blank=True, null=True)
    factor_work_quality = models.CharField(_("quality of work"), max_length=2, choices=PERFORMANCE_FACTOR_CHOICE, blank=True, null=True)
    factor_work_quantity = models.CharField(_("quanitity of work"), max_length=2, choices=PERFORMANCE_FACTOR_CHOICE, blank=True, null=True)
    factor_work_habits = models.CharField(_("work habits"), max_length=2, choices=PERFORMANCE_FACTOR_CHOICE, blank=True, null=True)
    factor_analysis = models.CharField(_("analysis and decision-making"), max_length=2, choices=PERFORMANCE_FACTOR_CHOICE, blank=True, null=True)
    factor_initiative = models.CharField(_("initiative and creativity"), max_length=2, choices=PERFORMANCE_FACTOR_CHOICE, blank=True, null=True)
    factor_interpersonal = models.CharField(_("interpersonal relations"), max_length=2, choices=PERFORMANCE_FACTOR_CHOICE, blank=True, null=True)
    factor_communication = models.CharField(_("communication"), max_length=2, choices=PERFORMANCE_FACTOR_CHOICE, blank=True, null=True)
    factor_dependability = models.CharField(_("dependability and responsibility"), max_length=2, choices=PERFORMANCE_FACTOR_CHOICE, blank=True, null=True)
    factor_professionalism = models.CharField(_("professionalism and customer service"), max_length=2, choices=PERFORMANCE_FACTOR_CHOICE, blank=True, null=True)
    factor_management = models.CharField(_("project management"), max_length=2, choices=PERFORMANCE_FACTOR_CHOICE, blank=True, null=True)
    factor_supervision = models.CharField(_("supervision"), max_length=2, choices=PERFORMANCE_FACTOR_CHOICE, blank=True, null=True)

    evaluation_successes = models.TextField(_("employee's successes"), blank=True)
    evaluation_opportunities = models.TextField(_("opportunities for growth"), blank=True)
    evaluation_goals_manager = models.TextField(_("goals for the coming year (manager)"), blank=True)
    evaluation_goals_employee = models.TextField(_("goals for the coming year (employee)"), blank=True)
    evaluation_comments_employee = models.TextField(_("employee comments"), blank=True)

    description_reviewed_employee = models.BooleanField(_("position description has been reviewed with employee"), default=False)
    signed_position_description = models.FileField(_("signed position description"), upload_to="uploads/signed-position-descriptions", blank=True, null=True)

    def username(self):
        return self.employee.user.username

    def days_until_due(self):
        timedelta = self.effective_date - datetime.date.today()
        return timedelta.days

    def overdue(self):
        if self.days_until_due() <= 0:
            return True
        return False

    def employee_action_required(self, employee):
        # Return (True, reason) if action is required. Else, return False
        # Manager might need to complete review
        if all([
            self.status == PerformanceReview.NEEDS_EVALUATION,
            self.employee.manager == employee,
            self.days_until_due() <= 30
        ]):
            return True, "Review is ready for completion"
        # Employee might need to complete self-evaluation
        if all([
            self.evaluation_comments_employee == "",
            self.employee == employee
        ]):
            return True, "Please complete your self-evaluation"
        # Anyone might need to sign the review
        signatures = self.all_required_signatures()
        for signature in signatures:
            if signature[4] and signature[3] == employee.pk:
                return True, "Your signature is required"
        return False, ""

    def employee_has_signed(self, employee):
        return Signature.objects.filter(review=self, employee=employee).count()

    def all_required_signatures(self):
        """
        Returns a list of lists of the form:
        (
            Employee Title, Employee Name, Signature Date, Employee PK,
            Whether the Employee is ready to sign and needs to sign
        )
        such that each tuple represents a signature required or already created
        for the Performance Review to be completed. Starts with the Employee
        and proceeds up the management chain until it gets to the Division
        Director. And then we add HR Manager and Executive Director.
        """
        signatures = []
        employee = self.employee
        employee_signature = Signature.objects.filter(review=self, employee=self.employee).first()
        last_employee_in_chain = employee # Keep track of the last employee so we can check if they signed
        added_hr_manager = False
        added_executive_director = False
        while True:
            # Try to get the current Employee's signature and add it to the signature list
            if len(signatures) == 0:
                title = "Employee"
            elif len(signatures) == 1:
                title = "Manager"
            else:
                if employee.job_title:
                    title = employee.job_title.name
                else:
                    title = None
            signature = Signature.objects.filter(review=self, employee=employee).first()
            if signature:
                signatures.append([title, signature.employee.name, signature.date, None, False]) # Not ready to sign because there is a signature
            else:
                ready_to_sign = False
                if title in ["Employee", "Manager"]:
                    if self.status != PerformanceReview.NEEDS_EVALUATION:
                        ready_to_sign = True
                else:
                    # If direct report has signed, we are ready
                    direct_report_signature = Signature.objects.filter(review=self, employee=last_employee_in_chain).first()
                    if direct_report_signature and employee_signature:
                        ready_to_sign = True
                signatures.append([title, None, None, employee.pk, ready_to_sign])
            
            # Keep track of whether we're already adding HR manager and ED signatures
            if employee.is_hr_manager:
                added_hr_manager = True
            if employee.is_executive_director:
                added_executive_director = True

            # Get the next manager in the chain
            if employee.is_division_director:
                break
            if employee.manager:
                last_employee_in_chain = employee
                employee = employee.manager
            else:
                break
        
        # Finally, add the HR Manager and Executive Director Signatures if still needed
        if not added_hr_manager:
            hr_manager = Employee.objects.filter(is_hr_manager=True).first()
            hr_signature = Signature.objects.filter(review=self, employee=hr_manager).first()
            if hr_signature:
                signatures.append(["Human Resources Manager", hr_manager.name, hr_signature.date, None, False]) # Not ready to sign because there is a signature
            else:
                # If last manager has signed, we are ready
                direct_report_signature = Signature.objects.filter(review=self, employee=last_employee_in_chain).first()
                ready_to_sign = False
                if direct_report_signature:
                    ready_to_sign = True
                signatures.append(["Human Resources Manager", None, None, hr_manager.pk, ready_to_sign])
        if not added_executive_director:
            ed = Employee.objects.filter(is_executive_director=True).first()
            ed_signature = Signature.objects.filter(review=self, employee=ed).first()
            if ed_signature:
                signatures.append(["Executive Director", ed.name, ed_signature.date, None, False]) # Not ready to sign because there is a signature
            else:
                # If HR manager has signed, we are ready
                ready_to_sign = False
                if hr_signature:
                    ready_to_sign = True
                signatures.append(["Executive Director", None, None, ed.pk, ready_to_sign])
        return signatures

    # NOTE: Not currently used, as we just wait for the next review to be
    # created in Caselle and exported. In the future, we may want to have
    # this app be the single source of truth for performance reviews.
    def create_next_review_for_employee(self):
        PerformanceReview.objects.create(
            employee=self.employee,
            period_start_date=self.period_end_date,
            period_end_date=self.period_end_date + datetime.timedelta(days=365),
            effective_date=self.effective_date + datetime.timedelta(days=365),
            evaluation_type=self.ANNUAL_EVALUATION
        )


class PRForm(models.Model):
    name = models.CharField(max_length=255)
    version = models.IntegerField(default=1)
    factors_response_set = models.ForeignKey(
        "PRFactorResponseSet", on_delete=models.CASCADE, blank=True, null=True
    )
    long_responses = models.JSONField(
        blank=True, null=True, default=list,
        help_text="Format [[\"Title\", \"Subtitle\"], ...] e.g. [[\"Strengths\", \"\"], [\"Areas for Improvement\", \"Be nice!\"]]"
    )

    class Meta:
        unique_together = ("name", "version")
        ordering = ["-pk"]
        verbose_name = _("Performance Review Form")

    def __str__(self):
        return f"{self.name} v{self.version}"


class PRFactor(models.Model):
    form = models.ForeignKey(
        "PRForm", on_delete=models.CASCADE, related_name="factors"
    )
    order = models.IntegerField(default=0)
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255, blank=True)
    not_applicable_option = models.BooleanField(default=False)


class PRFactorResponseSet(models.Model):
    class Meta:
        verbose_name = _("Performance Review Factor Response Set")

    def __str__(self):
        return str(self.responses)

    responses = models.JSONField(
        default=list, help_text="Format e.g. [\"Good\", \"Bad\", \"Ugly\"]"
    )


class SignatureReminder(SignatureReminderBase):
    """
    Represents the last time an employee was reminded to sign a Performance
    Evaluation. We can use this to remind them again a specific amount of time
    in the future.
    """
    
    class Meta:
        verbose_name = _("Signature Reminder")
        verbose_name_plural = _("Signature Reminders")
        get_latest_by = ("date")

    def __str__(self):
        if self.employee == self.review.employee:
            return f"Reminder for {self.employee.user.username} on {self.date} to sign their own review"
        elif self.employee == self.review.employee.manager:
            return f"Reminder for {self.employee.user.username} on {self.date} to sign a review for {self.review.employee.user.username} that they wrote"
        else:
            return f"Reminder for {self.employee.user.username} on {self.date} to sign a review for {self.review.employee.user.username}"

    review = models.ForeignKey("people.PerformanceReview", verbose_name=_("performance review"), on_delete=models.CASCADE)


class Signature(SignatureBase):
    class Meta:
        verbose_name = _("PR Signature")
        verbose_name_plural = _("PR Signatures")

    def __str__(self):
        return f"{self.employee.name}'s approval of {self.review.employee.name}'s performance review"

    review = models.ForeignKey("people.PerformanceReview", verbose_name=_("performance review"), on_delete=models.CASCADE)


#######################
### Self-Evaluation ###
#######################

# class EmployeeSelfEvaluation(models.Model):
#     review = models.OneToOneField("people.PerformanceReview", verbose_name=_("performance review"), on_delete=models.CASCADE)
#     self_evaluation_date = models.DateField(blank=True, null=True)
#     self_evaluation_accomplishments = models.TextField(_("employee self-evaluation accomplishments"), blank=True, null=True)
#     self_evaluation_help = models.TextField(_("employee self-evaluation help"), blank=True, null=True)
#     self_evaluation_communications = models.TextField(_("employee self-evaluation communications"), blank=True, null=True)
#     self_evaluation_abilities = models.TextField(_("employee self-evaluation abilities"), blank=True, null=True)
#     self_evaluation_training = models.TextField(_("employee self-evaluation training"), blank=True, null=True)
#     self_evaluation_goals = models.TextField(_("employee self-evaluation goals"), blank=True, null=True)
#     self_evaluation_future = models.TextField(_("employee self-evaluation future"), blank=True, null=True)


# class SelfEvaluationSignatureReminder(SignatureReminderBase):
#     """
#     Represents the last time an employee was reminded to sign an Employee
#     Self Evaluation. We can use this to remind them again a specific amount of
#     time in the future.
#     """
    
#     class Meta:
#         verbose_name = _("Self Evaluation Signature Reminder")
#         verbose_name_plural = _("Self Evaluation Signature Reminders")
#         get_latest_by = ("date")

#     # def __str__(self):
#     #     if self.employee == self.review.employee:
#     #         return f"Reminder for {self.employee.user.username} on {self.date} to sign their own review"
#     #     elif self.employee == self.review.employee.manager:
#     #         return f"Reminder for {self.employee.user.username} on {self.date} to sign a review for {self.review.employee.user.username} that they wrote"
#     #     else:
#     #         return f"Reminder for {self.employee.user.username} on {self.date} to sign a review for {self.review.employee.user.username}"

#     self_evaluation = models.ForeignKey("people.EmployeeSelfEvaluation", on_delete=models.CASCADE)


# class SelfEvaluationSignature(SignatureBase):
#     class Meta:
#         verbose_name = _("Self Evaluation Signature")
#         verbose_name_plural = _("Self Evaluation Signatures")

#     def __str__(self):
#         return f"{self.employee.name}'s approval of {self.review.employee.name}'s performance review self evaluation"

#     self_evaluation = models.ForeignKey("people.EmployeeSelfEvaluation", on_delete=models.CASCADE)


class ReviewNote(models.Model):
    class Meta:
        verbose_name = _("Review Note")
        verbose_name_plural = _("Review Notes")
        ordering = ["-pk"]

    def get_absolute_url(self):
        return reverse("note-update", kwargs={"pk": self.pk})

    author = models.ForeignKey("Employee", related_name="notes_written", verbose_name=_("author"), on_delete=models.CASCADE)
    employee = models.ForeignKey("Employee", related_name="notes", verbose_name=_("employee"), on_delete=models.CASCADE)
    created_at = models.DateTimeField(_("review note date"), auto_now=False, auto_now_add=True)
    note = models.TextField(_("review note"))


class ViewedSecurityMessage(models.Model):
    employee = models.ForeignKey("people.Employee", verbose_name=_("employee"), on_delete=models.CASCADE)
    security_message = models.ForeignKey(SecurityMessage, on_delete=models.CASCADE)
    datetime = models.DateTimeField(_("viewed date"), auto_now=False, auto_now_add=True)


class AllRelevantTeleworkApplicationsManager(models.Manager):
    def get_queryset(self, user):
        if not hasattr(user, 'employee'):
            import pdb; pdb.set_trace();
        queryset = super().get_queryset()
        desired_pks = [pr.pk for pr in user.employee.all_relevant_telework_applications()]
        queryset = queryset.filter(pk__in=desired_pks)
        return queryset


class TeleworkApplicationsSignatureRequiredManager(models.Manager):
    def get_queryset(self, user):
        queryset = super().get_queryset()
        desired_pks = [pr.pk for pr in user.employee.telework_applications_signature_required()]
        queryset = queryset.filter(pk__in=desired_pks)
        return queryset


class TeleworkApplicationsSignatureNotRequiredManager(models.Manager):
    def get_queryset(self, user):
        queryset = super().get_queryset()
        desired_pks = [pr.pk for pr in user.employee.telework_applications_signature_not_required()]
        queryset = queryset.filter(pk__in=desired_pks)
        return queryset


class TeleworkApplication(models.Model):
    class Meta:
        verbose_name = _("Telework Application")
        verbose_name_plural = _("Telework Applications")
        ordering = ["-pk"]

    def __str__(self):
        return f"Telework application for {self.employee.user.username}"

    def get_absolute_url(self):
        return reverse("telework_application", kwargs={"pk": self.pk})

    # Managers for filtering PRs
    objects = models.Manager()
    all_relevant_applications = AllRelevantTeleworkApplicationsManager()
    applications_signature_required = TeleworkApplicationsSignatureRequiredManager()
    applications_signature_not_required = TeleworkApplicationsSignatureNotRequiredManager()

    INCOMPLETE = 'I'
    READY_FOR_SIGNATURE = 'R'
    APPROVED = 'A'
    STATUS_CHOICE = [
        (INCOMPLETE, 'Incomplete'),
        (READY_FOR_SIGNATURE, 'Ready for signature'),
        (APPROVED, 'Approved')
    ]

    YES = 'Y'
    NO = 'N'
    NULLABLE_BOOLEAN_CHOICE = [
        (YES, 'Yes'),
        (NO, 'No')
    ]

    employee = models.OneToOneField("Employee", verbose_name=_("employee"), on_delete=models.CASCADE)
    status = models.CharField(_("application status"), max_length=1, choices=STATUS_CHOICE, default=INCOMPLETE)
    date_approved = models.DateField(_("date approved"), auto_now=False, auto_now_add=False, blank=True, null=True)

    date = models.DateField(_("date"), auto_now=False, auto_now_add=False, blank=True, null=True)
    program_manager_approve = models.CharField(_("program manager approve"), max_length=1, choices=NULLABLE_BOOLEAN_CHOICE, blank=True, null=True)

    hours_onsite = models.TextField(_("hours onsite"), blank=True, null=True)
    telework_location = models.TextField(_("telework location"), blank=True, null=True)
    hours_working = models.TextField(_("hours working"), blank=True, null=True)
    duties = models.TextField(_("duties"), blank=True, null=True)
    communication_when = models.TextField(_("communication when"), blank=True, null=True)
    communication_time = models.TextField(_("communication time"), blank=True, null=True)
    communication_how = models.TextField(_("communication how"), blank=True, null=True)

    equipment_provided_phone = models.BooleanField(_("equipment provided phone"), default=False)
    equipment_provided_laptop = models.BooleanField(_("equipment provided laptop"), default=False)
    equipment_provided_desktop = models.BooleanField(_("equipment provided desktop"), default=False)
    equipment_provided_monitor = models.BooleanField(_("equipment provided monitor"), default=False)
    equipment_provided_access = models.BooleanField(_("equipment provided access"), default=False)
    equipment_provided_other = models.BooleanField(_("equipment provided other"), default=False)
    equipment_provided_other_value = models.TextField(_("equipment provided other value"), blank=True, null=True)

    workspace_checklist_1 = models.CharField(_("workspace checklist 1"), max_length=1, choices=NULLABLE_BOOLEAN_CHOICE, blank=True, null=True)
    workspace_checklist_2 = models.CharField(_("workspace checklist 2"), max_length=1, choices=NULLABLE_BOOLEAN_CHOICE, blank=True, null=True)
    workspace_checklist_3 = models.CharField(_("workspace checklist 3"), max_length=1, choices=NULLABLE_BOOLEAN_CHOICE, blank=True, null=True)
    workspace_checklist_4 = models.CharField(_("workspace checklist 4"), max_length=1, choices=NULLABLE_BOOLEAN_CHOICE, blank=True, null=True)
    workspace_checklist_5 = models.CharField(_("workspace checklist 5"), max_length=1, choices=NULLABLE_BOOLEAN_CHOICE, blank=True, null=True)
    workspace_checklist_6 = models.CharField(_("workspace checklist 6"), max_length=1, choices=NULLABLE_BOOLEAN_CHOICE, blank=True, null=True)
    workspace_checklist_7 = models.CharField(_("workspace checklist 7"), max_length=1, choices=NULLABLE_BOOLEAN_CHOICE, blank=True, null=True)
    workspace_checklist_8 = models.CharField(_("workspace checklist 8"), max_length=1, choices=NULLABLE_BOOLEAN_CHOICE, blank=True, null=True)
    workspace_checklist_9 = models.CharField(_("workspace checklist 9"), max_length=1, choices=NULLABLE_BOOLEAN_CHOICE, blank=True, null=True)
    workspace_checklist_10 = models.CharField(_("workspace checklist 10"), max_length=1, choices=NULLABLE_BOOLEAN_CHOICE, blank=True, null=True)
    workspace_checklist_11 = models.CharField(_("workspace checklist 11"), max_length=1, choices=NULLABLE_BOOLEAN_CHOICE, blank=True, null=True)
    workspace_checklist_12 = models.CharField(_("workspace checklist 12"), max_length=1, choices=NULLABLE_BOOLEAN_CHOICE, blank=True, null=True)

    emergency_checklist_1 = models.CharField(_("emergency checklist 1"), max_length=1, choices=NULLABLE_BOOLEAN_CHOICE, blank=True, null=True)
    emergency_checklist_2 = models.CharField(_("emergency checklist 2"), max_length=1, choices=NULLABLE_BOOLEAN_CHOICE, blank=True, null=True)
    emergency_checklist_3 = models.CharField(_("emergency checklist 3"), max_length=1, choices=NULLABLE_BOOLEAN_CHOICE, blank=True, null=True)

    ergonomics_checklist_1 = models.CharField(_("emergency checklist 1"), max_length=1, choices=NULLABLE_BOOLEAN_CHOICE, blank=True, null=True)
    ergonomics_checklist_2 = models.CharField(_("emergency checklist 2"), max_length=1, choices=NULLABLE_BOOLEAN_CHOICE, blank=True, null=True)
    ergonomics_checklist_3 = models.CharField(_("emergency checklist 3"), max_length=1, choices=NULLABLE_BOOLEAN_CHOICE, blank=True, null=True)
    ergonomics_checklist_4 = models.CharField(_("emergency checklist 4"), max_length=1, choices=NULLABLE_BOOLEAN_CHOICE, blank=True, null=True)
    ergonomics_checklist_5 = models.CharField(_("emergency checklist 5"), max_length=1, choices=NULLABLE_BOOLEAN_CHOICE, blank=True, null=True)

    teleworker_comments = models.TextField(_("teleworker comments"), blank=True, null=True)
    manager_comments = models.TextField(_("manager comments"), blank=True, null=True)

    dependent_care_checklist_1 = models.CharField(_("dependent care checklist 1"), max_length=1, choices=NULLABLE_BOOLEAN_CHOICE, blank=True, null=True)
    dependent_care_documentation = models.FileField(_("dependent care documentation"), upload_to="uploads/dependent-care-documentation", blank=True, null=True)

    @property
    def program_manager_pk(self):
        if self.employee.has_program_manager:
            if self.employee.manager.job_title.name == 'Program Manager':
                return self.employee.manager.pk
            elif self.employee.manager.manager.job_title.name == 'Program Manager':
                return self.employee.manager.manager.pk
            else:
                return -1
        else:
            return -1

    @property
    def program_manager_name(self):
        if self.employee.has_program_manager:
            if self.employee.manager.job_title.name == 'Program Manager':
                return self.employee.manager.name
            elif self.employee.manager.manager.job_title.name == 'Program Manager':
                return self.employee.manager.manager.name
            else:
                return 'NO PROGRAM MANAGER FOUND'
        else:
            return 'NO PROGRAM MANAGER FOUND'

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # Mark as ready for signature if it is complete and has employee signatures
        if self.status == TeleworkApplication.INCOMPLETE:
            applicant = self.employee
            all_signatures = self.teleworksignature_set.all()
            has_employee_signature_0 = all_signatures.filter(employee=applicant, index=0).exists()
            has_employee_signature_1 = all_signatures.filter(employee=applicant, index=1).exists()
            if all([
                has_employee_signature_0,
                has_employee_signature_1,
                self.employee_fields_complete()
            ]):
                self.status = TeleworkApplication.READY_FOR_SIGNATURE
                self.save()

    def employee_fields_complete(self):
        completed_equipment_provided_other_value = True
        if self.equipment_provided_other and not self.equipment_provided_other_value:
            completed_equipment_provided_other_value = False

        completed_dependent_care_documentation = True
        if self.dependent_care_checklist_1 == TeleworkApplication.YES and not self.dependent_care_documentation:
            completed_dependent_care_documentation = False
        
        return all([
            bool(self.date),
            bool(self.hours_onsite),
            bool(self.telework_location),
            bool(self.hours_working),
            bool(self.duties),
            bool(self.communication_when),
            bool(self.communication_time),
            bool(self.communication_how),
            completed_equipment_provided_other_value,
            bool(self.workspace_checklist_1),
            bool(self.workspace_checklist_2),
            bool(self.workspace_checklist_3),
            bool(self.workspace_checklist_4),
            bool(self.workspace_checklist_5),
            bool(self.workspace_checklist_6),
            bool(self.workspace_checklist_7),
            bool(self.workspace_checklist_8),
            bool(self.workspace_checklist_9),
            bool(self.workspace_checklist_10),
            bool(self.workspace_checklist_11),
            bool(self.workspace_checklist_12),
            bool(self.emergency_checklist_1),
            bool(self.emergency_checklist_2),
            bool(self.emergency_checklist_3),
            bool(self.ergonomics_checklist_1),
            bool(self.ergonomics_checklist_2),
            bool(self.ergonomics_checklist_3),
            bool(self.ergonomics_checklist_4),
            bool(self.ergonomics_checklist_5),
            bool(self.dependent_care_checklist_1),
            completed_dependent_care_documentation
        ])

    def username(self):
        return self.employee.user.username

    def employee_signature(self, index):
        """
        (
            Signature index, Employee Role, Employee Name, Signature Date,
            Employee PK, Whether the Employee is ready to sign
        )
        """
        signature = TeleworkSignature.objects.filter(application=self, employee=self.employee, index=index).first()
        if signature:
            return[index, "Employee", signature.employee.name, signature.date, None, False] # Not ready to sign because there is a signature
        else:
            return [index, "Employee", None, None, self.employee.pk, True]

    def employee_signature_0(self):
        return self.employee_signature(0)

    def employee_signature_1(self):
        return self.employee_signature(1)

    def manager_ready_to_sign(self):
        if self.employee.manager:
            signature = TeleworkSignature.objects.filter(application=self, employee=self.employee.manager, index=0).first()
            return self.status == TeleworkApplication.READY_FOR_SIGNATURE and not signature
    
    def program_manager_ready_to_sign(self):
        if self.employee.has_program_manager:
            signature = TeleworkSignature.objects.filter(application=self, employee=self.employee.get_program_manager, index=0).first()
            return self.status == TeleworkApplication.READY_FOR_SIGNATURE and not signature
        else:
            return False

    def division_director_ready_to_sign(self):
        if self.employee.has_division_director:
            signature = TeleworkSignature.objects.filter(application=self, employee=self.employee.get_division_director, index=0).first()
            return self.status == TeleworkApplication.READY_FOR_SIGNATURE and not signature
        else:
            return False

    def manager_signed(self):
        if self.employee.manager:
            return TeleworkSignature.objects.filter(application=self, employee=self.employee.manager, index=0).count()

    def program_manager_signed(self):
        if self.employee.has_program_manager:
            return TeleworkSignature.objects.filter(application=self, employee=self.employee.get_program_manager, index=0).count()
    
    def division_director_signed(self):
        if self.employee.has_division_director:
            return TeleworkSignature.objects.filter(application=self, employee=self.employee.get_division_director, index=0).count()

    def manager_signature(self):
        signature = TeleworkSignature.objects.filter(application=self, employee=self.employee.manager, index=0).first()
        if signature:
            return[0, "Manager", signature.employee.name, signature.date, None, False] # Not ready to sign because there is a signature
        else:
            return [0, "Manager", None, None, self.employee.manager.pk, True]
    
    def program_manager_signature(self, index):
        # Rule out this being someone who does not ultimately report to a program manager
        if self.employee.is_division_director:
            return
        if self.employee.is_executive_director:
            return
        if self.employee.manager.is_division_director:
            return
        # TODO: HR people? Others?

        # Start by getting the program manager, which is the direct report of the division director
        current_employee = self.employee
        while True:
            if current_employee.is_executive_director:
                return
            if current_employee.manager and current_employee.manager.is_division_director:
                program_manager = current_employee
                break
            if current_employee.manager:
                current_employee = current_employee.manager
            else:
                # If we don't get to a division director somehow
                return
        signature = TeleworkSignature.objects.filter(application=self, employee=program_manager, index=index).first()
        if signature:
            return[index, "Program Manager", signature.employee.name, signature.date, None, False] # Not ready to sign because there is a signature
        else:
            return [index, "Program Manager", None, None, program_manager.pk, True]

    def program_manager_signature_0(self):
        return self.program_manager_signature(0)

    def program_manager_signature_1(self):
        return self.program_manager_signature(1)
    
    def division_director_signature(self):
        # Start by getting the division director
        current_employee = self.employee
        while True:
            if current_employee.is_division_director:
                director = current_employee
                break
            if current_employee.manager:
                current_employee = current_employee.manager
            else:
                # If we don't get to a division director somehow
                return
        signature = TeleworkSignature.objects.filter(application=self, employee=director, index=0).first()
        if signature:
            return[0, "Division Director", signature.employee.name, signature.date, None, False] # Not ready to sign because there is a signature
        else:
            return [0, "Division Director", None, None, director.pk, True]

class TeleworkSignature(models.Model):
    class Meta:
        verbose_name = _("Telework Signature")
        verbose_name_plural = _("Telework Signatures")

    def __str__(self):
        return f"{self.employee.name}'s approval of {self.application.employee.name}'s telework application"

    application = models.ForeignKey("people.TeleworkApplication", verbose_name=_("telework application"), on_delete=models.CASCADE)
    employee = models.ForeignKey("people.Employee", on_delete=models.CASCADE)
    index = models.SmallIntegerField(default=0)
    date = models.DateField(_("signature date"), auto_now=False, auto_now_add=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # Mark as ready for signature if it is complete and has employee signatures
        if self.application.status == TeleworkApplication.INCOMPLETE:
            applicant = self.application.employee
            all_signatures = self.application.teleworksignature_set.all()
            has_employee_signature_0 = all_signatures.filter(employee=applicant, index=0).exists()
            has_employee_signature_1 = all_signatures.filter(employee=applicant, index=1).exists()
            if all([
                has_employee_signature_0,
                has_employee_signature_1,
                self.application.employee_fields_complete()
            ]):
                self.application.status = TeleworkApplication.READY_FOR_SIGNATURE
                self.application.save()

        # Approve if all required signatures are present
        if self.application.status == TeleworkApplication.READY_FOR_SIGNATURE:
            approve_application = False
            applicant = self.application.employee
            all_signatures = self.application.teleworksignature_set.all()
            has_employee_signature_0 = all_signatures.filter(employee=applicant, index=0).exists()
            has_employee_signature_1 = all_signatures.filter(employee=applicant, index=1).exists()
            if has_employee_signature_0 and has_employee_signature_1:
                if applicant.manager:
                    has_manager_signature = all_signatures.filter(employee=self.application.employee.manager).exists()
                    if has_manager_signature:
                        if applicant.has_program_manager:
                            program_manager = applicant.get_program_manager
                            has_program_manager_signature_0 = all_signatures.filter(employee=program_manager, index=0).exists()
                            has_program_manager_signature_1 = all_signatures.filter(employee=program_manager, index=1).exists()
                            if has_program_manager_signature_0 and has_program_manager_signature_1:
                                if applicant.has_division_director:
                                    division_director = applicant.get_division_director
                                    has_division_director_signature = all_signatures.filter(employee=division_director).exists()
                                    if has_division_director_signature:
                                        # Application has all the required signatures, so approve
                                        approve_application = True
                                else:
                                    # Applicant has no division director but all the other required signatures, so approve
                                    approve_application = True
                        else:
                            # Applicant has no program manager but all the other required signatures, so approve
                            approve_application = True
                else:
                    # Applicant has no manager but all the other required signatures, so approve
                    approve_application = True
            
            if approve_application:
                self.application.status = TeleworkApplication.APPROVED
                self.application.save()


class Desk(models.Model):
    SCHAEFERS = 'S'
    PARK_PLACE = 'P'
    BUILDING_CHOICE = [
        (SCHAEFERS, 'Schaefers'),
        (PARK_PLACE, 'Park Place')
    ]

    class Meta:
        ordering = ["building", "floor", "number"]

    def __str__(self):
        return f"Desk: {self.get_building_display()} {self.floor}F #{self.number} "

    building = models.CharField(_("building"), max_length=1, choices=BUILDING_CHOICE, default=SCHAEFERS)
    floor = models.PositiveSmallIntegerField(default=1)
    number = models.CharField(max_length=10)
    active = models.BooleanField(default=True)
    lead = models.BooleanField(default=False)
    ergonomic = models.BooleanField(default=False)


class CurrentlyReservedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(check_out__isnull=True)


class DeskReservation(models.Model):
    class Meta:
        verbose_name = _("Desk Reservation")
        verbose_name_plural = _("Desk Reservations")
        # ordering = ["name"]
    
    def __str__(self):
        return f"Desk reservation for {self.employee.name}"

    objects = models.Manager()
    currently_reserved_objects = CurrentlyReservedManager()

    employee = models.ForeignKey("people.Employee", related_name="desk_reservations_old", on_delete=models.CASCADE)
    desk = models.ForeignKey("people.Desk", related_name="reservations_old", on_delete=models.CASCADE)
    check_in = models.DateTimeField(_("check-in datetime"), auto_now=False, auto_now_add=True)
    check_out = models.DateTimeField(_("check-out datetime"), null=True, auto_now=False, auto_now_add=False)