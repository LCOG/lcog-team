from django.db import models
from django.utils import timezone
from django.utils.translation import gettext as _

from ckeditor.fields import RichTextField


class ActiveManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(active=True)


class InactiveManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(active=False)


class ActiveMixin:
    class Meta:
        abstract = True
    
    active = models.BooleanField(default=True)

    objects = models.Manager()
    active_objects = ActiveManager()
    inactive_objects = InactiveManager()


class Organization(models.Model, ActiveMixin):
    class Meta:
        verbose_name = _("Organization")
        verbose_name_plural = _("Organizations")

    def __str__(self):
        return self.name

    name = models.CharField(_("name"), max_length=255)
    description = models.TextField(_("description"), blank=True, null=True)
    active = models.BooleanField(default=True) # Define explicitly here in order to filter in admin


class OrganizationObjectsQuerySet(models.QuerySet):
    def for_organization(self, organization):
        return self.filter(employee__organization=organization)
    
    def for_employee(self, employee):
        return self.filter(employee__organization=employee.organization)


class OrganizationObjectsManager(models.Manager):
    def get_queryset(self):
        return OrganizationObjectsQuerySet(self.model, using=self._db)
    
    def for_organization(self, organization):
        return self.get_queryset().for_organization(organization)

    def for_employee(self, employee):
        return self.get_queryset().for_employee(employee)


class ImageUpload(models.Model):
    description = models.CharField(_("description"), max_length=255)
    image = models.ImageField(upload_to="uploads/image-upload")


class SecurityMessage(models.Model):
    class Meta:
        verbose_name = _("Security Message")
        verbose_name_plural = _("Security Messages")
        ordering = ["active", "-pk"]
        get_latest_by = ("date")

    active = models.BooleanField(default=False)
    description = models.CharField(_("description"), max_length=255)
    date = models.DateField(default=timezone.now)
    content = RichTextField()
    num_active_employees = models.IntegerField(
        _("number of active employees at time of creation"), default=0
    )
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)

    @property
    def num_viewed(self):
        return self.viewedsecuritymessage_set.count()

    @property
    def percent_viewed(self):
        if self.num_active_employees:
            return f'{
                round(self.num_viewed / self.num_active_employees * 100, 2)
            }%'
        else:
            return '0%'

    def __str__(self):
        return self.description
    
    def save(self, *args, **kwargs):
        if not self.num_active_employees:
            from people.models import Employee # Avoid circular import
            self.num_active_employees = Employee.objects.filter(
                active=True, temporary=False, organization=self.organization
            ).count()
        super().save(*args, **kwargs)
    
    @property
    def viewed_by(self):
        viewed = list(self.viewedsecuritymessage_set.all().values_list(
            'employee__user__first_name', 'employee__user__last_name'
        ))
        return ', '.join([f'{name} {last}' for name, last in viewed])
    
    @property
    def unviewed_by(self):
        from people.models import Employee # Avoid circular import
        unviewed = list(
            Employee.objects\
                .filter(
                    active=True, temporary=False,
                    organization=self.organization
                )\
                .exclude(viewedsecuritymessage__security_message=self)\
                .values_list('user__first_name', 'user__last_name')
        )
        return ', '.join([f'{name} {last}' for name, last in unviewed])


class TrustedIPAddress(models.Model):
    """
    Allow these addresses to access the Desk Reservation App
    """
    
    class Meta:
        verbose_name = _("Trusted IP Address")
        verbose_name_plural = _("Trusted IP Addresses")

    def __str__(self):
        return _("Trusted IP Address")

    address = models.GenericIPAddressField()
    address_range_end = models.GenericIPAddressField(
        blank=True,
        null=True,
        help_text=_("Optional. If you want to allow a range of IP addresses, "
                    "enter the end of the range here.")
    )
    description = models.CharField(max_length=255)


class State(models.Model):
    class Meta:
        verbose_name = _("State")
        verbose_name_plural = _("States")

    def __str__(self):
        return self.name

    name = models.CharField(_("name"), max_length=255)


class ZipCode(models.Model):
    class Meta: 
        verbose_name = _("Zip Code")
        verbose_name_plural = _("Zip Codes")

    def __str__(self):
        return self.code

    code = models.CharField(_("code"), max_length=5)
    

class City(models.Model):
    class Meta:
        verbose_name = _("City")
        verbose_name_plural = _("Cities")

    def __str__(self):
        return self.name

    name = models.CharField(_("name"), max_length=255)
    state = models.ForeignKey(State, on_delete=models.CASCADE)



LANGUAGE_CHOICES = (
    ("asl", _("American Sign Language")),
    ("ar", _("Arabic")),
    ("bn", _("Bengali")),
    ("zh", _("Chinese")),
    ("hr", _("Croatian")),
    ("cs", _("Czech")),
    ("da", _("Danish")),
    ("nl", _("Dutch")),
    ("fi", _("Finnish")),
    ("fr", _("French")),
    ("de", _("German")),
    ("el", _("Greek")),
    ("gu", _("Gujarati")),
    ("ht", _("Haitian Creole")),
    ("he", _("Hebrew")),
    ("hi", _("Hindi")),
    ("hu", _("Hungarian")),
    ("id", _("Indonesian")),
    ("it", _("Italian")),
    ("ja", _("Japanese")),
    ("ko", _("Korean")),
    ("lv", _("Latvian")),
    ("lt", _("Lithuanian")),
    ("no", _("Norwegian")),
    ("fa", _("Persian")),
    ("pl", _("Polish")),
    ("pt", _("Portuguese")),
    ("ro", _("Romanian")),
    ("ru", _("Russian")),
    ("sr", _("Serbian")),
    ("sk", _("Slovak")),
    ("sl", _("Slovenian")),
    ("es", _("Spanish")),
    ("sw", _("Swahili")),
    ("sv", _("Swedish")),
    ("tl", _("Tagalog")),
    ("ta", _("Tamil")),
    ("th", _("Thai")),
    ("tr", _("Turkish")),
    ("ur", _("Urdu")),
    ("vi", _("Vietnamese")),
    ("cy", _("Welsh")),
    ("xh", _("Xhosa")),
    ("zu", _("Zulu")),
)