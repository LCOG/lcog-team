from datetime import date, datetime
import os

from django.contrib.sites.models import Site
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from mainsite.helpers import next_weekday, send_email, send_email_multiple
from people.models import Employee
from timeoff.models import TimeOffRequest, TimeOffRequestTemporaryApprover


def send_manager_new_timeoff_request_notification(tor):
    current_site = Site.objects.get_current()
    url = current_site.domain + '/timeoff/manage-requests'
    if tor.start_date == tor.end_date:
        message = (
            f'{tor.employee.name} has requested time off on {tor.start_date}. '
            f'View and acknowledge here: {url}'
        )
    else:
        message = (
            f'{tor.employee.name} has requested time off from {tor.start_date}'
            f' to {tor.end_date}. View and acknowledge here: {url}'
        )
    emails = [tor.employee.manager.user.email]

    # If this user is a temporary approver for someone else,
    # send them the notification as well.
    temporary_approvers = TimeOffRequestTemporaryApprover.objects.filter(
        employee_on_leave=tor.employee.manager,
        start_date__lte=date.today(),
        end_date__gte=date.today()
    )
    for approver in temporary_approvers:
        emails.append(approver.employee_in_stead.user.email)

    send_email_multiple(
        emails,
        [],
        f'New time off request: {tor.employee.name}',
        message,
        message
    )


def send_employee_manager_acknowledged_timeoff_request_notification(
    tor, manager=None
):
    """
    Manager is specified in the event of a temporary request approver while a
    manager is on leave.
    """
    current_site = Site.objects.get_current()
    url = current_site.domain + '/timeoff/my-requests'
    employee = tor.employee
    if manager:
        manager_name = manager.name
    else:
        manager_name = employee.manager.name
    
    dates_str = ''
    if tor.start_date == tor.end_date:
        dates_str = f'on {tor.start_date}'
    else:
        dates_str = f'from {tor.start_date} to {tor.end_date}'
    
    if tor.acknowledged:
        message = (
            f'{manager_name} has acknowledged your time off {dates_str}. View '
            f'here: {url}'
        )
    else:
        message = (
            f'{manager_name} has indicated a problem with your time off '
            f'{dates_str}. View here: {url}'
        )

    send_email(
        employee.user.email,
        f'Time off request response',
        message,
        message
    )


def send_team_timeoff_next_week_report(manager_username: str, team_name: str):
    current_site = Site.objects.get_current()
    calendar_url = current_site.domain + '/timeoff/calendar'
    profile_url = current_site.domain + '/profile'
    manager = Employee.objects.get(user__username=manager_username)
    team = manager.get_descendants_of_employee(manager)
    tors = TimeOffRequest.objects.filter(employee__in=team)
    
    today = datetime.now().date()
    next_monday = next_weekday(today, 0) # 0=Monday, 1=Tuesday, 2=Wednesday...
    next_tuesday = next_weekday(next_monday, 1)
    next_wednesday = next_weekday(next_monday, 2)
    next_thursday = next_weekday(next_monday, 3)
    next_friday = next_weekday(next_monday, 4)
    
    monday_tors = tors.filter(
        start_date__lte=next_monday, end_date__gte=next_monday
    )
    tuesday_tors = tors.filter(
        start_date__lte=next_tuesday, end_date__gte=next_tuesday
    )
    wednesday_tors = tors.filter(
        start_date__lte=next_wednesday, end_date__gte=next_wednesday
    )
    thursday_tors = tors.filter(
        start_date__lte=next_thursday, end_date__gte=next_thursday
    )
    friday_tors = tors.filter(
        start_date__lte=next_friday, end_date__gte=next_friday
    )

    num_tors = sum([
        monday_tors.count(), tuesday_tors.count(), wednesday_tors.count(),
        thursday_tors.count(), friday_tors.count()
    ])

    if num_tors == 0:
        return num_tors, len(team)

    html_template = '../templates/email/team-timeoff.html'
    html_message = render_to_string(html_template, { 'context': {
        'team_name': team_name, 'next_monday': next_monday,
        'next_tuesday': next_tuesday, 'next_wednesday': next_wednesday,
        'next_thursday': next_thursday, 'next_friday': next_friday,
        'monday_tors': monday_tors, 'tuesday_tors': tuesday_tors,
        'wednesday_tors': wednesday_tors, 'thursday_tors': thursday_tors,
        'friday_tors': friday_tors, 'calendar_url': calendar_url,
        'profile_url': profile_url, 'from_email': os.environ.get('FROM_EMAIL')
    }, })
    plaintext_message = strip_tags(html_message)

    # file1 = open('email.html', 'w')
    # file1.write(html_message)

    emails = []
    for recipient in team:
        if recipient.should_receive_email_of_type('timeoff', 'weekly'):
            emails.append(recipient.user.email)

    send_email_multiple(
        emails,
        [],
        f'{team_name} Time Off Next Week: {next_monday:%A} ' +
            f'{next_monday:%B} {next_monday.day} - {next_friday:%A} ' +
            f'{next_friday:%B} {next_friday.day}, {next_friday.year}',
        plaintext_message,
        html_message
    )
    
    return num_tors, len(team)

def send_test_timeoff_next_week_report():
    return send_team_timeoff_next_week_report('programmanager', 'Test Unit')

def send_is_timeoff_next_week_report():
    return send_team_timeoff_next_week_report('hleyba@lcog-or.gov', 'IS')

def send_daily_helpdesk_timeoff_today_report():
    current_site = Site.objects.get_current()
    calendar_url = current_site.domain + '/timeoff/calendar'
    profile_url = current_site.domain + '/profile'
    team_name = 'IS'
    help_desk = Employee.objects.filter(user__groups__name='IS Help Desk')
    is_team = Employee.objects.filter(user__groups__name='IS Employee')
    tors = TimeOffRequest.objects.filter(employee__in=is_team)
    
    today = datetime.now().date()
    today_tors = tors.filter(start_date__lte=today, end_date__gte=today)
    num_tors = today_tors.count()

    if num_tors == 0:
        return num_tors, len(help_desk)

    html_template = '../templates/email/team-timeoff-today.html'
    html_message = render_to_string(html_template, { 'context': {
        'team_name': team_name, 'today': today, 'today_tors': today_tors,
        'calendar_url': calendar_url, 'profile_url': profile_url,
        'from_email': os.environ.get('FROM_EMAIL')
    }, })
    plaintext_message = strip_tags(html_message)

    emails = []
    for recipient in help_desk:
        if recipient.should_receive_email_of_type('timeoff', 'daily'):
            emails.append(recipient.user.email)
            
    send_email_multiple(
        emails,
        [],
        f'{team_name} Time Off Today: {today:%A} {today:%B} ' +
            f'{today.day}, {today.year}',
        plaintext_message,
        html_message
    )

    return num_tors, len(help_desk)