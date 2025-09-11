from datetime import datetime, timedelta
import os

from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.db.models import Q
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from mainsite.helpers import record_error, send_email, send_email_multiple
from people.models import Employee
from purchases.models import ExpenseMonth, ExpenseStatement


def send_submitter_monthly_expenses_reminders(sending_user: User):
    # Once fiscal has uploaded the previous month's statements.
    # Submitter submitted last month and there's no draft for this month.
    # Submitter has an unsubmitted draft for this month.
    current_site = Site.objects.get_current()
    expenses_url = current_site.domain + '/expenses/submit'
    profile_url = current_site.domain + '/profile'
    
    html_template = \
        '../templates/email/expenses/submitter-monthly-reminder.html'

    today = datetime.now().date()
    # Current month is the month that just ended.
    # Previous month is the month before that.
    curr_month_date = today.replace(day=1) - timedelta(days=1)
    prev_month_date = curr_month_date.replace(day=1) - timedelta(days=1)
    month_before_that_date = prev_month_date.replace(day=1) - timedelta(days=1)
    curr_month_name = curr_month_date.strftime('%B')

    recipients = []
    subs = Employee.objects.filter(user__groups__name='Expense Submitter')
    for sub in subs:
        if sub.should_receive_email_of_type('expenses', ''):
            # Do they have an unsubmitted draft for this month?
            em = ExpenseMonth.objects.filter(
                purchaser=sub,
                year=curr_month_date.year,
                month=curr_month_date.month,
                status=ExpenseMonth.STATUS_DRAFT
            ).exists()
            if em:
                recipients.append([sub.user.email, 'draft'])
            else:
                # Is there a statement for a card of theirs this month?
                # Don't send if they have a submitted ExpenseMonth this month.
                es = ExpenseStatement.objects.filter(
                    card__assignee=sub,
                    year=curr_month_date.year,
                    month=curr_month_date.month
                ).exists()
                em_this_month = ExpenseMonth.objects.filter(
                    purchaser=sub, year=curr_month_date.year,
                    month=curr_month_date.month
                ).exists()
                if es and not em_this_month:
                    recipients.append([sub.user.email, 'statement'])
                else:
                    # Did they submit last month or the month before,
                    # but not this month?
                    em_last_month = ExpenseMonth.objects.filter(
                        purchaser=sub, year=prev_month_date.year,
                        month=prev_month_date.month
                    ).exists()
                    em_month_before_that = ExpenseMonth.objects.filter(
                        purchaser=sub, year=month_before_that_date.year,
                        month=month_before_that_date.month
                    ).exists()
                    if (
                        em_last_month or em_month_before_that
                    ) and not em_this_month:
                        recipients.append([sub.user.email, 'last_month'])
    for recipient in recipients:
        if sending_user.is_anonymous:
            # TODO: Not sure why these are anonymous, but log them for now.
            # Log error if sending_user is anonymous
            record_error(
                'send_submitter_monthly_expenses_reminders',
                'Anonymous user attempted to send reminders.',
                other_info={
                    'sending_user': sending_user,
                    'recipient': recipient
                }
            )
            continue # Continue to next item in loop. Don't send anything.
        sender = sending_user.employee.name if \
            sending_user.employee and sending_user.employee.name else \
            sending_user.username
        html_message = render_to_string(html_template, { 'context': {
            'curr_month_name': curr_month_name,
            'message_type': recipient[1],
            'sender_name': sender,
            'expenses_url': expenses_url,
            'profile_url': profile_url,
            'from_email': os.environ.get('FROM_EMAIL')
        }, })
        plaintext_message = strip_tags(html_message)
        send_email_multiple(
            [recipient[0]],
            ['payadmin@lcog-or.gov'],
            f'Time to enter { curr_month_name } expenses',
            plaintext_message,
            html_message
        )
    return len(recipients)


def send_submitter_weekly_revise_reminders():
    # Every week on Friday at 3PM
    # Submitter needs to revise and resubmit
    current_site = Site.objects.get_current()
    expenses_url = current_site.domain + '/expenses/submit'
    profile_url = current_site.domain + '/profile'
    
    html_template = \
        '../templates/email/expenses/submitter-weekly-revise-reminder.html'

    recipients = []
    subs = Employee.objects.filter(user__groups__name='Expense Submitter')
    for sub in subs:
        if sub.should_receive_email_of_type('expenses', ''):
            # Do they need to revise and resubmit?
            em = ExpenseMonth.objects.filter(
                purchaser=sub, status__in=[
                    ExpenseMonth.STATUS_APPROVER_DENIED,
                    ExpenseMonth.STATUS_DIRECTOR_DENIED,
                    ExpenseMonth.STATUS_FISCAL_DENIED
                ]
            ).exists()
            if em:
                recipients.append(sub.user.email)
    for recipient in recipients:
        html_message = render_to_string(html_template, { 'context': {
            'expenses_url': expenses_url,
            'profile_url': profile_url,
            'from_email': os.environ.get('FROM_EMAIL')
        }, })
        plaintext_message = strip_tags(html_message)
        send_email(
            recipient,
            f'Revise and resubmit expenses',
            plaintext_message,
            html_message
        )
    
    return len(recipients)


def send_submitter_denial_notification(submitter: Employee):
    # Direct notifications
    # Approver denied, alert submitter
    # Director denied, alert submitter
    # Fiscal denied, alert submitter
    current_site = Site.objects.get_current()
    expenses_url = current_site.domain + '/expenses/submit'
    profile_url = current_site.domain + '/profile'
    
    html_template = \
        '../templates/email/expenses/submitter-denial-notification.html'
    
    if submitter.should_receive_email_of_type('expenses', ''):
        html_message = render_to_string(html_template, { 'context': {
            'expenses_url': expenses_url,
            'profile_url': profile_url,
            'from_email': os.environ.get('FROM_EMAIL')
        }, })
        plaintext_message = strip_tags(html_message)
        send_email(
            submitter.user.email,
            f'Expense submission denied',
            plaintext_message,
            html_message
        )
        return 1
    else:
        return 0


def send_approver_weekly_approve_reminders():
    # Every week on Monday, Wednesday, and Friday at 3PM
    # Approver has GLs to approve
    current_site = Site.objects.get_current()
    expenses_url = current_site.domain + '/expenses/approve'
    profile_url = current_site.domain + '/profile'
    
    html_template = \
        '../templates/email/expenses/approver-weekly-approve-reminder.html'

    recipients = []
    approvers = Employee.objects.filter(user__groups__name='Expense Approver')
    for approver in approvers:
        if approver.should_receive_email_of_type('expenses', ''):
            # Do they have GLs to approve?
            gls = approver.expense_gls.filter(
                expense__month__status=ExpenseMonth.STATUS_SUBMITTED,
                approved_at__isnull=True
            ).exists()
            if gls:
                recipients.append(approver.user.email)
    for recipient in recipients:
        html_message = render_to_string(html_template, { 'context': {
            'expenses_url': expenses_url,
            'profile_url': profile_url,
            'from_email': os.environ.get('FROM_EMAIL')
        }, })
        plaintext_message = strip_tags(html_message)
        send_email(
            recipient,
            f'Expenses to approve',
            plaintext_message,
            html_message
        )
    
    return len(recipients)


def send_directors_weekly_approve_reminders():
    # Every week on Friday at 3PM
    # Director has expensemonths to approve
    current_site = Site.objects.get_current()
    expenses_url = current_site.domain + '/expenses/director'
    profile_url = current_site.domain + '/profile'
    
    html_template = \
        '../templates/email/expenses/' + \
        'directors-fiscal-weekly-approve-reminder.html'

    recipients = []
    directors = Employee.objects.filter(is_division_director=True)
    for director in directors:
        if director.should_receive_email_of_type('expenses', ''):
            # Do they have ExpenseMonths to approve?
            ems = ExpenseMonth.objects.filter(
                status=ExpenseMonth.STATUS_APPROVER_APPROVED,
                card__requires_director_approval=True,
                card__director=director,
            ).exists()
            if ems:
                recipients.append(director.user.email)
    for recipient in recipients:
        html_message = render_to_string(html_template, { 'context': {
            'expenses_url': expenses_url,
            'profile_url': profile_url,
            'from_email': os.environ.get('FROM_EMAIL')
        }, })
        plaintext_message = strip_tags(html_message)
        send_email(
            recipient,
            f'Expenses to approve',
            plaintext_message,
            html_message
        )
    
    return len(recipients)


def send_fiscal_weekly_approve_reminders():
    # Every week on Friday at 3PM
    # Fiscal has expensemonths to approve
    current_site = Site.objects.get_current()
    expenses_url = current_site.domain + '/expenses/fiscal'
    profile_url = current_site.domain + '/profile'
    
    html_template = \
        '../templates/email/expenses/' + \
        'directors-fiscal-weekly-approve-reminder.html'

    recipients = []
    fiscals = Employee.objects.filter(user__groups__name='Fiscal Employee')
    for fiscal in fiscals:
        if fiscal.should_receive_email_of_type('expenses', ''):
            # Do they have ExpenseMonths to approve?
            ems = ExpenseMonth.objects.filter(
                Q(status=ExpenseMonth.STATUS_DIRECTOR_APPROVED) |
                Q(
                    status=ExpenseMonth.STATUS_APPROVER_APPROVED,
                    card__requires_director_approval=False
                )
            ).exists()
            if ems:
                recipients.append(fiscal.user.email)
    for recipient in recipients:
        html_message = render_to_string(html_template, { 'context': {
            'expenses_url': expenses_url,
            'profile_url': profile_url,
            'from_email': os.environ.get('FROM_EMAIL')
        }, })
        plaintext_message = strip_tags(html_message)
        send_email(
            recipient,
            f'Expenses to approve',
            plaintext_message,
            html_message
        )
    
    return len(recipients)

