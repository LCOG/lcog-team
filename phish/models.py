from ckeditor.fields import RichTextField
from django.db import models

from mainsite.models import OrganizationObjectsManager
from people.models import Employee


class PhishReport(models.Model):
    class Meta:
        verbose_name = 'Phish Report'
        verbose_name_plural = 'Phish Reports'
        ordering = ['-created_at']

    objects = OrganizationObjectsManager()

    STATUS_REPORTED = 'reported'
    STATUS_PHISH = 'phish'
    STATUS_NOT_PHISH = 'not_phish'
    STATUS_CHOICES = [
        (STATUS_REPORTED, 'Reported'),
        (STATUS_PHISH, 'Phish'),
        (STATUS_NOT_PHISH, 'Not Phish'),
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    message = models.JSONField()
    additional_info = models.TextField(blank=True, null=True)
    status = models.CharField(
        max_length=255, choices=STATUS_CHOICES, default=STATUS_REPORTED
    )
    processed = models.BooleanField(default=False)


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
    body = RichTextField()
    difficulty = models.IntegerField(
        default=1, help_text="1 is easiest, 3 is hardest"
    )

    def save(self, *args, **kwargs):
        if self.difficulty < 1:
            self.difficulty = 1
        elif self.difficulty > 3:
            self.difficulty = 3
        super().save(*args, **kwargs)
    

class SyntheticPhish(models.Model):
    class Meta:
        verbose_name_plural = 'Synthetic phishes'

    objects = OrganizationObjectsManager()

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    template = models.ForeignKey(
        SyntheticPhishTemplate, on_delete=models.SET_NULL, null=True
    )
    sent_at = models.DateTimeField(auto_now_add=True)
    clicked = models.BooleanField(default=False)
    reported = models.BooleanField(default=False)
    reported_at = models.DateTimeField(blank=True, null=True)


class TrainingTemplate(models.Model):
    class Meta:
        unique_together = ('organization', 'name', 'version')

    def __str__(self):
        return self.name + " v" + str(self.version)

    objects = OrganizationObjectsManager()

    organization = models.ForeignKey(
        'mainsite.Organization', on_delete=models.CASCADE
    )
    active = models.BooleanField(default=True)

    name = models.CharField(max_length=255)
    version = models.IntegerField(default=1)
    content = RichTextField()


class TrainingAssignment(models.Model):
    objects = OrganizationObjectsManager()

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    template = models.ForeignKey(
        TrainingTemplate, on_delete=models.SET_NULL, null=True
    )
    assigned_at = models.DateTimeField(auto_now_add=True)
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(blank=True, null=True)


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