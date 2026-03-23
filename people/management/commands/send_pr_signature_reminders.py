from datetime import datetime

from django.core.management.base import BaseCommand, CommandError

from people.helpers import send_pr_signature_reminders


class Command(BaseCommand):
    help = 'Sends follow-up reminder emails for needed performance review ' \
           'signatures.'

    def handle(self, *args, **options):
        count = send_pr_signature_reminders()
        message = f'{ datetime.now() } - Sent follow-up reminder emails to {count} managers.'
        self.stdout.write(self.style.SUCCESS(message))