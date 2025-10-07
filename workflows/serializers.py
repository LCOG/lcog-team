from rest_framework import serializers

from workflows.models import (
    Action, EmployeeTransition, Process, ProcessInstance, Role, Step,
    StepChoice, StepInstance, TransitionChange, Workflow, WorkflowInstance
)


class RoleSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Role
        fields = ['url', 'pk', 'name', 'description', 'member_names']
    
    member_names = serializers.SerializerMethodField()

    @staticmethod
    def get_member_names(role):
        names = role.members.values_list('user__first_name', 'user__last_name')
        return [f'{first} {last}' for first, last in names]


class StepChoiceSerializer(serializers.HyperlinkedModelSerializer):
    next_step_pk = serializers.IntegerField(source="next_step.pk")
    trigger_processes_pks = serializers.SerializerMethodField()
    
    class Meta:
        model = StepChoice
        fields = '__all__'
        fields = [
            'pk', 'order', 'choice_text', 'step', 'next_step', 'next_step_pk',
            'trigger_processes_pks'
        ]

    @staticmethod
    def get_trigger_processes_pks(stepchoice):
        return [process.pk for process in stepchoice.trigger_processes.all()]


class ActionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Action
        fields = '__all__'


class StepSerializer(serializers.HyperlinkedModelSerializer):
    next_step_choices = StepChoiceSerializer(many=True)
    role = RoleSerializer()
    process_role_pk = serializers.SerializerMethodField()
    workflow_role_pk = serializers.SerializerMethodField()
    completion_action = ActionSerializer()
    optional_actions = ActionSerializer(many=True)
    
    class Meta:
        model = Step
        fields = [
            'url', 'pk', 'order', 'start', 'end', 'name', 'description',
            'choices_prompt', 'role', 'next_step', 'next_step_choices',
            'process_role_pk', 'workflow_role_pk', 'completion_action',
            'optional_actions'
        ]
    
    @staticmethod
    def get_process_role_pk(step):
        return step.process.role.pk if step.process.role else None
    
    @staticmethod
    def get_workflow_role_pk(step):
        return step.process.workflow.role.pk if step.process.workflow.role else None


class ProcessSerializer(serializers.ModelSerializer):
    steps = StepSerializer(many=True)
    
    class Meta:
        model = Process
        fields = [
            'url', 'pk', 'name', 'version', 'steps'
        ]


class WorkflowSerializer(serializers.HyperlinkedModelSerializer):
    processes = ProcessSerializer(many=True)

    class Meta:
        model = Workflow
        fields = [
            'url', 'pk', 'name', 'type', 'icon', 'version', 'processes'
        ]


class StepInstanceSerializer(serializers.ModelSerializer):
    step = StepSerializer(required=False)
    completed_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = StepInstance
        fields = [
            'url', 'pk', 'started_at', 'completed_at', 'step', 'completed_by',
            'completed_by_name', 'undo_completion_possible'
        ]
    
    @staticmethod
    def get_completed_by_name(stepinstance):
        if stepinstance.completed_by:
            return stepinstance.completed_by.name
        else:
            return None


class ProcessInstanceSerializer(serializers.ModelSerializer):
    step_instances = StepInstanceSerializer(source='stepinstance_set',
        many=True)
    current_step_instance = StepInstanceSerializer()
    action_required = serializers.SerializerMethodField()

    class Meta:
        model = ProcessInstance
        fields = [
            'url', 'pk', 'process', 'step_instances', 'current_step_instance',
            'completed_at', 'percent_complete', 'action_required'
        ]
        depth = 1
    
    def get_action_required(self, pi):
        user = None
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            user = request.user
        if user and hasattr(user, "employee"):
            return pi.employee_action_required(user.employee)
        return False


class TransitionChangeSerializer(serializers.ModelSerializer):
    created_by_name = serializers.SerializerMethodField()
    created_by_initials = serializers.SerializerMethodField()

    class Meta:
        model = TransitionChange
        fields = [
            'url', 'pk', 'transition', 'date', 'created_by',
            'created_by_name', 'created_by_initials', 'changes'
        ]
    
    @staticmethod
    def get_created_by_name(transitionchange):
        if transitionchange.created_by:
            return transitionchange.created_by.name
        else:
            return None

    @staticmethod
    def get_created_by_initials(transitionchange):
        if transitionchange.created_by:
            return transitionchange.created_by.initials
        else:
            return None


class EmployeeTransitionSerializer(serializers.ModelSerializer):
    submitter_pk = serializers.CharField(source='submitter.pk', required=False)
    submitter_name = serializers.CharField(
        source='submitter.name', required=False
    )
    submitter_division = serializers.CharField(
        source='submitter.unit_or_program.division.name', required=False
    )
    current_employee_pk = serializers.SerializerMethodField()
    current_employee_name = serializers.SerializerMethodField()
    title_pk = serializers.SerializerMethodField()
    title_name = serializers.SerializerMethodField()
    manager_pk = serializers.SerializerMethodField()
    manager_name = serializers.SerializerMethodField()
    unit_pk = serializers.SerializerMethodField()
    unit_name = serializers.SerializerMethodField()
    access_emails_pk = serializers.SerializerMethodField()
    access_emails_name = serializers.SerializerMethodField()
    changes = TransitionChangeSerializer(many=True)

    class Meta:
        model = EmployeeTransition
        fields = [
            'url', 'pk', 'type', 'worker_type', 'date_submitted',
            'submitter_pk', 'submitter_name', 'submitter_division',
            'current_employee_pk', 'current_employee_name',
            'employee_first_name', 'employee_middle_initial',
            'employee_last_name', 'employee_preferred_name', 'employee_number',
            'employee_id', 'employee_email', 'title_pk', 'title_name', 'fte',
            'hours_per_week', 'hourly_rate', 'salary_range', 'salary_step',
            'stipend', 'bilingual', 'second_language', 'manager_pk',
            'manager_name', 'unit_pk', 'unit_name', 'transition_date',
            'system_change_date', 'schedule', 'lwop', 'lwop_details',
            'preliminary_hire', 'delete_profile', 'office_location',
            'cubicle_number', 'union_affiliation', 'teleworking',
            'computer_type', 'computer_gl', 'computer_description',
            'phone_number', 'phone_request', 'phone_request_data', 'load_code',
            'cell_phone', 'should_delete', 'extension_remain_active',
            'reassign_to', 'gas_pin_needed', 'oregon_access', 'business_cards',
            'prox_card_needed', 'mailbox_needed', 'access_emails_pk',
            'access_emails_name', 'special_instructions', 'fiscal_field',
            'assignee', 'changes'
        ]

    @staticmethod
    def get_current_employee_pk(transition):
        if transition.current_employee:
            return transition.current_employee.pk
        else:
            return -1

    @staticmethod
    def get_current_employee_name(transition):
        if transition.current_employee:
            return transition.current_employee.legal_name
        else:
            return ''

    @staticmethod
    def get_manager_pk(transition):
        if transition.manager:
            return transition.manager.pk
        else:
            return -1

    @staticmethod
    def get_manager_name(transition):
        if transition.manager:
            return transition.manager.legal_name
        else:
            return ''
    
    @staticmethod
    def get_title_pk(transition):
        if transition.title:
            return transition.title.pk
        else:
            return -1

    @staticmethod
    def get_title_name(transition):
        if transition.title:
            if transition.title.name:
                return transition.title.name
            else:
                return ''

    @staticmethod
    def get_unit_pk(transition):
        if transition.unit:
            return transition.unit.pk
        else:
            return -1

    @staticmethod
    def get_unit_name(transition):
        if transition.unit:
            if transition.unit.name:
                return f'{transition.unit.division.name} - {transition.unit.name}'
            else:
                return transition.unit.division.name
        else:
            return ''
    
    @staticmethod
    def get_access_emails_pk(transition):
        if transition.access_emails:
            return transition.access_emails.pk
        else:
            return -1

    @staticmethod
    def get_access_emails_name(transition):
        if transition.access_emails:
            return transition.access_emails.name
        else:
            return ''


class EmployeeTransitionRedactedSerializer(EmployeeTransitionSerializer):
    """
    Same as the regular serializer but leave out sensitive fields: hourly_rate,
    salary_range, and salary_step.
    """
    class Meta:
        model = EmployeeTransition
        fields = [
            'url', 'pk', 'type', 'worker_type', 'date_submitted',
            'submitter_pk', 'submitter_name', 'submitter_division',
            'employee_first_name', 'employee_middle_initial',
            'employee_last_name', 'employee_preferred_name', 'employee_number',
            'employee_id', 'employee_email', 'title_pk', 'title_name', 'fte',
            'hours_per_week', 'bilingual', 'second_language', 'manager_pk',
            'manager_name', 'unit_pk', 'unit_name', 'transition_date',
            'system_change_date', 'lwop', 'lwop_details', 'preliminary_hire',
            'delete_profile', 'office_location', 'cubicle_number',
            'union_affiliation', 'teleworking', 'computer_type', 'computer_gl',
            'computer_description', 'phone_number', 'phone_request',
            'phone_request_data', 'load_code', 'cell_phone', 'should_delete',
            'extension_remain_active', 'reassign_to', 'gas_pin_needed',
            'oregon_access', 'business_cards', 'prox_card_needed',
            'mailbox_needed', 'access_emails_pk', 'access_emails_name',
            'special_instructions', 'changes'
        ]

class WorkflowInstanceBaseSerializer(serializers.ModelSerializer):
    title_name = serializers.SerializerMethodField()
    employee_action_required = serializers.SerializerMethodField()
    pis_action_required = serializers.SerializerMethodField()
    transition_action_required = serializers.SerializerMethodField()
    workflow_type = serializers.CharField(source='workflow.type')
    workflow_name = serializers.SerializerMethodField()
    workflow_role_pk = serializers.IntegerField(
        source='workflow.role.pk', required=False
    )

    @staticmethod
    def get_title_name(wfi):
        if wfi.title:
            if wfi.title.name:
                return wfi.title.name
            else:
                return ''

    def get_employee_action_required(self, wfi):
        user = None
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            user = request.user
        if user and hasattr(user, "employee"):
            return wfi.employee_action_required(user.employee)
        return False
    
    def get_transition_action_required(self, wfi):
        user = None
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            user = request.user
        if user and hasattr(user, "employee"):
            return wfi.transition_action_required(user.employee)
        return False
    
    def get_pis_action_required(self, wfi):
        user = None
        request = self.context.get("request")
        if request and hasattr(request, "user"):
            user = request.user
        if user and hasattr(user, "employee"):
            return wfi.pis_action_required(user.employee)
        return False

    @staticmethod
    def get_workflow_name(wfi):
        display_value = wfi.workflow.name
        t = wfi.transition
        if t:
            employee_name = f'{t.employee_first_name} {t.employee_last_name}'
            if employee_name == ' ':
                employee_name = 'No Name'
            display_value += f' - {employee_name}'
        return display_value


class WorkflowInstanceSimpleSerializer(WorkflowInstanceBaseSerializer):
    """
    Used for WorkflowTable component
    """
    status = serializers.SerializerMethodField()
    transition_type = serializers.CharField(
        source='transition.type', required=False
    )
    transition_submitter = serializers.SerializerMethodField()
    transition_date_submitted = serializers.SerializerMethodField()

    class Meta:
        model = WorkflowInstance
        fields = [
            'url', 'pk', 'created_by', 'started_at', 'complete',
            'completed_at', 'percent_complete', 'status', 'employee_name',
            'title_name', 'transition_type', 'transition_submitter',
            'transition_date_submitted', 'transition_date', 'workflow_type',
            'workflow_name', 'workflow_role_pk', 'employee_action_required',
            'pis_action_required', 'transition_action_required'
        ]
        depth = 1
    
    @staticmethod
    def get_status(wfi):
        if wfi.transition and wfi.transition.assignee == 'Submitter':
            return wfi.transition.submitter.name
        elif wfi.transition and wfi.transition.assignee != 'Complete':
            return wfi.transition.assignee
        else:
            return wfi.percent_complete

    @staticmethod
    def get_transition_submitter(wfi):
        if wfi.transition:
            if wfi.transition.submitter:
                return wfi.transition.submitter.name
            else:
                return ''
    
    @staticmethod
    def get_transition_date_submitted(wfi):
        if wfi.transition:
            if wfi.transition.date_submitted:
                return wfi.transition.date_submitted
            else:
                return ''


class WorkflowInstanceSerializer(WorkflowInstanceBaseSerializer):
    process_instances = ProcessInstanceSerializer(source='pis', many=True)
    transition = EmployeeTransitionSerializer()

    class Meta:
        model = WorkflowInstance
        fields = [
            'url', 'pk', 'workflow', 'process_instances', 'transition',
            'active', 'complete', 'percent_complete', 'title_name',
            'employee_action_required', 'pis_action_required',
            'transition_action_required', 'workflow_type', 'workflow_role_pk'
        ]
        depth = 1
