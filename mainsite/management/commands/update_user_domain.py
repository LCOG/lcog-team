from datetime import datetime

from django.apps import apps
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Updates user email domains from @lcog.org to @lcog-or.gov'

    def handle(self, *args, **options):
        User = apps.get_model('auth', 'User')
        for user in User.objects.filter(email__endswith='@lcog.org'):
            new_email = user.email.replace('@lcog.org', '@lcog-or.gov')
            user.email = new_email
            user.username = new_email
            user.save(update_fields=['email', 'username'])