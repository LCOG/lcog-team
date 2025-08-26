from django import forms
from django.contrib import admin
from django.contrib.auth import password_validation
from django.contrib.auth.admin import GroupAdmin, UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserCreationForm as BaseUserCreationForm
from django.contrib.auth.models import Group, User
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from mainsite.models import ImageUpload, SecurityMessage, TrustedIPAddress
from people.admin import EmployeeInline

from .models import (
    City, ImageUpload, Organization, SecurityMessage, State, ZipCode
)


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ("pk", "name", "description")
    search_fields = ("name",)
    ordering = ("pk",)
    list_filter = ("active",)
    fields = ("pk", "name", "description", "active")
    readonly_fields = ("pk",)
    inlines = [EmployeeInline]


@admin.register(ImageUpload)
class ImageUploadAdmin(admin.ModelAdmin):
    list_display = ("pk", "description")


@admin.register(SecurityMessage)
class SecurityMessageAdmin(admin.ModelAdmin):
    list_display = (
        "date", "organization", "description", "num_viewed", "percent_viewed",
        "active"
    )
    list_filter = ("active", "organization")
    fields = (
        "active", "date", "organization", "description", "content",
        "num_active_employees", "num_viewed", "percent_viewed", "viewed_by",
        "unviewed_by"
    )
    readonly_fields = (
        "num_viewed", "percent_viewed", "viewed_by", "unviewed_by"
    )


@admin.register(TrustedIPAddress)
class TrustedIPAddressAdmin(admin.ModelAdmin):
    list_display = ["address", "address_range_end", "description"]


class UserCreationForm(BaseUserCreationForm):
    password1 = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        help_text=password_validation.password_validators_help_text_html(),
        required=False
    )
    password2 = forms.CharField(
        label=_("Password confirmation"),
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        strip=False,
        help_text=_("Enter the same password as before, for verification."),
        required=False
    )


# admin.site.unregister(User)

# @admin.register(User)
# class UserAdmin(BaseUserAdmin):
#     add_form = UserCreationForm


admin.site.unregister(Group)
class UserInline(admin.TabularInline):
    model = Group.user_set.through
    extra = 0
    ordering = ['user__username']

    def user_full_name(self, obj):
        return f"{obj.user.first_name} {obj.user.last_name}"
    user_full_name.short_description = "Full Name"

    fields = ['user', 'user_full_name']
    readonly_fields = ['user_full_name']


@admin.register(Group)
class GenericGroup(GroupAdmin):
    inlines = [UserInline]


# Provide a link to the detail page of an object
class EditLinkToInlineObject(object):
    def edit_link(self, instance):
        url = reverse('admin:%s_%s_change' % (
            instance._meta.app_label,  instance._meta.model_name),  args=[instance.pk] )
        if instance.pk:
            return mark_safe(u'<a href="{u}">edit</a>'.format(u=url))
        else:
            return ''


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    pass


@admin.register(State)
class StateAdmin(admin.ModelAdmin):
    pass

@admin.register(ZipCode)
class ZipCodeAdmin(admin.ModelAdmin):
    pass