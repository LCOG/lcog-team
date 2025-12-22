from django.db import models

from mainsite.models import OrganizationObjectsManager
from people.models import Employee


class PhishReport(models.Model):
    objects = OrganizationObjectsManager()

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    message = models.JSONField()
    organic = models.BooleanField(default=True)
    processed = models.BooleanField(default=False)