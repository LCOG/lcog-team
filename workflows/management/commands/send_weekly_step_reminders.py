from datetime import datetime

from django.core.management.base import BaseCommand

from workflows.helpers import send_weekly_step_reminders


class Command(BaseCommand):
    help = 'Sends weekly step reminder email to workflow workhorses'

    def handle(self, *args, **options):
        num_employees = send_weekly_step_reminders()
        dt = datetime.now()
        message = f'{dt} - Sent weekly step reminders to ' + \
            f'{num_employees} workflow workhorses.'
        self.stdout.write(self.style.SUCCESS(message))
