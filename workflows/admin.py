from django.contrib import admin
from django.forms import BaseInlineFormSet, ModelForm
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.db import transaction

from workflows.models import (
    Action, EmployeeTransition, Process, ProcessInstance, Role, Step,
    StepChoice, StepInstance, TransitionChange, Workflow, WorkflowInstance
)


@admin.register(Workflow)
class WorkflowAdmin(admin.ModelAdmin):
    list_display = ("name", "version")


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ("pk", "name", "members_list")
    filter_horizontal = ("members",)
    
    # Avoid many queries when getting members to display in list
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.prefetch_related('members')

    def members_list(self, obj):
        return ",\n".join([employee.name for employee in obj.members.all()])


class GetParentFormSet(BaseInlineFormSet):
    """
    Used to access the parent model instance in an inline model form
    """
    def get_form_kwargs(self, index):
        kwargs = super().get_form_kwargs(index)
        kwargs['parent_object'] = self.instance
        return kwargs


class StepForm(ModelForm):
    """Used in Step Admin for next_step"""
    def __init__(self, *args, **kwargs):
        super(StepForm, self).__init__(*args, **kwargs)
        self.fields['next_step'].queryset = Step.objects.filter(
            process=self.instance.process
        ).exclude(pk=self.instance.pk).order_by('order')


class StepInlineForm(ModelForm):
    """
    Used in Process Admin for child Steps' next_steps and trigger_processes
    """
    def __init__(self, *args, parent_object, **kwargs):
        super(StepInlineForm, self).__init__(*args, **kwargs)
        if parent_object.pk:
            self.fields['next_step'].queryset = Step.objects\
                .filter(process=parent_object)\
                .exclude(pk=self.instance.pk)\
                .order_by('order')
            self.fields['trigger_processes'].queryset = Process.objects.filter(
                workflow=parent_object.workflow
            ).exclude(pk=parent_object.pk).order_by('name')
        else:
            self.fields['next_step'].queryset = Step.objects.none()
            self.fields['trigger_processes'].queryset = Process.objects.none()


class StepChoiceForm(ModelForm):
    """Used in Step Admin for Step choices"""
    def __init__(self, *args, parent_object, **kwargs):
        super(StepChoiceForm, self).__init__(*args, **kwargs)
        self.fields['next_step'].queryset = Step.objects.filter(
            process=parent_object.process
        ).exclude(pk=parent_object.pk).order_by('order')         


class ProcessInstanceForm(ModelForm):
    """
    Used in ProcessInstance Admin for current_step_instance and
    workflow_instance
    """
    def __init__(self, *args, **kwargs):
        super(ProcessInstanceForm, self).__init__(*args, **kwargs)
        self.fields['current_step_instance'].queryset = \
            StepInstance.objects.filter(process_instance=self.instance)
        if hasattr(self.instance, 'process'):
            self.fields['workflow_instance'].queryset = \
                WorkflowInstance.objects.filter(
                    workflow=self.instance.process.workflow
                )


class StepInstanceForm(ModelForm):
    """Used in StepInstance Admin for process_instance"""
    def __init__(self, *args, **kwargs):
        super(StepInstanceForm, self).__init__(*args, **kwargs)
        # Filter step based on the process of the step instance
        if hasattr(self.instance, 'process_instance'):
            self.fields['step'].queryset = Step.objects.filter(
                process=self.instance.process_instance.process
            )
        # Filter process_instance based on the process of the step
        if hasattr(self.instance, 'step'):
            self.fields['process_instance'].queryset = \
                ProcessInstance.objects.filter(
                    process=self.instance.step.process
                )


class StepInline(admin.TabularInline):
    model = Step
    formset = GetParentFormSet
    form = StepInlineForm
    ordering = ('order',)
    readonly_fields = ("edit_link", "next_step_choices")
    extra = 0

    def edit_link(self, instance):
        url = reverse('admin:%s_%s_change' % (
            instance._meta.app_label, instance._meta.model_name
        ), args=[instance.pk] )
        if instance.pk:
            return mark_safe(u'<a href="{u}">edit</a>'.format(u=url))
        else:
            return ''

    def next_step_choices(self, instance):
        choices_text = ''
        for idx, choice in enumerate(
            instance.next_step_choices.all().order_by('order')
        ):
            triggered_processes = choice.trigger_processes.all()
            if idx != 0:
                choices_text += " / "
            choices_text += choice.choice_text + ": " + \
                str(choice.next_step.order) + ' - ' + choice.next_step.name
            if triggered_processes.count():
                choices_text += " -> " + \
                    ', '.join([p.name for p in triggered_processes])
        return choices_text


@admin.action(description="Duplicate selected Processes")
@transaction.atomic
def duplicate_process(modeladmin, request, queryset):
    for process in queryset:
        original_process_id = process.pk
        process.pk = None
        process.name = f"{process.name} (Copy)"
        process.save()

        # Duplicate Steps
        original_steps = Step.objects.filter(process_id=original_process_id)
        step_mapping = {}
        for step in original_steps:
            old_pk = step.pk
            step.pk = None
            step.process = process
            step.save()
            step_mapping[old_pk] = step

        # After all steps are duplicated, update next_step for each new step
        for old_step_pk, new_step in step_mapping.items():
            old_step = Step.objects.get(pk=old_step_pk)
            if old_step.next_step_id:
                new_next_step = step_mapping.get(old_step.next_step_id)
                if new_next_step:
                    new_step.next_step = new_next_step
                    new_step.save()

        # Duplicate StepChoices
        for old_step_pk, new_step in step_mapping.items():
            choices = StepChoice.objects.filter(step_id=old_step_pk)
            for choice in choices:
                choice.pk = None
                choice.step = new_step
                # Save the original next_step before changing pk
                original_next_step_id = choice.next_step_id
                choice.save()
                # Set the next_step to the duplicated step if it exists
                if original_next_step_id:
                    new_next_step = step_mapping.get(original_next_step_id)
                    if new_next_step:
                        choice.next_step = new_next_step
                        choice.save()


@admin.register(Process)
class ProcessAdmin(admin.ModelAdmin):
    list_display = ("name", "workflow", "version")
    list_filter = ("workflow",)
    ordering = ("workflow", "name")
    inlines = (StepInline,)
    actions = [duplicate_process]


class StepChoiceInline(admin.TabularInline):
    model = StepChoice
    formset = GetParentFormSet
    form = StepChoiceForm
    fk_name = "step"
    ordering = ("order",)
    extra = 0


@admin.register(Step)
class StepAdmin(admin.ModelAdmin):
    list_display = ("order", "name",)
    list_filter = ("process",)
    ordering = ("order",)
    form = StepForm
    inlines = (StepChoiceInline,)


@admin.register(Action)
class ActionAdmin(admin.ModelAdmin):
    list_display = ("name", "type")


@admin.register(WorkflowInstance)
class WorkflowInstanceAdmin(admin.ModelAdmin):
    list_display = (
        "pk", "workflow", "created_by", "started_at", "completed_at",
        "complete", "active"
    )
    list_filter = ("workflow", "active", "complete")
    readonly_fields = ("started_at",)
    fields = (
        "created_by", "started_at", "completed_at", "workflow", "transition",
        "active", "complete"
    )


@admin.register(ProcessInstance)
class ProcessInstanceAdmin(admin.ModelAdmin):
    list_display = (
        "pk", "process", "workflow_instance", "current_step_instance"
    )
    fields = (
        "started_at", "completed_at", "process", "workflow_instance",
        "current_step_instance"
    )
    list_filter = ("process__workflow", "process")
    readonly_fields = ("started_at",)
    form = ProcessInstanceForm


@admin.register(StepInstance)
class StepInstanceAdmin(admin.ModelAdmin):
    list_display = ("pk", "step", "process_instance")
    ordering = ("process_instance", "step__order")
    fields = (
        "started_at", "completed_at", "step", "process_instance",
        "completed_by"
    )
    readonly_fields = ("started_at",)
    form = StepInstanceForm


class TransitionChangeInline(admin.TabularInline):
    model = TransitionChange
    readonly_fields = ("date", "created_by", "changes")
    extra = 0


@admin.register(EmployeeTransition)
class EmployeeTransitionAdmin(admin.ModelAdmin):
    inlines = (TransitionChangeInline,)
