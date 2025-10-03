from datetime import datetime, timedelta, timezone
import json
import requests
import traceback

from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext as _

from mainsite.helpers import record_error
from mainsite.models import ActiveManager, InactiveManager, LANGUAGE_CHOICES
from people.middleware import get_current_employee
from people.models import Employee, JobTitle, UnitOrProgram


class HasTimeStampsMixin(models.Model):
    class Meta:
        abstract = True

    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)

    @property
    def duration(self):
        if self.completed_at:
            return self.completed_at - self.started_at
        else:
            return datetime.now(timezone.utc) - self.started_at


class HasCreatorMixin(models.Model):
    class Meta:
        abstract = True

    created_by = models.ForeignKey(
        Employee, blank=True, null=True, on_delete=models.SET_NULL
    )

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if not self.created_by:
            employee = get_current_employee()
            self.created_by = employee
            self.save()


class Role(models.Model):
    class Meta:
        ordering = ["name"]
    
    def __str__(self):
        return self.name

    name = models.CharField(max_length=100)
    description = models.CharField(max_length=300, blank=True)
    members = models.ManyToManyField(
        "people.Employee", related_name="workflow_roles", blank=True
    )


class EmployeeTransition(models.Model):
    TRANSITION_TYPE_NEW = 'New'
    TRANSITION_TYPE_RETURN = 'Return'
    TRANSITION_TYPE_NAME_CHANGE = 'Name Change'
    TRANSITION_TYPE_CHANGE = 'Change/Modify'
    TRANSITION_TYPE_EXIT = 'Exit'
    TRANSITION_TYPE_CHOICES = [
        (TRANSITION_TYPE_NEW, TRANSITION_TYPE_NEW),
        (TRANSITION_TYPE_RETURN, TRANSITION_TYPE_RETURN),
        (TRANSITION_TYPE_NAME_CHANGE, TRANSITION_TYPE_NAME_CHANGE),
        (TRANSITION_TYPE_CHANGE, TRANSITION_TYPE_CHANGE),
        (TRANSITION_TYPE_EXIT, TRANSITION_TYPE_EXIT)
    ]

    WORKER_TYPE_EMPLOYEE = 'Employee'
    WORKER_TYPE_INTERN = 'Intern'
    WORKER_TYPE_VOLUNTEER = 'Volunteer'
    WORKER_TYPE_TEMP_AGENCY = 'Temp Agency'
    WORKER_TYPE_TEMP_NON_AGENCY = 'Temp Non-Agency'
    WORKER_TYPE_CONTRACTOR = 'Contractor'
    WORKER_TYPE_CHOICES = [
        (WORKER_TYPE_EMPLOYEE, WORKER_TYPE_EMPLOYEE),
        (WORKER_TYPE_INTERN, WORKER_TYPE_INTERN),
        (WORKER_TYPE_VOLUNTEER, WORKER_TYPE_VOLUNTEER),
        (WORKER_TYPE_TEMP_AGENCY, WORKER_TYPE_TEMP_AGENCY),
        (WORKER_TYPE_TEMP_NON_AGENCY, WORKER_TYPE_TEMP_NON_AGENCY),
        (WORKER_TYPE_CONTRACTOR, WORKER_TYPE_CONTRACTOR)
    ]

    EMPLOYEE_ID_CLSD = 'CLSD'
    EMPLOYEE_ID_CLID = 'CLID'
    EMPLOYEE_ID_NONE = 'None/Non-Employee'
    EMPLOYEE_ID_CHOICES = [
        (EMPLOYEE_ID_CLSD, EMPLOYEE_ID_CLSD),
        (EMPLOYEE_ID_CLID, EMPLOYEE_ID_CLID),
        (EMPLOYEE_ID_NONE, EMPLOYEE_ID_NONE)
    ]

    LOCATION_COTTAGE_GROVE = 'Cottage Grove'
    LOCATION_FLORENCE = 'Florence'
    LOCATION_JUNCTION_CITY = 'Junction City'
    LOCATION_OAKRIDGE = 'Oakridge'
    LOCATION_PP1 = 'PPB - 1st Floor'
    LOCATION_PP4 = 'PPB - 4th Floor'
    LOCATION_PP5 = 'PPB - 5th Floor'
    LOCATION_SB = 'Schaefers - Basement'
    LOCATION_S1 = 'Schaefers - 1st Floor'
    LOCATION_S2 = 'Schaefers - 2nd Floor'
    LOCATION_S3 = 'Schaefers - 3rd Floor'
    LOCATION_SENIOR_MEALS = 'Senior Meals Site'
    LOCATION_VENETA = 'Veneta'
    LOCATION_CHOICES = [
        (LOCATION_COTTAGE_GROVE, LOCATION_COTTAGE_GROVE),
        (LOCATION_FLORENCE, LOCATION_FLORENCE),
        (LOCATION_JUNCTION_CITY, LOCATION_JUNCTION_CITY),
        (LOCATION_OAKRIDGE, LOCATION_OAKRIDGE),
        (LOCATION_PP1, LOCATION_PP1),
        (LOCATION_PP4, LOCATION_PP4),
        (LOCATION_PP5, LOCATION_PP5),
        (LOCATION_SB, LOCATION_SB),
        (LOCATION_S1, LOCATION_S1),
        (LOCATION_S2, LOCATION_S2),
        (LOCATION_S3, LOCATION_S3),
        (LOCATION_SENIOR_MEALS, LOCATION_SENIOR_MEALS),
        (LOCATION_VENETA, LOCATION_VENETA),   
    ]

    UNION_NON_REPRESENTED = 'Non-Represented'
    UNION_EA = 'EA'
    UNION_SEIU = 'SEIU'
    UNION_SENIOR_MEALS = 'Senior Meals'
    UNION_MANAGEMENT = 'Management'
    UNION_CHOICES = [
        (UNION_NON_REPRESENTED, UNION_NON_REPRESENTED),
        (UNION_EA, UNION_EA),
        (UNION_SEIU, UNION_SEIU),
        (UNION_SENIOR_MEALS, UNION_SENIOR_MEALS),
        (UNION_MANAGEMENT, UNION_MANAGEMENT)
    ]

    COMPUTER_TYPE_NEW = 'New'
    COMPUTER_TYPE_REPURPOSED = 'Repurposed'
    COMPUTER_TYPE_CHOICES = [
        (COMPUTER_TYPE_NEW, COMPUTER_TYPE_NEW),
        (COMPUTER_TYPE_REPURPOSED, COMPUTER_TYPE_REPURPOSED),
    ]

    PHONE_REQUEST_NEW = 'New number needed'
    PHONE_REQUEST_REMOVE = 'Remove phone'
    PHONE_REQUEST_DELETE_NUM = 'Delete number'
    PHONE_REQUEST_REASSIGN = 'Reassign to:'
    PHONE_REQUEST_CHANGE = 'Change name display to:'
    PHONE_REQUEST_DELETE_VM = 'Delete voicemail box'
    PHONE_REQUEST_CHOICES = [
        (PHONE_REQUEST_NEW, PHONE_REQUEST_NEW),
        (PHONE_REQUEST_REMOVE, PHONE_REQUEST_REMOVE),
        (PHONE_REQUEST_DELETE_NUM, PHONE_REQUEST_DELETE_NUM),
        (PHONE_REQUEST_REASSIGN, PHONE_REQUEST_REASSIGN),
        (PHONE_REQUEST_CHANGE, PHONE_REQUEST_CHANGE),
        (PHONE_REQUEST_DELETE_VM, PHONE_REQUEST_DELETE_VM)
    ]

    OREGON_ACCESS_NONE = 'Not needed'
    OREGON_ACCESS_DESKTOP = 'Desktop'
    OREGON_ACCESS_REMOTE = 'Remote'
    OREGON_ACCESS_CHOICES = [
        (OREGON_ACCESS_NONE, OREGON_ACCESS_NONE),
        (OREGON_ACCESS_DESKTOP, OREGON_ACCESS_DESKTOP),
        (OREGON_ACCESS_REMOTE, OREGON_ACCESS_REMOTE)
    ]

    ASSIGNEE_NONE = 'None'
    ASSIGNEE_SUBMITTER = 'Submitter'
    ASSIGNEE_HIRING_LEAD = 'Hiring Lead'
    ASSIGNEE_FISCAL = 'Fiscal'
    ASSIGNEE_HR = 'HR'
    ASSIGNEE_COMPLETE = 'Complete'
    ASSIGNEE_CHOICES = [
        (ASSIGNEE_NONE, ASSIGNEE_NONE),
        (ASSIGNEE_SUBMITTER, ASSIGNEE_SUBMITTER),
        (ASSIGNEE_HIRING_LEAD, ASSIGNEE_HIRING_LEAD),
        (ASSIGNEE_FISCAL, ASSIGNEE_FISCAL),
        (ASSIGNEE_HR, ASSIGNEE_HR),
        (ASSIGNEE_COMPLETE, ASSIGNEE_COMPLETE)
    ]

    class Meta:
        ordering = ["pk"]

    def __str__(self):
        if self.transition_date:
            date = datetime.strftime(self.transition_date, '%m/%d/%Y')
        else:
            date = "No date"
        return "EmployeeTransition ({}): {} - {}".format(
            self.pk, self.title, date
        )

    type = models.CharField(
        _("transition type"), max_length=20, choices=TRANSITION_TYPE_CHOICES,
        blank=True, null=True
    )
    worker_type = models.CharField(
        _("worker type"), max_length=15, choices=WORKER_TYPE_CHOICES,
        default=WORKER_TYPE_EMPLOYEE
    )
    # TODO: What does this mean now? Currently submitter and date are set only
    # the first time the transition is saved.
    date_submitted = models.DateTimeField(blank=True, null=True)
    submitter = models.ForeignKey(
        Employee, blank=True, null=True, on_delete=models.SET_NULL,
        related_name="submitter_of_transitions"
    )
    current_employee = models.ForeignKey(
        Employee, blank=True, null=True, on_delete=models.SET_NULL,
        related_name="current_employee_of_transitions"
    )
    employee_first_name = models.CharField(blank=True, max_length=50)
    employee_middle_initial = models.CharField(blank=True, max_length=5)
    employee_last_name = models.CharField(blank=True, max_length=50)
    employee_preferred_name = models.CharField(blank=True, max_length=100)
    employee_number = models.PositiveSmallIntegerField(blank=True, null=True)
    employee_id = models.CharField(
        blank=True, max_length=17, choices=EMPLOYEE_ID_CHOICES
    )
    employee_email = models.EmailField(blank=True)
    title = models.ForeignKey(
        JobTitle, blank=True, null=True, on_delete=models.SET_NULL
    )
    fte = models.FloatField(blank=True, default=1.0)
    hours_per_week = models.FloatField(blank=True, default=0)
    hourly_rate = models.DecimalField(
        blank=True, null=True, max_digits=10, decimal_places=2
    )
    salary_range = models.DecimalField(
        blank=True, null=True, max_digits=10, decimal_places=2
    )
    salary_step = models.PositiveSmallIntegerField(blank=True, null=True)
    stipend = models.CharField(
        blank=True, max_length=100, help_text=_("e.g. $500/month")
    )
    bilingual = models.BooleanField(default=False)
    second_language = models.CharField(
        max_length=20, choices=LANGUAGE_CHOICES, blank=True
    )
    manager = models.ForeignKey(
        Employee, blank=True, null=True, on_delete=models.SET_NULL,
        related_name="manager_of_transitions"
    )
    unit = models.ForeignKey(
        UnitOrProgram, blank=True, null=True, on_delete=models.SET_NULL
    )
    transition_date = models.DateTimeField(blank=True, null=True)
    system_change_date = models.DateTimeField(blank=True, null=True)
    lwop = models.BooleanField(default=False)
    lwop_details = models.TextField(blank=True, null=True)
    preliminary_hire = models.BooleanField(default=False)
    delete_profile = models.BooleanField(default=False)
    # Weekly schedule string (U=Tuesday, H=Thursday) e.g. MUWF is no Thursdays
    schedule = models.CharField(max_length=5, blank=True)
    office_location = models.CharField(
        max_length=30, choices=LOCATION_CHOICES, blank=True
    )
    cubicle_number = models.CharField(
        max_length=10, blank=True, null=True
    )
    union_affiliation = models.CharField(
        max_length=20, choices=UNION_CHOICES, blank=True
    )
    teleworking = models.BooleanField(default=False)
    computer_type = models.CharField(
        max_length=10, choices=COMPUTER_TYPE_CHOICES, blank=True
    )
    computer_gl = models.CharField(max_length=30, blank=True)
    computer_description = models.CharField(max_length=200, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    phone_request = models.CharField(
        max_length=30, choices=PHONE_REQUEST_CHOICES, blank=True
    )
    phone_request_data = models.CharField(max_length=50, blank=True)
    load_code = models.CharField(max_length=50, blank=True)
    cell_phone = models.BooleanField(default=False)
    should_delete = models.BooleanField(default=False)
    reassign_to = models.CharField(max_length=50, blank=True)
    gas_pin_needed = models.BooleanField(_("Gas PIN needed"), default=False)
    oregon_access = models.CharField(
        default=OREGON_ACCESS_NONE, max_length=10,
        choices=OREGON_ACCESS_CHOICES
    )
    business_cards = models.BooleanField(default=False)
    prox_card_needed = models.BooleanField(default=False)
    mailbox_needed = models.BooleanField(default=False)
    access_emails = models.ForeignKey(
        Employee, blank=True, null=True, on_delete=models.SET_NULL,
        related_name="access_emails_after_transitions"
    )
    special_instructions = models.TextField(blank=True)
    fiscal_field = models.TextField(blank=True)

    assignee = models.CharField(
        max_length=100, choices=ASSIGNEE_CHOICES, default=ASSIGNEE_NONE
    )

    __original_values = {}

    @property
    def is_sds(self):
        return self.employee_id == self.EMPLOYEE_ID_CLSD

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__original_values = self.__dict__.copy()
        # self.__original_values["date_submitted"] = json.dumps(self.date_submitted)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        original = self.__original_values
        new = self.__dict__.copy()
        # Creata a change record
        changes = {}
        for field in self._meta.fields:
            if field.name in ["id", "date_submitted", "submitter"]:
                continue
            if field.name == 'transition_date' and new[field.name]:
                original_date = original[field.name]
                new_date = new[field.name]
                # When coming from the form, the date is a string
                if type(new_date) == str:
                    new_date = datetime.strptime(
                        new_date, '%Y-%m-%dT%H:%M:%S.%fZ'
                    ).replace(tzinfo=timezone.utc)
                # Strip microseconds from timestamps
                new_date -= timedelta(microseconds=new_date.microsecond)
                if original_date:
                    original_date -= timedelta(
                        microseconds=original_date.microsecond
                    )
                # Do not create a change record if the date has not changed
                if original_date == new_date:
                    continue
                # String representation of the date
                original_value = str(original_date)
                new_value = str(new_date)
            elif field.name == 'system_change_date' and new[field.name]:
                original_date = original[field.name]
                new_date = new[field.name]
                # When coming from the form, the date is a string
                if type(new_date) == str:
                    new_date = datetime.strptime(
                        new_date, '%Y-%m-%dT%H:%M:%S.%fZ'
                    ).replace(tzinfo=timezone.utc)
                # Strip microseconds from timestamps
                new_date -= timedelta(microseconds=new_date.microsecond)
                if original_date:
                    original_date -= timedelta(
                        microseconds=original_date.microsecond
                    )
                # Do not create a change record if the date has not changed
                if original_date == new_date:
                    continue
                # String representation of the date
                original_value = str(original_date)
                new_value = str(new_date)
            else:
                original_value = original[field.column]
                new_value = new[field.column]
            if original_value != new_value:
                changes[field.name] = {
                    "original": original_value,
                    "new": new_value,
                }
        if len(changes):
            json_changes = json.dumps(changes, sort_keys=True, default=str)
            employee = get_current_employee()
            TransitionChange.objects.create(
                transition=self, created_by=employee,
                changes=json_changes
            )

    def employee_action_required(self, employee):
        # Return True if the employee is responsible for reviewing the form
        assignee = self.assignee
        if assignee in [self.ASSIGNEE_NONE, self.ASSIGNEE_COMPLETE]:
            return False
        elif assignee == self.ASSIGNEE_SUBMITTER:
            if self.submitter == employee:
                return True
        elif assignee == self.ASSIGNEE_HIRING_LEAD:
            return employee.is_sds_hiring_lead
        elif assignee == self.ASSIGNEE_FISCAL:
            return employee.is_fiscal_employee
        elif assignee == self.ASSIGNEE_HR:
            return employee.is_hr_employee
        return False


class TransitionChange(HasCreatorMixin):
    """
    A change record for a transition.
    """
    class Meta:
        ordering = ["pk"]

    transition = models.ForeignKey(
        EmployeeTransition, blank=True, null=True, on_delete=models.CASCADE,
        related_name="changes"
    )
    date = models.DateTimeField(auto_now_add=True)
    changes = models.JSONField()


class Workflow(models.Model):
    """
    A high-level workflow, e.g. new employee onboarding.
    """
    class Meta:
        ordering = ["pk"]
    
    def __str__(self):
        return f"Workflow: {self.name}"
    
    name = models.CharField(
        max_length=100, help_text=_("Display name of the workflow")
    )
    type = models.CharField(
        max_length=100, blank=True,
        help_text=_("Short name for the type of workflow, e.g. new, exit")
    )
    role = models.ForeignKey(
        Role, blank=True, null=True, on_delete=models.SET_NULL,
        help_text=_(
            "The set of employees with full admin access to this workflow"
        )
    )
    icon = models.CharField(
        max_length=50, blank=True,
        help_text=_("The name of a Material Design icon")
    )
    version = models.IntegerField(default=1)

    # TODO: Complete when all child processes are complete


class Process(models.Model):
    """
    A process within a workflow with a definite start and end. May be done in
    parallel with one another.
    e.g. HR and IS processes for new employee onboarding
    """
    def __str__(self):
        return f"Process: {self.name} v{self.version}"

    class Meta:
        verbose_name_plural = _("Processes")
    
    name = models.CharField(max_length=100)
    workflow = models.ForeignKey(
        Workflow, related_name="processes", on_delete=models.CASCADE
    )
    workflow_start = models.BooleanField(
        default=False,
        help_text=_("Start this process when a workflow begins.")
    )
    role = models.ForeignKey(
        Role, blank=True, null=True, on_delete=models.SET_NULL,
        help_text=_(
            "The set of employees with full admin access to this process"
        )
    )
    version = models.IntegerField(default=1)

    @property
    def total_steps(self):
        # Count the number of steps before the final one. Don't count the final
        # step because it is the "complete" step and cannot be completed.
        return self.steps.filter(end=True).first().num_steps_before

    # def save(self, *args, **kwargs):
    #     super().save(*args, **kwargs)
    #     # If a Process has any Steps, it must have exactly one start Step and
    #     # one end Step.
    #     if self.steps.count():
    #         if self.steps.filter(start=True).count() != 1:
    #             raise ValidationError("A process must have exactly one start step.")
    #         if self.steps.filter(end=True).count() != 1:
    #             raise ValidationError("A process must have exactly one end step.")

    # TODO: Get this working either here or on the Step class
    # def clean(self):
    #     # If a Process has any Steps, it must have exactly one start Step and
    #     # one end Step.
    #     if (self.pk):
    #         if self.steps.count():
    #             if self.steps.filter(start=True).count() == 0:
    #                 self.steps.first().start = True
    #                 self.save()
    #             if self.steps.filter(end=True).count() == 0:
    #                 self.steps.last().end = True
    #                 self.save()

    def create_process_instance(self, wfi):
        pi = ProcessInstance.objects.create(
            process=self, workflow_instance=wfi
        )
        first_step = self.steps.filter(start=True)[0]
        si = StepInstance.objects.create(step=first_step, process_instance=pi)
        from workflows.helpers import send_step_completion_email
        send_step_completion_email(si)
        pi.current_step_instance = si
        pi.save()
    
    def delete_process_instances(self, wfi):
        pis = ProcessInstance.objects.filter(
            process=self, workflow_instance=wfi
        )
        for pi in pis:
            pi.delete()

    #TODO: Complete when step marked "end" is completed
    #TODO: On save, make sure there is a start and end step if there are any steps


class Action(models.Model):
    LINK = 'LINK'
    API = 'API'
    EMAIL = 'EMAIL'
    ACTION_TYPE_CHOICES = [
        (LINK, 'Navigate to Link'),
        (API, 'Make API call'),
        (EMAIL, 'Send an email'),
    ]
    
    type = models.CharField(
        _("action type"), max_length=5, choices=ACTION_TYPE_CHOICES,
        blank=True, null=True
    )
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=300, blank=True)
    # Url need not be valid, for internal URLs
    url = models.CharField(max_length=300, blank=True)

    def __str__(self):
        return self.name

    def clean(self):
        # A link must have a URL
        if self.type == self.LINK and not self.url:
            raise ValidationError("A link must have a URL")
        elif self.type == self.API:
            # TODO
            pass
        elif self.type == self.EMAIL:
            # TODO
            pass
    
    def trigger(self):
        if self.type == self.LINK:
            # TODO
            pass
        elif self.type == self.API:
            # Make an http request to the url
            response = requests.get(self.url)
            import pdb; pdb.set_trace()
        elif self.type == self.EMAIL:
            # TODO
            pass


class Step(models.Model):
    def __str__(self):
        return f"{self.order} - {self.name}"

    process = models.ForeignKey(
        Process, related_name="steps", on_delete=models.CASCADE
    )
    order = models.IntegerField(
        help_text=_("Display order in admin Process detail"), default=0
    )
    start = models.BooleanField(default=False)
    end = models.BooleanField(default=False)
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=300, blank=True)
    role = models.ForeignKey(
        Role, blank=True, null=True, on_delete=models.SET_NULL,
        help_text=_(
            "The set of employees responsible for completing this step"
        )
    )
    next_step = models.ForeignKey(
        "self", blank=True, null=True, on_delete=models.SET_NULL,
        help_text=_("The next step, when there is only one")
    )
    choices_prompt = models.CharField(
        max_length=200, blank=True,
        help_text=_("The prompt for when there are multiple next step choices")
    )
    trigger_processes = models.ManyToManyField(
        Process, related_name="triggering_steps", blank=True
    )
    completion_action = models.ForeignKey(
        Action, blank=True, null=True, on_delete=models.SET_NULL,
        help_text=_("Action to trigger as this step completes")
    )
    optional_actions = models.ManyToManyField(
        Action, blank=True, related_name="triggering_steps"
    )

    # TODO: On save, make sure there is only one start and end step for a given process

    # TODO: These checks are not working with StepInline readonly_fields
    # def clean(self):
    #     # A process can only have one start and one end step
    #     if self.start and self.process.steps.filter(start=True).count() > 1:
    #         raise ValidationError("A process can't have more than one start step.")
    #     if self.end and self.process.steps.filter(end=True).count() > 1:
    #         raise ValidationError("A process can't have more than one end step.")
        
    #     # TODO: Implement check for infinite loops?
    #     if self.next_step == self:
    #         raise ValidationError("A step can't be its own next step.")

    @property
    def members(self):
        if self.role and self.role.members.count():
            return self.role.members.all()
        else:
            return None

    @property
    def num_steps_before(self):
        """
        Count the number of steps before the current step. Since there are
        multiple possible paths to the beginning of a process, just get one
        route back and call that sufficient.
        TODO: Rewrite to calculate the best-case (quickest) path back (or worst
        case, or average of all cases)
        """
        num_steps = 0
        current_step = self
        while True:
            if current_step.start == True:
                # We have reached the beginning of the process.
                break
            else:
                # Here we just get the first previous step we can
                previous_step = Step.objects.filter(
                    next_step=current_step
                ).first()
                if not previous_step:
                    # In the case of a choice, there is no next step, so find
                    # the step that leads to this one with choices.
                    step_choice = StepChoice.objects.filter(
                        next_step=current_step
                    ).first()
                    previous_step = step_choice.step
                if not previous_step:
                    raise Exception("Couldn't find a previous step.")
                # Move back one step
                current_step = previous_step
                num_steps += 1
        return num_steps

    @property
    def num_steps_after(self):
        """
        Count the number of steps after the current step. Since there are
        multiple possible paths to the end of a process, just get one route
        forward and call that sufficient.
        TODO: Rewrite to calculate the best-case (quickest) path forward (or
        worst case, or average of all cases)
        """
        num_steps = 0
        current_step = self
        while True:
            if current_step.end == True:
                # We have reached the end of the process.
                break
            else:
                # Look for the next step
                if current_step.next_step:
                    current_step = current_step.next_step
                else:
                    # In the case of a choice, there is no next step, so find
                    # the first choice that leads to a step.
                    step_choice = StepChoice.objects.filter(
                        step=current_step
                    ).first()
                    if not step_choice:
                        m = "Couldn't find a next step."
                        record_error(m, None, None, traceback.format_exc())
                        raise Exception(m)
                    current_step = step_choice.next_step
                num_steps += 1
        return num_steps

    #TODO: On save, error if no next and not end
    #TODO: Properties for next step, previous step, is first step and is last step


class StepChoice(models.Model):
    step = models.ForeignKey(
        Step, related_name="next_step_choices", on_delete=models.CASCADE
    )
    order = models.IntegerField(
        help_text=_("Display order in admin Step detail"), default=0
    )
    choice_text = models.CharField(max_length=100)
    next_step = models.ForeignKey(
        Step, blank=True, null=True, on_delete=models.SET_NULL
    )
    trigger_processes = models.ManyToManyField(
        Process, related_name="triggering_step_choices", blank=True
    )


class WorkflowInstance(HasTimeStampsMixin, HasCreatorMixin):
    class Meta:
        ordering = ["pk"]

    def __str__(self):
        return "WorkflowInstance ({}): {}".format(self.pk, self.workflow)

    objects = models.Manager()
    active_objects = ActiveManager()
    inactive_objects = InactiveManager()

    workflow = models.ForeignKey(Workflow, on_delete=models.CASCADE)
    transition = models.OneToOneField(
        EmployeeTransition, blank=True, null=True, on_delete=models.SET_NULL
    )
    active = models.BooleanField(default=True)
    complete = models.BooleanField(default=False)
    percent_complete = models.IntegerField(default=0)
    
    @property
    def employee_name(self):
        if self.transition:
            return f'{self.transition.employee_first_name} {self.transition.employee_last_name}'
    
    @property
    def title(self):
        if self.transition:
            return self.transition.title
    
    @property
    def transition_date(self):
        if self.transition:
            return self.transition.transition_date
        
    def pis_action_required(self, employee):
        # True if any of the process instances require action from the employee
        return any(
            pi.employee_action_required(employee) for
            pi in self.pis.all()
        )
    
    def transition_action_required(self, employee):
        # True if the transition requires action from the employee
        return self.transition.employee_action_required(employee) if \
            self.transition else False

    def employee_action_required(self, employee):
        return self.pis_action_required(employee) or \
            self.transition_action_required(employee)
    
    def delete(self, *args, **kwargs):
        # Delete any employee transitions
        if self.transition:
            self.transition.delete()
        super().delete(*args, **kwargs)
    
    def update_percent_complete(self):
        pis = self.pis.all()
        total_steps = sum([pi.total_steps for pi in pis])
        if total_steps == 0:
            self.percent_complete = 0
        else:
            complete_steps = sum([pi.complete_steps for pi in pis])
            self.percent_complete = int((complete_steps / total_steps) * 100)
        # Trigger completion if all process instances are complete.
        # If stepping backwards, mark incomplete.
        if self.percent_complete == 100:
            self.completed_at = datetime.now(timezone.utc)
            self.complete = True
        elif self.complete:
            self.completed_at = None
            self.complete = False
        self.save()


class ProcessInstance(HasTimeStampsMixin):
    class Meta:
        ordering = ["pk"]

    def __str__(self):
        return "ProcessInstance ({}): {}".format(self.pk, self.process)
    
    process = models.ForeignKey("workflows.Process", on_delete=models.CASCADE)
    workflow_instance = models.ForeignKey(
        WorkflowInstance, on_delete=models.CASCADE, related_name="pis"
    )
    current_step_instance = models.ForeignKey(
        "workflows.StepInstance", blank=True, null=True,
        on_delete=models.SET_NULL
    )
    percent_complete = models.IntegerField(default=0)

    @property
    def total_steps(self):
        return self.process.total_steps
    
    @property
    def complete_steps(self):
        if not self.current_step_instance:
            return self.total_steps
        else:
            return self.current_step_instance.step.num_steps_before

    def employee_action_required(self, employee):
        # True if the employee is responsible for completing the current step
        if not self.current_step_instance:
            # TODO: This should not happen; maybe log an error
            return False
        return self.current_step_instance.employee_action_required(employee)

    def update_percent_complete(self):
        if not self.current_step_instance:
            self.percent_complete = 100
        else:
            num_steps_before = self.current_step_instance.step.num_steps_before
            num_steps_after = self.current_step_instance.step.num_steps_after
            # Add the steps before, the current step, and the steps after, but
            # subtract one because the final step is the "complete" step and
            # cannot be completed.
            total_steps = num_steps_before + 1 + num_steps_after - 1
            if total_steps == 0:
                self.percent_complete = 0
            else:
                self.percent_complete = int(
                    (num_steps_before / total_steps) * 100
                )
        # Trigger completion. If stepping backwards, mark incomplete.
        if self.percent_complete == 100:
            self.completed_at = datetime.now(timezone.utc)
        elif self.completed_at != None:
            self.completed_at = None
        self.save()


class StepInstance(HasTimeStampsMixin):
    class Meta:
        ordering = ["pk"]

    def __str__(self):
        return "StepInstance ({}): {}".format(self.pk, self.step)
    
    step = models.ForeignKey(Step, on_delete=models.CASCADE)
    process_instance = models.ForeignKey(
        ProcessInstance, on_delete=models.CASCADE
    )
    completed_by = models.ForeignKey(
        "people.Employee", blank=True, null=True, on_delete=models.SET_NULL
    )

    @property
    def is_complete(self):
        return bool(self.completed_by)

    @property
    def undo_completion_possible(self):
        if self.step.next_step:
            # If there is a next step, we can undo if it is incomplete
            return self.step.next_step.stepinstance_set.filter(
                process_instance=self.process_instance,
                completed_at__isnull=True
            ).exists()
        else:
            choices = self.step.next_step_choices.all()
            if choices.count():
                # If there are next step choices, we can undo if none of the
                # next steps are complete
                return StepInstance.objects.filter(
                    step__in=[choice.next_step for choice in choices],
                    process_instance=self.process_instance,
                    completed_at__isnull=False
                ).count() == 0
            else:
                # If there is no next step, we can undo
                return True

    #TODO: Complete method fills completed_at, completed_by, and current_step_instance and completed_at on Workflow instance. This is currently done in the view, but maybe it should be here?

    def employee_action_required(self, employee):
        # Return True if the employee is responsible for completing this step
        if self.step.role:
            return employee.workflow_roles.filter(
                pk=self.step.role.pk
            ).count() > 0
        return False