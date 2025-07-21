from django.contrib import admin
from django.urls import reverse
from django.utils.safestring import mark_safe

from .models import (
    Division, Employee, JobTitle, PerformanceReview, PRFactor,
    PRFactorResponseSet, PRForm, ReviewNote, Signature, SignatureReminder,
    TeleworkApplication, TeleworkSignature, UnitOrProgram,
    ViewedSecurityMessage
)


class EmployeeInline(admin.TabularInline):
    model = Employee
    fields = (
        "edit_link", "active", "temporary", "number", "username",
        "unit_or_program", "manager"
    )
    readonly_fields = (
        "edit_link", "active", "temporary", "number", "username",
        "unit_or_program", "manager"
    )
    extra = 0

    def edit_link(self, instance):
        url = reverse(
            'admin:%s_%s_change' %
                (instance._meta.app_label,  instance._meta.model_name),
            args=[instance.pk]
        )
        if instance.pk:
            return mark_safe(u'<a href="{u}">edit</a>'.format(u=url))
        else:
            return ''


class UnitOrProgramInline(admin.TabularInline):
    model = UnitOrProgram
    extra = 0


@admin.register(Division)
class DivisionAdmin(admin.ModelAdmin):
    list_display = ("name",)
    list_filter = ("organization",)
    inlines = (UnitOrProgramInline,)


@admin.register(JobTitle)
class JobTitleAdmin(admin.ModelAdmin):
    list_display = ("name", "division", "active", "position_description_link")
    list_filter = ("division", "active")
    ordering = ("division", "name")
    inlines = [EmployeeInline]


class WorkflowOptionsInline(admin.TabularInline):
    model = Employee.workflow_options.through
    extra = 0


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = (
        "number", "active", "username", "job_title", "unit_or_program",
        "manager"
    )
    list_filter = (
        "active", "organization", "unit_or_program__division",
        "unit_or_program"
    )
    search_fields = ("user__username", "job_title__name")
    inlines = [WorkflowOptionsInline]


# class SelfEvaluationInline(EditLinkToInlineObject, admin.StackedInline):
#     model = EmployeeSelfEvaluation
#     readonly_fields = ('edit_link',)
#     extra = 0


class SignatureReminderInline(admin.TabularInline):
    model = SignatureReminder
    fields = ("employee", "date", "next_date")
    readonly_fields = ("date",)
    extra = 0


class SignatureInline(admin.TabularInline):
    model = Signature
    fields = ("employee", "date",)
    readonly_fields = ("date",)
    extra = 0


@admin.register(PerformanceReview)
class PerformanceReviewAdmin(admin.ModelAdmin):
    list_display = ("username", "status", "form", "effective_date")
    list_filter = ("status", "form", "employee")
    search_fields = ("employee__user__username", )
    inlines = (SignatureInline, SignatureReminderInline)
    # inlines = (SignatureInline, SignatureReminderInline, SelfEvaluationInline)

    def get_form(self, request, obj=None, **kwargs):
        pr_exists = hasattr(obj, 'pk')
        if pr_exists:
            user_is_superuser = request.user.is_superuser
            employee_cannot_view_pr = not hasattr(request.user, 'employee') or \
                obj.pk not in request.user.employee.prs_can_view()
            if not user_is_superuser and employee_cannot_view_pr:
                self.exclude = (
                    'step_increase', 'top_step_bonus', 'action_other',
                    'factor_job_knowledge', 'factor_work_quality',
                    'factor_work_quantity', 'factor_work_habits',
                    'factor_analysis', 'factor_initiative', 'factor_interpersonal',
                    'factor_communication', 'factor_dependability',
                    'factor_professionalism', 'factor_management',
                    'factor_supervision', 'evaluation_successes',
                    'evaluation_opportunities', 'evaluation_goals_manager',
                    'evaluation_goals_employee', 'evaluation_comments_employee',
                    'description_reviewed_employee', 'signed_position_description'
                )
            else:
                self.exclude = ()
        form = super(PerformanceReviewAdmin, self).get_form(
            request, obj, **kwargs
        )
        return form


class PRFactorInline(admin.TabularInline):
    model = PRFactor
    extra = 0


@admin.register(PRForm)
class PRFormAdmin(admin.ModelAdmin):
    list_display = ("name", "version")
    search_fields = ("name", )
    # exclude = ("factors",)
    inlines = (PRFactorInline,)


@admin.register(PRFactorResponseSet)
class PRFactorResponseSetAdmin(admin.ModelAdmin):
    list_display = ("responses",)


# class SelfEvaluationSignatureInline(admin.TabularInline):
#     model = SelfEvaluationSignature
#     extra = 0


# class SelfEvaluationSignatureReminderInline(admin.TabularInline):
#     model = SelfEvaluationSignatureReminder
#     extra = 0


# @admin.register(EmployeeSelfEvaluation)
# class SelfEvaluationAdmin(admin.ModelAdmin):
#     model = EmployeeSelfEvaluation
#     inlines = (SelfEvaluationSignatureInline, SelfEvaluationSignatureReminderInline)


@admin.register(ReviewNote)
class ReviewNoteAdmin(admin.ModelAdmin):
    list_display = ("author", "employee", "created_at")
    list_filter = ("employee", "author")
    readonly_fields = ("created_at",)

    def get_form(self, request, obj=None, **kwargs):
        note_exists = hasattr(obj, 'pk')
        user_is_superuser = request.user.is_superuser
        employee_cannot_view_note = not hasattr(request.user, 'employee') or \
            obj.pk not in request.user.employee.notes_can_view()
        if note_exists and not user_is_superuser and employee_cannot_view_note:
            self.exclude = ('note',)
        else:
            self.exclude = ()
        form = super(ReviewNoteAdmin, self).get_form(request, obj, **kwargs)
        return form


@admin.register(ViewedSecurityMessage)
class ViewedSecurityMessageAdmin(admin.ModelAdmin):
    list_display = ("employee", "security_message", "datetime")
    list_filter = ("security_message",)


class TeleworkSignatureInline(admin.TabularInline):
    model = TeleworkSignature
    fields = ("employee", "index", "date",)
    readonly_fields = ("date",)
    extra = 0


@admin.register(TeleworkApplication)
class TeleworkApplicationAdmin(admin.ModelAdmin):
    list_display = ("username", "status")
    inlines = (TeleworkSignatureInline,)
