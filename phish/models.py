from ckeditor.fields import RichTextField
import secrets

from django.db import models
from django.utils.safestring import mark_safe

from mainsite.models import OrganizationObjectsManager
from people.models import Employee
from phish.helpers import send_training_assignment_notification


class PhishReport(models.Model):
    class Meta:
        verbose_name = 'Phish Report'
        verbose_name_plural = 'Phish Reports'
        ordering = ['-created_at']

    objects = OrganizationObjectsManager()

    STATUS_REPORTED = 'reported'
    STATUS_PHISH = 'phish'
    STATUS_NOT_PHISH = 'not_phish'
    STATUS_TRAINING = 'training'
    STATUS_CHOICES = [
        (STATUS_REPORTED, 'Reported'),
        (STATUS_PHISH, 'Phish'),
        (STATUS_NOT_PHISH, 'Not Phish'),
        (STATUS_TRAINING, 'Training Needed'),
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    sender = models.CharField(max_length=255, blank=True, null=True)
    has_attachments = models.BooleanField(default=False)
    message = models.JSONField()
    additional_info = models.TextField(blank=True, null=True)
    status = models.CharField(
        max_length=255, choices=STATUS_CHOICES, default=STATUS_REPORTED
    )
    processed = models.BooleanField(default=False)


class PhishReportAttachment(models.Model):
    report = models.ForeignKey(
        PhishReport, related_name="attachments", on_delete=models.CASCADE
    )
    attachments = models.FileField(
        upload_to="uploads/phish-attachments", blank=True, null=True
    )


class PhishTask(models.Model):
    def __str__(self):
        return self.name

    organization = models.ForeignKey(
        'mainsite.Organization', on_delete=models.CASCADE
    )
    name = models.CharField(max_length=255)
    order = models.IntegerField(default=0)


class PhishReportTask(models.Model):
    report = models.ForeignKey(PhishReport, on_delete=models.CASCADE)
    task = models.ForeignKey(PhishTask, on_delete=models.CASCADE)
    completed_at = models.DateTimeField(auto_now_add=True)
    completed_by = models.ForeignKey(
        'people.Employee', on_delete=models.SET_NULL, null=True, blank=True
    )


class SyntheticPhishTemplate(models.Model):
    class Meta:
        unique_together = ('organization', 'name', 'version')
        ordering = ['pk']

    def __str__(self):
        return self.name + " v" + str(self.version)

    objects = OrganizationObjectsManager()

    organization = models.ForeignKey(
        'mainsite.Organization', on_delete=models.CASCADE
    )
    active = models.BooleanField(default=True)

    name = models.CharField(max_length=255)
    version = models.IntegerField(default=1)
    subject = models.CharField(max_length=255)
    body = RichTextField(config_name='allow_all_content', help_text=mark_safe(
        "HTML content of the email. Use the following variables to personalize"
        " messages:<ul>"
        "<li>{{user_email}} – user's email</li>"
        "<li>{{user_first_name}} – user's first name</li>"
        "<li>{{user_last_name}} – user's last name</li>"
        "<li>{{user_name}} – user's full name</li>"
        "<li>{{org_name}} – organization's name</li>"
        "<li>{{click_url}} – link which tracks user clicks - configured in your "
        "Organization's Phish Configuration</li>"
        "</ul>"
    ))
    difficulty = models.IntegerField(
        default=1, help_text="1 is easiest, 3 is hardest"
    )
    failure_message = models.TextField(
        blank=True, null=True,
        help_text="Message displayed when the user clicks a phishing link and "
        "fails the simulation, providing feedback to the user. For example, "
        "'The message contained a suspicious link.' or 'Your manager will "
        "never email you asking for your Social Security number.'"
    )

    def save(self, *args, **kwargs):
        if self.difficulty < 1:
            self.difficulty = 1
        elif self.difficulty > 3:
            self.difficulty = 3
        super().save(*args, **kwargs)
    

def generate_click_token():
    return secrets.token_urlsafe(32)


class SyntheticPhish(models.Model):
    class Meta:
        verbose_name_plural = 'Synthetic phishes'

    objects = OrganizationObjectsManager()

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    template = models.ForeignKey(
        SyntheticPhishTemplate, on_delete=models.SET_NULL, null=True
    )
    sent_at = models.DateTimeField(auto_now_add=True)
    click_token = models.CharField(
        max_length=64,
        unique=True,
        db_index=True,
        default=generate_click_token,
        editable=False,
    )
    clicked = models.BooleanField(default=False)
    clicked_at = models.DateTimeField(blank=True, null=True)
    reported = models.BooleanField(default=False)
    reported_at = models.DateTimeField(blank=True, null=True)


class TrainingTemplate(models.Model):
    class Meta:
        unique_together = ('organization', 'name', 'version')
        ordering = ['pk']

    def __str__(self):
        return self.name + " v" + str(self.version)

    objects = OrganizationObjectsManager()

    organization = models.ForeignKey(
        'mainsite.Organization', on_delete=models.CASCADE
    )
    active = models.BooleanField(default=True)

    name = models.CharField(max_length=255)
    version = models.IntegerField(default=1)
    content = RichTextField(config_name='allow_all_content')


class TrainingAssignment(models.Model):
    objects = OrganizationObjectsManager()

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    template = models.ForeignKey(
        TrainingTemplate, on_delete=models.SET_NULL, null=True
    )
    assigned_at = models.DateTimeField(auto_now_add=True)
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(blank=True, null=True)

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new and self.template:
            send_training_assignment_notification(
                self.employee, self.template.name, self.pk
            )


class PhishGroup(models.Model):
    class Meta:
        verbose_name = 'Phish Group'
        verbose_name_plural = 'Phish Groups'

    def __str__(self):
        return self.name

    organization = models.ForeignKey(
        'mainsite.Organization', on_delete=models.CASCADE,
        related_name='phish_groups'
    )
    order = models.IntegerField(default=0)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    color = models.CharField(max_length=32, default='primary')
    members = models.ManyToManyField(
        Employee, related_name='phish_groups', blank=True
    )


class PhishRiskProfile(models.Model):
    class Meta:
        verbose_name = 'Phish Risk Profile'
        verbose_name_plural = 'Phish Risk Profiles'

    def __str__(self):
            return self.name

    organization = models.ForeignKey(
        'mainsite.Organization', on_delete=models.CASCADE,
        related_name='phish_risk_profiles'
    )
    order = models.IntegerField(default=0)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    color = models.CharField(max_length=32, default='primary')
    members = models.ManyToManyField(
        Employee, related_name='phish_risk_profiles', blank=True
    )


class PhishConfiguration(models.Model):
    class Meta:
        verbose_name = 'Phish Configuration'
        verbose_name_plural = 'Phish Configurations'

    def __str__(self):
        return f'Phish Configuration for {self.organization}'

    organization = models.OneToOneField(
        'mainsite.Organization',
        on_delete=models.CASCADE,
        related_name='phish_configuration',
    )
    phish_report_notification_email = models.EmailField(
        blank=True,
        null=True,
        help_text=(
            'Email address that receives a notification when a genuine '
            'phishing report is submitted.'
        ),
    )
    phish_link_domain = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text=(
            'Domain used for synthetic phishing links. For example, '
            '"https://hu1Wei.s.gy" (no trailing slash).'
        ),
    )