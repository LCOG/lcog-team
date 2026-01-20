import datetime
import logging
import os
import pytz
from rest_framework.test import APIRequestFactory
import requests
import urllib.parse

from django.apps import apps
from django.contrib.sites.models import Site
from django.core.mail import EmailMultiAlternatives, send_mail
from django.urls import reverse

error_logger = logging.getLogger('watchtower-error-logger')
email_logger = logging.getLogger('watchtower-email-logger')

SEND_MANAGER_FIRST_REMINDER_NEW_PR_DAYS_BEFORE = 60
SEND_MANAGER_SECOND_REMINDER_NEW_PR_DAYS_BEFORE = 45
SEND_MANAGER_PERSISTENT_REMINDERS_NEW_PR_DAYS_BEFORE = 30

EMPLOYEE_SIGNATURE_REMINDER = 2
MANAGER_SIGNATURE_REMINDER = 2
MANAGER_SIGNATURE_REMINDER_SUBSEQUENT = 1

ESCALATION_TO_NEXT_MANAGER_REMINDER = 7

HR_SIGNATURE_REMINDER_SUBSEQUENT = 1

ED_SIGNATURE_REMINDER_SUBSEQUENT = 1


def readable_date(date):
    local_date = date.astimezone(pytz.timezone('America/Los_Angeles'))
    return local_date.strftime('%m/%d/%y')

def get_host_url(request):
    host = request.get_host()
    if request.is_secure():
        return f'https://{ host }/'
    else:
        return f'http://{ host }/' 


def record_error(
    message, error, request=None, traceback=None, other_info=None
):
    message = 'Environment: ' + os.environ.get('ENVIRONMENT') + '\n' + message
    message += '\n'
    message += 'User: ' + str(request.user) if request else 'None'
    message += '\n'
    message += 'Error: ' + str(error)
    message += '\n'
    message += str(request.__dict__) if request else 'None'
    message += '\n'
    message += str(traceback)
    message += '\n'
    message += 'Other Info: ' + str(other_info) if other_info else 'None'
    error_logger.error(message)

def record_email_sent(subject='', body='', to_addresses=[], cc_addresses=[]):
    message = 'Environment: ' + os.environ.get('ENVIRONMENT') + '\n'
    message += 'To: ' + ', '.join(to_addresses) + '\n'
    message += 'CC: ' + ', '.join(cc_addresses) + '\n'
    message += 'Subject: ' + subject + '\n'
    message += 'Body: ' + body
    email_logger.info(message)

def send_email(to_address, subject, body, html_body):
    env = os.getenv('ENVIRONMENT')
    if env == 'DEV':
        subject = f'TEST FROM DEV: {subject}'
        body = f'THIS IS A TEST EMAIL\n{body}'
        html_body = \
            f'<div style="color: red;">THIS IS A TEST EMAIL</div>{html_body}'
    elif env == 'STAGING':
        subject = f'TEST FROM STAGING: {subject}'
        body = f'THIS IS A TEST EMAIL\n{body}'
        html_body = \
            f'<div style="color: red;">THIS IS A TEST EMAIL</div>{html_body}'
    try:
        sent_email = send_mail(
            subject,
            body,
            from_email=os.environ.get('FROM_EMAIL'),
            recipient_list=[to_address],
            # auth_user=os.environ.get('FROM_EMAIL_USERNAME'),
            # auth_password=os.environ.get('FROM_EMAIL_PASSWORD'),
            html_message=html_body
        )
        record_email_sent(subject, body, [to_address])
        return sent_email
    except Exception as e:
        record_error('Error sending email', e)

def send_email_multiple(
    to_addresses=[], cc_addresses=[], subject='', text_body='', html_body=''
):
    env = os.getenv('ENVIRONMENT')
    if env == 'DEV':
        subject = f'TEST FROM DEV: {subject}'
        text_body = f'THIS IS A TEST EMAIL\n{text_body}'
        html_body = \
            f'<div style="color: red;">THIS IS A TEST EMAIL</div>{html_body}'
    elif env == 'STAGING':
        subject = f'TEST FROM STAGING: {subject}'
        text_body = f'THIS IS A TEST EMAIL\n{text_body}'
        html_body = \
            f'<div style="color: red;">THIS IS A TEST EMAIL</div>{html_body}'
    email = EmailMultiAlternatives(
        subject=subject, body=text_body,
        from_email=os.environ.get('FROM_EMAIL'), to=to_addresses,
        cc=cc_addresses
    )
    email.attach_alternative(html_body, "text/html")
    try:
        sent_email = email.send()
        record_email_sent(subject, text_body, to_addresses, cc_addresses)
        return sent_email
    except Exception as e:
        record_error('Error sending email', e)

def send_evaluation_written_email_to_employee(employee, review):
    # Notification #5
    SignatureReminder = apps.get_model('people.SignatureReminder')
    current_site = Site.objects.get_current()
    url = current_site.domain + '/pr/' + str(review.pk)
    send_email(
        employee.user.email,
        f'Signature required: {review.employee.manager.name} has completed your performance evaluation',
        f'Your manager {review.employee.manager.name} has completed your evaluation for an upcoming performance review, which requires your signature. View and sign here: {url}',
        f'Your manager {review.employee.manager.name} has completed your evaluation for an upcoming performance review, which requires your signature. View and sign here: {url}'
    )
    next_reminder = datetime.datetime.today() + datetime.timedelta(days=EMPLOYEE_SIGNATURE_REMINDER)
    SignatureReminder.objects.create(review=review, employee=employee, next_date=next_reminder)


def send_signature_email_to_manager(employee, review):
    # Notification #10
    SignatureReminder = apps.get_model('people.SignatureReminder')
    current_site = Site.objects.get_current()
    url = current_site.domain + '/pr/' + str(review.pk)
    send_email(
        employee.user.email,
        f'Signature required: Performance evaluation for {review.employee.name}',
        f'{review.employee.manager.name} has completed an evaluation for {review.employee.name}, which requires your signature. View and sign here: {url}',
        f'{review.employee.manager.name} has completed an evaluation for {review.employee.name}, which requires your signature. View and sign here: {url}'
    )
    next_reminder = datetime.datetime.today() + datetime.timedelta(days=MANAGER_SIGNATURE_REMINDER)
    SignatureReminder.objects.create(review=review, employee=employee, next_date=next_reminder)


def send_signature_email_to_hr_manager(review):
    # Notification #13
    hr_manager = apps.get_model('people.Employee').objects.get(
        organization=review.employee.organization, is_hr_manager=True
    )
    send_signature_email_to_manager(hr_manager, review)


def send_signature_email_to_executive_director(review):
    # Notification #16
    executive_director = apps.get_model('people.Employee').objects.get(
        organization=review.employee.organization, is_executive_director=True
    )
    send_signature_email_to_manager(executive_director, review)


def send_pr_completed_email(review):
    # Notification #19
    pr_completed_employees = apps.get_model('people.Employee').objects.filter(
        user__groups__name='PR Completed Employees',
        organization=review.employee.organization
    )
    hr_manager = apps.get_model('people.Employee').objects.get(
        organization=review.employee.organization, is_hr_manager=True
    )
    current_site = Site.objects.get_current()
    url = current_site.domain + '/print/pr/' + str(review.pk)
    send_email_multiple(
        to_addresses=pr_completed_employees.values_list('user__email', flat=True),
        subject='A Performance Evaluation has been completed',
        text_body=f'{hr_manager.name} has approved a performance evaluation for {review.employee.name}. Please print it here: {url}',
        html_body=f'{hr_manager.name} has approved a performance evaluation for {review.employee.name}. Please print it here: {url}'
    )


def send_pr_reminder_emails():
    # TODO: Won't work with multiple executive directors. This needs to loop thru all organizations.
    current_site = Site.objects.get_current()
    Employee = apps.get_model('people.Employee')
    PerformanceReview = apps.get_model('people.PerformanceReview')
    Signature = apps.get_model('people.Signature')
    SignatureReminder = apps.get_model('people.SignatureReminder')
    today = datetime.date.today()
    # TODO: Remove after testing done
    # today = datetime.date.today() + datetime.timedelta(days=2)
    # today = datetime.date.today() + datetime.timedelta(days=7)
    hr_manager = Employee.objects.get(is_hr_manager=True)
    executive_director = Employee.objects.get(is_executive_director=True)

    users = {}
    notifications = {
        'review_to_write': [], 'review_to_write_other': [],
        'signature_required': [], 'signature_required_other': []
    }
    
    def add_reminder(email, notification_type, subject, text_body, html_body):
        if not email in users.keys():
            users[email] = {
                'review_to_write': [], 'review_to_write_other': [],
                'signature_required': [], 'signature_required_other': []
            }
        users[email][notification_type].append([subject, text_body, html_body])
    
    #########################################################
    ### Reminders to get a manager to write an evaluation ###
    #########################################################
    for pr in PerformanceReview.objects.filter(status=PerformanceReview.NEEDS_EVALUATION):
        days_until_due = pr.days_until_due()
        if days_until_due in [60, 45]:
            url = current_site.domain + '/pr/' + str(pr.pk)
            # Notification #1
            # Notification #2
            add_reminder(pr.employee.manager.user.email, 'review_to_write', 'Upcoming performance review', f'A review for {pr.employee.name} is due in {pr.days_until_due()} days on {pr.effective_date}. Write an evaluation here: {url}', f'A review for {pr.employee.name} is due in {pr.days_until_due()} days on {pr.effective_date}. Write an evaluation here: <a href="{url}">{url}</a>')
        if days_until_due <= 30:
            url = current_site.domain + '/pr/' + str(pr.pk)
            # Notification #3
            add_reminder(pr.employee.manager.user.email, 'review_to_write', 'Performance review behind schedule', f'A review for {pr.employee.name} is due in {pr.days_until_due()} days on {pr.effective_date}. Write an evaluation here: {url}', f'A review for {pr.employee.name} is due in {pr.days_until_due()} days on {pr.effective_date}. Write an evaluation here: <a href="{url}">{url}</a>')
            # Notification #4: Reminder to manager's manager
            add_reminder(pr.employee.manager.manager.user.email, 'review_to_write_other', 'Performance review behind schedule', f'A review for {pr.employee.name} is due from {pr.employee.manager.name} in {pr.days_until_due()} days on {pr.effective_date}. Contact them here: {pr.employee.manager.user.email}', f'A review for {pr.employee.name} is due from {pr.employee.manager.name} in {pr.days_until_due()} days on {pr.effective_date}. Contact them here: <a href="mailto:{pr.employee.manager.user.email}">{pr.employee.manager.user.email}</a>')
    
    #################################################################
    ### Reminders to get an employee to sign their own evaluation ###
    #################################################################
    for pr in PerformanceReview.objects.filter(status=PerformanceReview.EVALUATION_WRITTEN):
        url = current_site.domain + '/pr/' + str(pr.pk)
        employee = pr.employee
        employee_signatures = Signature.objects.filter(review=pr, employee=employee)
        if employee_signatures.count() == 0:
            employee_reminders = SignatureReminder.objects.filter(review=pr, employee=employee)
            employee_reminder = None
            manager_reminder = None
            if employee_reminders.count():
                employee_reminder = employee_reminders.latest()
                manager_reminder = employee_reminders.earliest()

            # Reminder to employee
            if employee_reminder:
                if today >= employee_reminder.next_date:
                    # Notification #6: Remind employee a subsequent time to sign own evaluation
                    add_reminder(employee.user.email, 'signature_required', f'Signature required: {employee.manager.name} has completed your performance evaluation', f'Your manager {employee.manager.name} has completed your evaluation for an upcoming performance review, which requires your signature. View and sign here: {url}', f'Your manager {employee.manager.name} has completed your evaluation for an upcoming performance review, which requires your signature. View and sign here: <a href="{url}">{url}</a>')
                    next_reminder = datetime.datetime.today() + datetime.timedelta(days=EMPLOYEE_SIGNATURE_REMINDER)
                    SignatureReminder.objects.create(review=pr, employee=employee, next_date=next_reminder)
            else:
                # Notification #6
                add_reminder(employee.user.email, 'signature_required', f'Signature required: {employee.manager.name} has completed your performance evaluation', f'Your manager {employee.manager.name} has completed your evaluation for an upcoming performance review, which requires your signature. View and sign here: {url}', f'Your manager {employee.manager.name} has completed your evaluation for an upcoming performance review, which requires your signature. View and sign here: <a href="{url}">{url}</a>')
                next_reminder = datetime.datetime.today() + datetime.timedelta(days=EMPLOYEE_SIGNATURE_REMINDER)
                SignatureReminder.objects.create(review=pr, employee=employee, next_date=next_reminder)
            
            # Reminder to their manager
            if manager_reminder:
                if today >= manager_reminder.date + datetime.timedelta(days=ESCALATION_TO_NEXT_MANAGER_REMINDER):
                    # Notification #7: Escalate to employee's manager to get employee to sign their evaluation
                    add_reminder(employee.manager.user.email, 'signature_required_other', f'A performance review is behind schedule', f'A signature is required by {employee.name} for their evaluation. Contact them here: {employee.user.email}', f'A signature is required by {employee.name} for their evaluation. Contact them here: <a href="mailto:{employee.user.email}">{employee.user.email}</a>')
                    # We don't need to make another reminder because this same reminder will trigger every subsequent day
        
    #####################################################################################
    ### Reminders to get managers to review and sign a written performance evaluation ###
    #####################################################################################
    for pr in PerformanceReview.objects.filter(status=PerformanceReview.EVALUATION_WRITTEN):
        url = current_site.domain + '/pr/' + str(pr.pk)
        
        # Determine which manager needs to sign the PR next
        employee = pr.employee.manager
        while True:
            signatures = Signature.objects.filter(review=pr, employee=employee)
            if signatures.count() > 0:
                if employee.manager:
                    employee = employee.manager
                else:
                    employee = None
            else:
                break
        
        # Reminder to manager
        reminders = SignatureReminder.objects.filter(review=pr, employee=employee)
        if reminders.count():
            if today >= reminders.latest().next_date: # If it's time to send another reminder
                if employee == pr.employee.manager:
                    # Notification #8: Manager reminded to sign an evaluation they wrote
                    add_reminder(employee.user.email, 'signature_required', f'Signature required: Performance evaluation for {pr.employee.name}', f'Your evaluation for {pr.employee.name} requires your signature. View and sign here: {url}', f'Your evaluation for {pr.employee.name} requires your signature. View and sign here: <a href="{url}">{url}</a>')
                    next_reminder = datetime.datetime.today() + datetime.timedelta(days=MANAGER_SIGNATURE_REMINDER)
                    SignatureReminder.objects.create(review=pr, employee=employee, next_date=next_reminder)
                else:
                    # Notification #11: Upper manager reminded to sign an evaluation
                    add_reminder(employee.user.email, 'signature_required', f'Signature required: Performance evaluation for {pr.employee.name}', f'{pr.employee.manager.name} has completed an evaluation for {pr.employee.name}, which requires your signature. View and sign here: {url}', f'{pr.employee.manager.name} has completed an evaluation for {pr.employee.name}, which requires your signature. View and sign here: <a href="{url}">{url}</a>')
                    next_reminder = datetime.datetime.today() + datetime.timedelta(days=MANAGER_SIGNATURE_REMINDER)
                    SignatureReminder.objects.create(review=pr, employee=employee, next_date=next_reminder)

                # Reminder to upper manager
                if reminders.count():
                    earliest_reminder = reminders.earliest()
                    if today >= earliest_reminder.date + datetime.timedelta(days=ESCALATION_TO_NEXT_MANAGER_REMINDER):
                        # Notification #9, Notification #12: Escalate to manager's manager to get manager to sign evaluation
                        add_reminder(employee.manager.user.email, 'signature_required_other', f'A performance review is behind schedule', f'A signature is required by {employee.name} for their evaluation. Contact them here: {employee.user.email}', f'A signature is required by {employee.name} for their evaluation. Contact them here: <a href="mailto:{employee.user.email}">{employee.user.email}</a>')
                        # We don't need to make another reminder because this same reminder will trigger every subsequent day
        else:
            if employee == pr.employee.manager:
                # Notification #8
                add_reminder(employee.user.email, 'signature_required', f'Signature required: Performance evaluation for {pr.employee.name}', f'Your evaluation for {pr.employee.name} requires your signature. View and sign here: {url}', f'Your evaluation for {pr.employee.name} requires your signature. View and sign here: <a href="{url}">{url}</a>')
                next_reminder = datetime.datetime.today() + datetime.timedelta(days=MANAGER_SIGNATURE_REMINDER)
                SignatureReminder.objects.create(review=pr, employee=employee, next_date=next_reminder)
            else:
                # Notification #11
                add_reminder(employee.user.email, 'signature_required', f'Signature required: Performance evaluation for {pr.employee.name}', f'{pr.employee.manager.name} has completed an evaluation for {pr.employee.name}, which requires your signature. View and sign here: {url}', f'{pr.employee.manager.name} has completed an evaluation for {pr.employee.name}, which requires your signature. View and sign here: <a href="{url}">{url}</a>')
                next_reminder = datetime.datetime.today() + datetime.timedelta(days=MANAGER_SIGNATURE_REMINDER)
                SignatureReminder.objects.create(review=pr, employee=employee, next_date=next_reminder)

    ###########################################################################################
    ### Reminders to get the HR manager to review and sign a written performance evaluation ###
    ###########################################################################################
    for pr in PerformanceReview.objects.filter(status=PerformanceReview.EVALUATION_APPROVED):
        url = current_site.domain + '/pr/' + str(pr.pk)
        employee = pr.employee
        hr_signatures = Signature.objects.filter(review=pr, employee=hr_manager)
        hr_reminder = None
        ed_reminder = None
        if hr_signatures.count() == 0:
            hr_reminders = SignatureReminder.objects.filter(review=pr, employee=hr_manager)
            hr_reminder = hr_reminders.latest()
            ed_reminder = hr_reminders.earliest()
            
            def add_hr_reminder():
                add_reminder(hr_manager.user.email, 'signature_required', f'Signature required: A Performance Evaluation has been approved by the division director', f'{employee.manager.name} has completed an evaluation for {employee.name}, which requires your signature. View and sign here: {url}', f'{employee.manager.name} has completed an evaluation for {employee.name}, which requires your signature. View and sign here: <a href="{url}">{url}</a>')
                next_reminder = datetime.datetime.today() + datetime.timedelta(days=HR_SIGNATURE_REMINDER_SUBSEQUENT)
                SignatureReminder.objects.create(review=pr, employee=hr_manager, next_date=next_reminder)

            # Reminder to HR Manager
            if hr_reminder:
                if today >= hr_reminder.next_date:
                    # Notification #14: Remind HR manager a subsequent time to sign evaluation
                    add_hr_reminder()
            else:
                # Notification #14
                add_hr_reminder()
            
            # Reminder to Executive Director if HR Manager isn't responding
            if ed_reminder:
                if today >= ed_reminder.date + datetime.timedelta(days=ESCALATION_TO_NEXT_MANAGER_REMINDER):
                    # Notification #15: Escalate to Executive Director to get HR Manager to sign the evaluation
                    add_reminder(executive_director.user.email, 'signature_required_other', f'A performance review is behind schedule', f'A signature is required by {hr_manager.name} for an evaluation for {employee.name}. Contact them here: {hr_manager.user.email}', f'A signature is required by {hr_manager.name} for an evaluation for {employee.name}. Contact them here: <a href="mailto:{hr_manager.user.email}">{hr_manager.user.email}</a>')
                    # We don't need to make another reminder because this same reminder will trigger every subsequent day

    ###################################################################################################
    ### Reminders to get the Executive Director to review and sign a written performance evaluation ###
    ###################################################################################################
    for pr in PerformanceReview.objects.filter(status=PerformanceReview.EVALUATION_HR_PROCESSED):
        url = current_site.domain + '/pr/' + str(pr.pk)
        employee = pr.employee
        ed_signatures = Signature.objects.filter(review=pr, employee=executive_director)
        if ed_signatures.count() == 0:
            ed_reminders = SignatureReminder.objects.filter(review=pr, employee=executive_director)
            ed_reminder = None
            hr_reminder = None
            if ed_reminders.count():
                ed_reminder = ed_reminders.latest()
                hr_reminder = ed_reminders.earliest()
            
            # Reminder to Executive Director
            def add_ed_reminder():
                add_reminder(executive_director.user.email, 'signature_required', f'Signature required: A Performance Evaluation has been approved by {hr_manager.name}', f'{employee.manager.name} has completed an evaluation for {employee.name}, which requires your signature. View and sign here: {url}', f'{employee.manager.name} has completed an evaluation for {employee.name}, which requires your signature. View and sign here: <a href="{url}">{url}</a>')
                next_reminder = datetime.datetime.today() + datetime.timedelta(days=ED_SIGNATURE_REMINDER_SUBSEQUENT)
                SignatureReminder.objects.create(review=pr, employee=executive_director, next_date=next_reminder)
            
            if ed_reminder:
                if today >= ed_reminder.next_date:
                    # Notification #17: Remind HR manager a subsequent time to sign evaluation
                    add_ed_reminder()
            else:
                # Notification #17
                add_ed_reminder()
            
            # Reminder to HR Manager if the Executive Director isn't responding
            if hr_reminder:
                if today >= hr_reminder.date + datetime.timedelta(days=ESCALATION_TO_NEXT_MANAGER_REMINDER):
                    # Notification #18: Escalate to HR Manager to get Executive Director to sign the evaluation
                    add_reminder(hr_manager.user.email, 'signature_required_other', f'A performance review is behind schedule', f'A signature is required by {executive_director.name} for an evaluation for {employee.name}. Contact them here: {executive_director.user.email}', f'A signature is required by {executive_director.name} for an evaluation for {employee.name}. Contact them here: <a href="mailto:{executive_director.user.email}">{executive_director.user.email}</a>')
                    # We don't need to make another reminder because this same reminder will trigger every subsequent day

    ####################################################
    ### Gather all the reminders and send the emails ###
    ####################################################
    for user in users.items():
        print('\n')
        print('USER:', user[0])
        if len(user[1]['review_to_write']):
            print('REVIEW_TO_WRITE')
            for notification in user[1]['review_to_write']:
                print(notification)
        if len(user[1]['review_to_write_other']):
            print('REVIEW_TO_WRITE_OTHER')
            for notification in user[1]['review_to_write_other']:
                print(notification)
        if len(user[1]['signature_required']):
            print('SIGNATURE_REQUIRED')
            for notification in user[1]['signature_required']:
                print(notification)
        if len(user[1]['signature_required_other']):
            print('SIGNATURE_REQUIRED_OTHER')
            for notification in user[1]['signature_required_other']:
                print(notification)
        
        review_to_write_notifications = user[1]['review_to_write']
        review_to_write_other_notifications = user[1]['review_to_write_other']
        signature_required_notifications = user[1]['signature_required']
        signature_required_other_notifications = user[1]['signature_required_other']

        total_num_notifications = len(review_to_write_notifications) + len(review_to_write_other_notifications) + len(signature_required_notifications) + len(signature_required_other_notifications)
        
        if total_num_notifications == 1:
            # Single Notification Email
            notifications = review_to_write_notifications + review_to_write_other_notifications + signature_required_notifications + signature_required_other_notifications
            notification = notifications[0]
            send_email(user[0], notification[0], notification[1], notification[2])
        elif total_num_notifications > 1:
            # Batch Notification Email
            subject = 'LCOG Performance Review To-Dos'
            text_body = 'There are multiple performance reviews that require your attention:\n'
            html_body = '<div>There are multiple performance reviews that require your attention:</div>'
            for notification_type in ['review_to_write', 'review_to_write_other', 'signature_required', 'signature_required_other']:
                notifications = user[1][notification_type]
                if len(notifications):
                    cleaned_header = " ".join([s.capitalize() for s in notification_type.split('_')])
                    text_body += '\n' + cleaned_header
                    html_body += f'<h3>{cleaned_header}</h3><table>'
                    for notification in notifications:
                        text_body += '\n' + notification[1]
                        html_body += f'<tr><th>{notification[0]}</th><td>{notification[2]}</td></tr>'
                    text_body += '\n'
                    html_body += '</table>'
            html_body += '<style>table { border-collapse: collapse; } th, td { border: 1px black solid; padding: 5px; }'
            print('HTML_BODY')
            print(html_body)
            send_email(user[0], subject, text_body, html_body)
    
    return users


def is_true_string(str):
    if str in ['true', 'True']:
        return True
    return False


def prop_in_obj(obj, prop, is_not):
    return prop in obj and obj[prop] != is_not


# d = datetime.date(2022, 8, 4)
# next_monday = next_weekday(d, 0) # 0=Monday, 1=Tuesday, 2=Wednesday...
def next_weekday(d, weekday):
    days_ahead = weekday - d.weekday()
    if days_ahead <= 0: # Target day already happened this week
        days_ahead += 7
    return d + datetime.timedelta(days_ahead)


def get_lat_long(address, city, state, zip):
    if '#' in address:
        address = address[:address.index('#')] # Remove unit number
    if ' 1/2' in address:
        address = address.replace(' 1/2', '') # Remove the 1/2 designation
    url = 'https://nominatim.openstreetmap.org/search/' + \
        urllib.parse.quote(f'${address}, ${city}, ${state}, ${zip}') + \
        '?format=json'
    response = requests.get(url).json()
    if response:
        return response[0]["lat"], response[0]["lon"]
    return None, None


def get_is_trusted_ip():
    # TODO: I couldn't get this to work because I don't have access to the
    # client IP here.
    from mainsite.api_views import TrustedIPViewSet
    factory = APIRequestFactory()
    trustedip_url = reverse('trustedip-list')
    trustedip_request = factory.get(trustedip_url)
    trustedip_view = TrustedIPViewSet.as_view({'get': 'list'})
    trusted_ip_response = trustedip_view(trustedip_request)
    is_trusted_ip = trusted_ip_response.data if hasattr(
        trusted_ip_response, 'data') else False
    return is_trusted_ip