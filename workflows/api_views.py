from datetime import datetime
import traceback

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from django.utils import timezone
from django.utils.timezone import get_current_timezone

from mainsite.helpers import is_true_string, prop_in_obj, record_error

from people.models import Employee, JobTitle, UnitOrProgram

from workflows.helpers import (
    create_process_instances, send_early_hr_email,
    send_mailbox_notification_email, send_step_completion_email,
    send_transition_fiscal_email, send_transition_hr_email,
    send_transition_sds_hiring_leads_email, send_transition_stn_email,
    send_transition_submitter_email
)
from workflows.models import (
    EmployeeTransition, Process, ProcessInstance, Role, Step, StepChoice,
    StepInstance, TransitionChange, Workflow, WorkflowInstance
)

from workflows.serializers import (
    EmployeeTransitionRedactedSerializer, EmployeeTransitionSerializer,
    ProcessInstanceSerializer, ProcessSerializer, RoleSerializer,
    StepChoiceSerializer, StepInstanceSerializer, StepSerializer,
    TransitionChangeSerializer, WorkflowInstanceSerializer,
    WorkflowInstanceSimpleSerializer, WorkflowSerializer
)


class WorkflowViewSet(viewsets.ModelViewSet):
    queryset = Workflow.objects.all()
    serializer_class = WorkflowSerializer
    # permission_classes = [
    #     IsAuthenticatedOrReadOnly
    # ]

    def get_queryset(self):
        """
        This view should return a list of all workflows for which the user has
        the appropriate role.
        """
        user = self.request.user
        if user.is_authenticated:
            if user.is_superuser:
                queryset = Workflow.objects.all()
            else:
                wfs_can_view = filter(
                    lambda x: x['display'],
                    user.employee.workflow_display_options()
                )
                wfs_can_view_ids = list(map(lambda x: x['id'], wfs_can_view))
                queryset = Workflow.objects.filter(id__in=wfs_can_view_ids)
        else:
            queryset = Workflow.objects.none()
        return queryset


class WorkflowInstanceViewSet(viewsets.ModelViewSet):
    queryset = WorkflowInstance.objects.all()
    serializer_class = WorkflowInstanceSerializer
    # permission_classes = [
    #     IsAuthenticatedOrReadOnly
    # ]

    def get_serializer_class(self):
        simple = self.request.query_params.get('simple', None)
        if simple is not None and is_true_string(simple):
            return WorkflowInstanceSimpleSerializer
        return super().get_serializer_class()

    def get_queryset(self):
        """

        """
        user = self.request.user
        if user.is_authenticated:
            wfs_can_view = filter(
                lambda x: x['display'],
                user.employee.workflow_display_options()
            )
            wfs_can_view_ids = list(map(lambda x: x['id'], wfs_can_view))
            archived = self.request.query_params.get('archived', None)
            if archived is not None and is_true_string(archived):
                # Archived WFIs
                return WorkflowInstance.inactive_objects.filter(
                    workflow__id__in=wfs_can_view_ids
                ).order_by('-started_at').select_related(
                    'transition', 'workflow', 'workflow__role'
                ).prefetch_related('pis')
            elif archived is not None and not is_true_string(archived):
                complete = self.request.query_params.get('complete', None)
                if complete is not None and is_true_string(complete):
                    # Complete WFIs
                    return WorkflowInstance.active_objects.filter(
                        workflow__id__in=wfs_can_view_ids, complete=True
                    ).order_by('-completed_at').select_related(
                        'transition', 'workflow', 'workflow__role'
                    ).prefetch_related('pis')
                elif complete is not None and not is_true_string(complete):
                    # Current active WFIs
                    return WorkflowInstance.active_objects.filter(
                        workflow__id__in=wfs_can_view_ids, complete=False
                    ).order_by('started_at').select_related(
                        'transition', 'workflow', 'workflow__role'
                    ).prefetch_related('pis')
            return WorkflowInstance.objects.all()
        else:
            return WorkflowInstance.objects.none()


    def create(self, request):
        wf_type = request.data['type']
        wf = None
        et = None
        employeeID = EmployeeTransition.EMPLOYEE_ID_CLID
        if request.user.employee.is_sds_employee:
            employeeID = EmployeeTransition.EMPLOYEE_ID_CLSD
        if wf_type == 'employee-new':
            et = EmployeeTransition.objects.create(
                type=EmployeeTransition.TRANSITION_TYPE_NEW,
                employee_id=employeeID
            )
        elif wf_type == 'employee-return':
            et = EmployeeTransition.objects.create(
                type=EmployeeTransition.TRANSITION_TYPE_RETURN,
                employee_id=employeeID
            )
        elif wf_type == 'employee-name-change':
            et = EmployeeTransition.objects.create(
                type=EmployeeTransition.TRANSITION_TYPE_NAME_CHANGE,
                employee_id=employeeID
            )
        elif wf_type == 'employee-change':
            et = EmployeeTransition.objects.create(
                type=EmployeeTransition.TRANSITION_TYPE_CHANGE,
                employee_id=employeeID
            )
        elif wf_type == 'employee-exit':
            et = EmployeeTransition.objects.create(
                type=EmployeeTransition.TRANSITION_TYPE_EXIT,
                employee_id=employeeID
            )
        try:
            wf = Workflow.objects.get(type=wf_type)
        except Workflow.DoesNotExist:
            return Response(
                data='Invalid workflow type',
                status=status.HTTP_400_BAD_REQUEST
            )
        # Create workflow instance
        wfi = WorkflowInstance.objects.create(workflow=wf, transition=et)
        # Create process instances
        for process in wf.processes.filter(workflow_start=True):
            process.create_process_instance(wfi)
        serialized_wfi = WorkflowInstanceSerializer(wfi,
            context={'request': request}
        )
        return Response(serialized_wfi.data)
    
    def partial_update(self, request, pk=None):
        """
        Archive/restore or complete/reopen a workflow instance.
        """
        wfi = WorkflowInstance.objects.get(pk=pk)
        if request.data['action'] == 'archive':
            wfi.active = False
        elif request.data['action'] == 'restore':
            wfi.active = True
        # TODO: Add logic to prevent completing an archived workflow instance
        # TODO: For now, complete is a manual process, but it should intersect
        # somehow with the process instances being complete.
        elif request.data['action'] == 'complete':
            wfi.complete = True
            wfi.completed_at = timezone.now()
        elif request.data['action'] == 'reopen':
            wfi.complete = False
            wfi.completed_at = None
        else:
            return Response(
                data='Invalid action', status=status.HTTP_400_BAD_REQUEST
            )
        wfi.save()
        serialized_wfi = WorkflowInstanceSerializer(wfi,
            context={'request': request})
        return Response(serialized_wfi.data)

    def destroy(self, request, pk=None):
        try:
            instance = self.get_object()
            if instance.transition:
                instance.transition.delete()
            return super().destroy(request, pk)
        except Exception as e:
            message = 'Error deleting workflow instance.'
            record_error(message, e, request, traceback.format_exc())
            return Response(
                data=message,
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class EmployeeTransitionViewSet(viewsets.ModelViewSet):
    queryset = EmployeeTransition.objects.all()
    serializer_class = EmployeeTransitionSerializer
    # permission_classes = [
    #     IsAuthenticatedOrReadOnly
    # ]

    def get_queryset(self):
        """
        Block anonymous users and users without access from seeing any
        transitions. Superusers can see all.
        """
        queryset = EmployeeTransition.objects.none()
        user = self.request.user
        if not user.is_anonymous and user.is_authenticated:
            if user.is_superuser:
                queryset = EmployeeTransition.objects.all()
            elif user.employee:
                employee = user.employee
                if employee.can_view_employee_transitions():
                    # Users who can view employee transitions can see all
                    queryset = EmployeeTransition.objects.all()
        return queryset

    def get_serializer_class(self):
        """
        Superusers and HR/Fiscal employees should see all fields. All others
        should see only a subset.
        """
        serializer = EmployeeTransitionRedactedSerializer
        user = self.request.user
        if not user.is_anonymous and user.is_authenticated:
            if user.is_superuser:
                # Superusers can see all fields
                return EmployeeTransitionSerializer
            if user.employee:
                employee = user.employee
                if employee.is_hr_employee or employee.is_fiscal_employee:
                    # HR and Fiscal employees can see all fields
                    serializer = EmployeeTransitionSerializer
        return serializer

    # def create(self, request):
    #     if self.request.data['type'] == 'new_employee_onboarding':
    #         et = EmployeeTransition.objects.create(type=EmployeeTransition.TRANSITION_TYPE_NEW)
    #         wf = Workflow.objects.get(name="New Employee Onboarding")
    #         wfi = WorkflowInstance.objects.create(workflow=wf, transition=et)
    #         # Create process instances
    #         for process in wf.processes.filter(workflow_start=True):
    #             process.create_process_instance(wfi)
    #         serialized_wfi = WorkflowInstanceSerializer(wfi,
    #             context={'request': request}
    #         )
    #         return Response(serialized_wfi.data)

    def update(self, request, pk=None):
        try:
            t = EmployeeTransition.objects.get(pk=pk)

            # Set submitter only the first time the transition is updated
            if not t.submitter:
                submitter = Employee.objects.get(pk=request.data['submitter_pk']) if \
                    'submitter_pk' in request.data else None
                t.submitter = submitter
                t.date_submitted = datetime.now(tz=get_current_timezone())
                # Also set the assignee
                t.assignee = EmployeeTransition.ASSIGNEE_SUBMITTER

            t.type = request.data['type']
            t.worker_type = request.data['worker_type']

            current_employee = t.current_employee.pk if t.current_employee else -1
            editing_employee = all([
                # Employee field is being edited
                'current_employee_pk' in request.data,
                # Employee field is being changed
                request.data['current_employee_pk'] != current_employee
            ])
            if editing_employee:
                if request.data['current_employee_pk'] != -1:
                    t.current_employee = Employee.objects.get(
                        pk=request.data['current_employee_pk']
                    )
                else:
                    t.current_employee = None

            t.employee_first_name = request.data['employee_first_name']
            t.employee_middle_initial = request.data['employee_middle_initial']
            t.employee_last_name = request.data['employee_last_name']
            t.employee_preferred_name = request.data['employee_preferred_name']
            
            # Only HR can edit employee number fields
            user_is_hr = request.user.employee.is_hr_employee
            if user_is_hr:
                t.employee_id = request.data['employee_id']
                t.employee_number = request.data['employee_number']
                t.employee_email = request.data['employee_email']
            
            if prop_in_obj(request.data, 'title_pk', -1):
                t.title = JobTitle.objects.get(pk=request.data['title_pk'])
            else:
                t.title = None

            t.fte = request.data['fte']
            t.hours_per_week = request.data['hours_per_week']
            t.hourly_rate = request.data['hourly_rate']

            # Only the submitter, hiring manager, HR, fiscal, and SDS hiring leads
            # can edit salary fields.
            user_is_submitter = request.user.employee == t.submitter
            user_is_hiring_manager = request.user.employee == t.manager
            user_is_hr = request.user.employee.is_hr_employee
            user_is_fiscal = request.user.employee.is_fiscal_employee
            user_is_sds_hiring_lead = request.user.employee.is_sds_hiring_lead
            user_can_edit_salary = any([
                user_is_submitter, user_is_hiring_manager, user_is_hr,
                user_is_fiscal, user_is_sds_hiring_lead
            ])
            if request.data['salary_range'] == None and t.salary_range == None:
                editing_salary_range = False
            else:
                editing_salary_range = all([
                    'salary_range' in request.data,
                    request.data['salary_range'] != str(t.salary_range)
                ])
            editing_salary_step = all([
                'salary_step' in request.data,
                request.data['salary_step'] != t.salary_step
            ])
            editing_stipend = request.data['stipend'] != t.stipend
            editing_salary = any([
                editing_salary_range, editing_salary_step, editing_stipend
            ])
            if editing_salary and not user_can_edit_salary:
                message = 'Only the submitter, hiring manager, fiscal, HR, \
                    or hiring leads can edit salary fields.'
                record_error(message, None, request, traceback.format_exc())
                return Response(
                    data=message,
                    status=status.HTTP_403_FORBIDDEN
                )
            if editing_salary and user_can_edit_salary:
                t.salary_range = request.data['salary_range']
                t.salary_step = request.data['salary_step']
                t.stipend = request.data['stipend']
            
            t.bilingual = request.data['bilingual']
            t.second_language = request.data['second_language']
            
            # On an update, only the original submitter can edit manager field
            user_is_submitter = request.user.employee == t.submitter
            user_is_hr = request.user.employee.is_hr_employee
            user_can_edit_manager = any([user_is_submitter, user_is_hr])
            current_manager = t.manager.pk if t.manager else -1
            editing_manager = all([
                # Manager field is being edited
                'manager_pk' in request.data,
                # Manager field is being changed
                request.data['manager_pk'] != current_manager
            ])
            if editing_manager and not user_can_edit_manager:
                message = 'Only the submitter and HR can edit the manager \
                    field.'
                record_error(message, e, request, traceback.format_exc())
                return Response(
                    data=message,
                    status=status.HTTP_403_FORBIDDEN
                )
            if user_can_edit_manager:
                if editing_manager:
                    if request.data['manager_pk'] != -1:
                        t.manager = Employee.objects.get(pk=request.data['manager_pk'])
                    else:
                        t.manager = None
                
            if prop_in_obj(request.data, 'unit_pk', -1):
                t.unit = UnitOrProgram.objects.get(pk=request.data['unit_pk'])
            else:
                t.unit = None
            
            if 'transition_date' in request.data:
                t.transition_date = request.data['transition_date']
            else:
                t.transition_date = None

            if 'system_change_date' in request.data:
                t.system_change_date = request.data['system_change_date']
            else:
                t.system_change_date = None

            t.schedule = request.data['schedule']
            t.lwop = request.data['lwop']
            t.lwop_details = request.data['lwop_details']
            t.preliminary_hire = request.data['preliminary_hire']
            t.delete_profile = request.data['delete_profile']
            t.office_location = request.data['office_location']
            t.cubicle_number = request.data['cubicle_number']
            t.union_affiliation = request.data['union_affiliation']
            t.teleworking = request.data['teleworking']
            t.computer_type = request.data['computer_type']
            t.computer_gl = request.data['computer_gl']
            t.computer_description = request.data['computer_description']
            t.phone_number = request.data['phone_number']
            t.phone_request = request.data['phone_request']
            t.phone_request_data = request.data['phone_request_data']
            t.load_code = request.data['load_code']
            t.cell_phone = request.data['cell_phone']
            t.should_delete = request.data['should_delete']
            t.extension_remain_active = request.data['extension_remain_active']
            t.reassign_to = request.data['reassign_to']
            t.gas_pin_needed = request.data['gas_pin_needed']
            t.oregon_access = request.data['oregon_access']
            t.business_cards = request.data['business_cards']
            t.prox_card_needed = request.data['prox_card_needed']
            t.mailbox_needed = request.data['mailbox_needed']
            
            if prop_in_obj(request.data, 'access_emails_pk', -1):
                t.access_emails = Employee.objects.get(
                    pk=request.data['access_emails_pk']
                )    
            else:
                t.access_emails = None 
            
            t.special_instructions = request.data['special_instructions']

            # Only fiscal can edit fiscal field
            user_is_fiscal = request.user.employee.is_fiscal_employee
            if user_is_fiscal:
                t.fiscal_field = request.data['fiscal_field']

            t.save()
            serialized_transition = EmployeeTransitionSerializer(t,
                context={'request': request})
            return Response(serialized_transition.data)
        except Exception as e:
            message = 'Error updating employee transition.'
            record_error(message, e, request, traceback.format_exc())
            return Response(
                data=message,
                status=status.HTTP_403_FORBIDDEN
            )

    @action(detail=True, methods=['post'])
    def send_mailbox_notification_email(self, request, pk):
        try:
            transition = EmployeeTransition.objects.get(pk=pk)
            send_mailbox_notification_email(
                transition,
                sender_name=request.data['senderName'],
                sender_email=request.data['senderEmail'],
                url=request.data['transitionUrl'] )
            return Response("Mailbox notification email sent.")
        except Exception as e:
            message = 'Error sending mailbox notification email.'
            record_error(message, e, request, traceback.format_exc())
            return Response(
                data=message,
                status=status.HTTP_403_FORBIDDEN
            )

    @action(detail=True, methods=['post'])
    def send_transition_to_email_list(self, request, pk):
        try:
            transition = EmployeeTransition.objects.get(pk=pk)
            if request.data['type'] == 'SDS':
                transition.assignee = EmployeeTransition.ASSIGNEE_HIRING_LEAD
                transition.save()
                send_transition_sds_hiring_leads_email(
                    transition,
                    extra_message=request.data['extraMessage'],
                    sender_name=request.data['senderName'],
                    sender_email=request.data['senderEmail'],
                    url=request.data['transitionUrl']
                )
                send_early_hr_email(
                    transition,
                    url=request.data['transitionUrl']
                )
            elif request.data['type'] == 'FI':
                transition.assignee = EmployeeTransition.ASSIGNEE_FISCAL
                transition.save()
                send_transition_fiscal_email(
                    transition,
                    extra_message=request.data['extraMessage'],
                    sender_name=request.data['senderName'],
                    sender_email=request.data['senderEmail'],
                    url=request.data['transitionUrl']
                )
                submitter = Employee.objects.get(
                    user__email=request.data['senderEmail']
                )
                if submitter.is_gs_employee or submitter.is_admin_employee:
                    send_early_hr_email(
                        transition,
                        url=request.data['transitionUrl']
                    )
            elif request.data['type'] == 'HR':
                transition.assignee = EmployeeTransition.ASSIGNEE_HR
                transition.save()
                send_transition_hr_email(
                    transition,
                    extra_message=request.data['extraMessage'],
                    sender_name=request.data['senderName'],
                    sender_email=request.data['senderEmail'],
                    url=request.data['transitionUrl']
                )
            elif request.data['type'] == 'STN':
                transition.assignee = EmployeeTransition.ASSIGNEE_COMPLETE
                transition.save()
                send_transition_stn_email(
                    transition,
                    update=request.data['update'],
                    extra_message=request.data['extraMessage'],
                    sender_name=request.data['senderName'],
                    url=request.data['transitionUrl']
                )
                create_process_instances(transition)
            elif request.data['type'] == 'ASSIGN':
                if request.data['reassignTo'] == 'Submitter':
                    transition.assignee = EmployeeTransition.ASSIGNEE_SUBMITTER
                    transition.save()
                    send_transition_submitter_email(
                        transition,
                        extra_message=request.data['extraMessage'],
                        sender_name=request.data['senderName'],
                        sender_email=request.data['senderEmail'],
                        url=request.data['transitionUrl'],
                        reassigned=True
                    )
                elif request.data['reassignTo'] == 'Hiring Lead':
                    transition.assignee = EmployeeTransition.ASSIGNEE_HIRING_LEAD
                    transition.save()
                    send_transition_sds_hiring_leads_email(
                        transition,
                        extra_message=request.data['extraMessage'],
                        sender_name=request.data['senderName'],
                        sender_email=request.data['senderEmail'],
                        url=request.data['transitionUrl'],
                        reassigned=True
                    )
                elif request.data['reassignTo'] == 'Fiscal':
                    transition.assignee = EmployeeTransition.ASSIGNEE_FISCAL
                    transition.save()
                    send_transition_fiscal_email(
                        transition,
                        extra_message=request.data['extraMessage'],
                        sender_name=request.data['senderName'],
                        sender_email=request.data['senderEmail'],
                        url=request.data['transitionUrl'],
                        reassigned=True
                    )
                elif request.data['reassignTo'] == 'HR':
                    transition.assignee = EmployeeTransition.ASSIGNEE_HR
                    transition.save()
                    send_transition_hr_email(
                        transition,
                        extra_message=request.data['extraMessage'],
                        sender_name=request.data['senderName'],
                        sender_email=request.data['senderEmail'],
                        url=request.data['transitionUrl'],
                        reassigned=True
                    )
                else:
                    return Response(
                        data="Invalid assignee.",
                        status=status.HTTP_400_BAD_REQUEST
                    )
            else:
                return Response(
                    data="Invalid type.",
                    status=status.HTTP_400_BAD_REQUEST
                )
            return Response("Sent email to staff.")
        except Exception as e:
            message = 'Error sending transition email.'
            record_error(message, e, request, traceback.format_exc())
            return Response(
                data=message,
                status=status.HTTP_403_FORBIDDEN
            )


class TransitionChangeViewSet(viewsets.ModelViewSet):
    queryset = TransitionChange.objects.all()
    serializer_class = TransitionChangeSerializer

    def get_queryset(self):
        """
        Block anonymous users and users without access from seeing any
        transitions. Superusers can see all.
        """
        queryset = TransitionChange.objects.none()
        user = self.request.user
        if not user.is_anonymous and user.is_authenticated:
            if user.is_superuser:
                queryset = TransitionChange.objects.all()
            elif user.employee:
                employee = user.employee
                if employee.can_view_employee_transitions():
                    # Users who can view employee transitions can see all
                    queryset = TransitionChange.objects.all()
        return queryset


class ProcessViewSet(viewsets.ModelViewSet):
    queryset = Process.objects.all()
    serializer_class = ProcessSerializer
    # permission_classes = [
    #     IsAuthenticatedOrReadOnly
    # ]

    def get_queryset(self):
        """

        """
        user = self.request.user
        if user.is_authenticated:
            if user.is_superuser:
                queryset = Process.objects.all()
            else:
                queryset = Process.objects.none()
        else:
            queryset = Process.objects.none()
        return queryset


class ProcessInstanceViewSet(viewsets.ModelViewSet):
    queryset = ProcessInstance.objects.all()
    serializer_class = ProcessInstanceSerializer
    # permission_classes = [
    #     IsAuthenticatedOrReadOnly
    # ]

    def get_queryset(self):
        """
        This view should return a list of all time off requests for which
        the currently authenticated user is the manager.
        """
        user = self.request.user
        if user.is_authenticated:
            if user.is_superuser:
                queryset = ProcessInstance.objects.all()
            else:
                queryset = ProcessInstance.objects.none()
        else:
            queryset = ProcessInstance.objects.none()
        return queryset


class StepViewSet(viewsets.ModelViewSet):
    queryset = Step.objects.all()
    serializer_class = StepSerializer
    # permission_classes = [
    #     IsAuthenticatedOrReadOnly
    # ]

    def get_queryset(self):
        """
        This view should return a list of all time off requests for which
        the currently authenticated user is the manager.
        """
        user = self.request.user
        if user.is_authenticated:
            if user.is_superuser:
                queryset = Step.objects.all()
            else:
                queryset = Step.objects.none()
        else:
            queryset = Step.objects.none()
        return queryset


class StepChoiceViewSet(viewsets.ModelViewSet):
    queryset = StepChoice.objects.all()
    serializer_class = StepChoiceSerializer
    # permission_classes = [
    #     IsAuthenticatedOrReadOnly
    # ]

    def get_queryset(self):
        """
        This view should return a list of all step choices.
        """
        user = self.request.user
        if user.is_authenticated:
            queryset = StepChoice.objects.all()
        else:
            queryset = StepChoice.objects.none()
        return queryset


class StepInstanceViewSet(viewsets.ModelViewSet):
    queryset = StepInstance.objects.all()
    serializer_class = StepInstanceSerializer
    # permission_classes = [
    #     IsAuthenticatedOrReadOnly
    # ]

    def get_queryset(self):
        """
        This view should return a list of all step instances.
        """
        user = self.request.user
        if user.is_authenticated:
            queryset = StepInstance.objects.all()
        else:
            queryset = StepInstance.objects.none()
        return queryset
    
    def partial_update(self, request, pk=None):
        """
        Complete or undo completion of a step instance
        """
        stepinstance = StepInstance.objects.get(pk=pk)

        # If step instance or step choice completion triggers a new
        # process, create a list for creation
        trigger_processes = []
        # StepInstance ProcessInstance triggers
        if stepinstance.step.trigger_processes.count():
            trigger_processes += list(stepinstance.step.trigger_processes.all())

        # COMPLETION
        if (request.data['action'] == 'complete'):
            # Complete the current step instance  
            if stepinstance.completed_at:
                # Prevent completing a step instance twice
                return Response(
                    data='This step instance has already been completed.',
                    status=status.HTTP_400_BAD_REQUEST
                )
      
            stepinstance.completed_at = timezone.now()
            stepinstance.completed_by = request.user.employee
            stepinstance.save()

            # Trigger any completion actions
            if stepinstance.step.completion_action:
                stepinstance.step.completion_action.trigger()
                
            # Make the next StepInstance
            processinstance = stepinstance.process_instance
            if 'nextStepPk' in request.data:
                next_step = Step.objects.get(pk=request.data['nextStepPk'])
            else:
                next_step=stepinstance.step.next_step
            new_stepinstance = StepInstance.objects.create(
                step=next_step,
                process_instance=processinstance
            )
            processinstance.current_step_instance = new_stepinstance
            processinstance.save()
            # Notify responsible parties of the new step instance if
            # they're different from the current step instance
            if new_stepinstance.step.role != stepinstance.step.role:
                send_step_completion_email(new_stepinstance, stepinstance)

            # Update PI percent complete and completion status
            processinstance.update_percent_complete()
            
            # Update WFI percent complete and completion status
            wfi = processinstance.workflow_instance
            wfi.update_percent_complete()

            # Delete triggered processes
            # StepChoice ProcessInstance triggers
            if 'triggerProcessesPks' in request.data:
                for pk in request.data['triggerProcessesPks']:
                    trigger_processes.append(Process.objects.get(pk=pk))
            for process in trigger_processes:
                process.create_process_instance(wfi)
        
        # UNCOMPLETION
        else:
            # Undo completion of the current step instance
            if not stepinstance.completed_at:
                # Prevent undoing completion of a step instance that hasn't
                # been completed
                return Response(
                    data='This step instance has not been completed.',
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Undo completion of current SI (user and date)
            stepinstance.completed_at = None
            stepinstance.completed_by = None
            stepinstance.save()

            # Update PI
            processinstance = stepinstance.process_instance
            nextStepInstance = StepInstance.objects.get(
                pk=request.data['nextStepInstancePk']
            )
            if nextStepInstance.step.end:
                # If the next step is the last step instance in a process,
                # un-complete the process
                processinstance.completed_at = None
            processinstance.current_step_instance = stepinstance
            processinstance.update_percent_complete()
            processinstance.save()
            workflowinstance = processinstance.workflow_instance
            workflowinstance.update_percent_complete()

            # Delete next SI
            nextStepInstance.delete()

            # Delete triggered processes
            # StepChoice ProcessInstance triggers
            for step_choice in stepinstance.step.next_step_choices.all():
                for process in step_choice.trigger_processes.all():
                    trigger_processes.append(process)

            for process in trigger_processes:
                process.delete_process_instances(workflowinstance)

        serialized_stepinstance = StepInstanceSerializer(stepinstance,
            context={'request': request})
        return Response(serialized_stepinstance.data)


class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    # permission_classes = [
    #     IsAuthenticatedOrReadOnly
    # ]

    def get_queryset(self):
        """
        This view should return a list of all time off requests for which
        the currently authenticated user is the manager.
        """
        user = self.request.user
        if user.is_authenticated:
            if user.is_superuser:
                queryset = Role.objects.all()
            else:
                queryset = Role.objects.none()
        else:
            queryset = Role.objects.none()
        return queryset