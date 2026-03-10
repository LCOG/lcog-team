from datetime import datetime

from django.core.management.base import BaseCommand, CommandError

from people.helpers import send_manager_pr_notices


class Command(BaseCommand):
    help = 'Sends reminder emails for upcoming performance reviews'

    def handle(self, *args, **options):
        count = send_manager_pr_notices()
        message = f'{ datetime.now() } - Sent emails to {count} managers.'
        self.stdout.write(self.style.SUCCESS(message))