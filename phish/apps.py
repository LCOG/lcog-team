from django.apps import AppConfig


class PhishConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'phish'

    def ready(self):
        import mainsite.admin  # Ensure OrganizationAdmin is registered
        import phish.admin  # Ensure PhishConfigurationInline is available

        from django.contrib import admin
        from mainsite.models import Organization
        from phish.admin import PhishConfigurationInline

        organization_admin = admin.site._registry.get(Organization)
        if not organization_admin:
            return

        existing_inlines = list(getattr(organization_admin, 'inlines', []))
        if PhishConfigurationInline not in existing_inlines:
            organization_admin.inlines = existing_inlines + [
                PhishConfigurationInline
            ]
