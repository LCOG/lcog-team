from datetime import datetime, timedelta
import os
import pytz

from django.contrib.auth.models import Group
from django.contrib.sites.models import Site
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from mainsite.helpers import readable_date, send_email, send_email_multiple
from people.models import JobTitle
from workflows.models import (
    EmployeeTransition, ProcessInstance, Role, WorkflowInstance
)

STAFF_TRANSITION_NEWS_EMAIL = os.environ.get('STAFF_TRANSITION_NEWS_EMAIL')
STAFF_MAILBOX_RECIPIENTS = os.environ.get('STAFF_MAILBOX_RECIPIENTS')

def send_mailbox_notification_email(
    t, sender_name='', sender_email='', url=''
):
    current_site = Site.objects.get_current()
    transition_url = current_site.domain + url
    profile_url = current_site.domain + '/profile'

    first_name = t.employee_first_name if t.employee_first_name else ''
    last_name = t.employee_last_name if t.employee_last_name else ''
    name_string = f'{ first_name } { last_name }'
    if t.type == EmployeeTransition.TRANSITION_TYPE_NEW:
        type_verb = 'starting'
    elif t.type == EmployeeTransition.TRANSITION_TYPE_CHANGE:
        type_verb = 'changing'
    elif t.type == EmployeeTransition.TRANSITION_TYPE_EXIT:
        type_verb = 'terminating'
    else:
        type_verb = 'changing'
    date_string = readable_date(t.transition_date) if t.transition_date else ''

    subject = f'New mailbox needed for { name_string }'

    html_template = '../templates/email/employee-transition-mailbox.html'
    html_message = render_to_string(html_template, {
        'name_string': name_string, 'type_verb': type_verb,
        'date_string': date_string, 'transition_url': transition_url,
        'sender_name': sender_name, 'profile_url': profile_url
    })
    plaintext_message = strip_tags(html_message)

    # Send to mailbox admins
    send_email_multiple(
        [STAFF_MAILBOX_RECIPIENTS], [], subject, plaintext_message, html_message
    )

def send_transition_submitter_email(
    t, extra_message=None, sender_name='', sender_email='', url='',
    reassigned=False
):
    current_site = Site.objects.get_current()
    transition_url = current_site.domain + url
    profile_url = current_site.domain + '/profile'
    
    reassigned_subject = 'REASSIGNED: ' if reassigned else ''
    title = t.title.name if t.title else ''
    if t.type == EmployeeTransition.TRANSITION_TYPE_NEW:
        type_verb = 'starting'
    elif t.type == EmployeeTransition.TRANSITION_TYPE_CHANGE:
        type_verb = 'changing'
    elif t.type == EmployeeTransition.TRANSITION_TYPE_EXIT:
        type_verb = 'terminating'
    else:
        type_verb = 'changing'
    date = readable_date(t.transition_date) if t.transition_date else ''

    subject = f'{ reassigned_subject }{ title } EIS { type_verb } { date }'

    html_template = '../templates/email/employee-transition-sds.html'
    html_message = render_to_string(html_template, {
        'title': title, 'type_verb': type_verb, 'date': date,
        'extra_message': extra_message, 'transition_url': transition_url,
        'sender_name': sender_name, 'profile_url': profile_url
    })
    plaintext_message = strip_tags(html_message)

    # Send to submitter and copy sender
    to_addresses = [
        t.submitter.user.email if (
            t.submitter and \
            t.submitter.should_receive_email_of_type(
                'workflows', 'transitions'
            ) and t.submitter.user.email
        ) else ''
    ]
    cc_addresses = [sender_email]

    send_email_multiple(
        to_addresses, cc_addresses, subject, plaintext_message, html_message
    )

def send_transition_sds_hiring_leads_email(
    t, extra_message=None, sender_name='', sender_email='', url='',
    reassigned=False
):
    current_site = Site.objects.get_current()
    transition_url = current_site.domain + url
    profile_url = current_site.domain + '/profile'
    
    reassigned_subject = 'REASSIGNED: ' if reassigned else ''
    title = t.title.name if t.title else ''
    if t.type == EmployeeTransition.TRANSITION_TYPE_NEW:
        type_verb = 'starting'
    elif t.type == EmployeeTransition.TRANSITION_TYPE_CHANGE:
        type_verb = 'changing'
    elif t.type == EmployeeTransition.TRANSITION_TYPE_EXIT:
        type_verb = 'terminating'
    else:
        type_verb = 'changing'
    date = readable_date(t.transition_date) if t.transition_date else ''

    subject = f'{ reassigned_subject }{ title } EIS { type_verb } { date }'

    html_template = '../templates/email/employee-transition-sds.html'
    html_message = render_to_string(html_template, {
        'title': title, 'type_verb': type_verb, 'date': date,
        'extra_message': extra_message, 'transition_url': transition_url,
        'sender_name': sender_name, 'profile_url': profile_url
    })
    plaintext_message = strip_tags(html_message)

    # Send to S&DS hiring leads and copy hiring manager and sender
    to_users = Group.objects.get(name='SDS Hiring Lead').user_set.all()
    to_addresses = [
        user.email for user in to_users if \
        user.employee.should_receive_email_of_type('workflows', 'transitions')
    ]
    cc_addresses = []
    if t.manager and t.manager.user.email:
        cc_addresses.append(t.manager.user.email)
    if sender_email not in cc_addresses:
        cc_addresses.append(sender_email)

    send_email_multiple(
        to_addresses, cc_addresses, subject, plaintext_message, html_message
    )

def send_transition_fiscal_email(
    t, extra_message=None, sender_name='', sender_email='', url='',
    reassigned=False
):
    current_site = Site.objects.get_current()
    transition_url = current_site.domain + url
    profile_url = current_site.domain + '/profile'
    
    reassigned_subject = 'REASSIGNED: ' if reassigned else ''
    first_name = t.employee_first_name if t.employee_first_name else ''
    last_name = t.employee_last_name if t.employee_last_name else ''
    name = f'{ first_name } { last_name }'
    if t.type == EmployeeTransition.TRANSITION_TYPE_NEW:
        type_verb = 'starting'
    elif t.type == EmployeeTransition.TRANSITION_TYPE_CHANGE:
        type_verb = 'changing'
    elif t.type == EmployeeTransition.TRANSITION_TYPE_EXIT:
        type_verb = 'terminating'
    else:
        type_verb = 'changing'
    date = readable_date(t.transition_date) if t.transition_date else ''

    subject = f'{ reassigned_subject }{ name } EIS { type_verb } { date }'

    html_template = '../templates/email/employee-transition-fiscal-hr.html'
    html_message = render_to_string(html_template, {
        'name': name, 'type_verb': type_verb, 'date': date,
        'extra_message': extra_message, 'transition_url': transition_url,
        'sender_name': sender_name, 'profile_url': profile_url
    })
    plaintext_message = strip_tags(html_message)

    # Send to fiscal employees.
    # Copy hiring manager and, if SDS, SDS hiring leads.
    to_users = Group.objects.get(name='Fiscal Employee').user_set.all()
    to_addresses = [
        user.email for user in to_users if \
        user.employee.should_receive_email_of_type('workflows', 'transitions')
    ]
    cc_addresses = []
    if t.manager and t.manager.user.email:
        cc_addresses.append(t.manager.user.email)
    
    if t.is_sds:
        sds_hiring_leads_users = Group.objects.get(
            name='SDS Hiring Lead'
        ).user_set.all()
        sds_hiring_leads_emails = [
            user.email for user in sds_hiring_leads_users if \
            user.employee.should_receive_email_of_type(
                'workflows', 'transitions'
            )
        ]
        for email in sds_hiring_leads_emails:
            cc_addresses.append(email)

    send_email_multiple(
        to_addresses, cc_addresses, subject, plaintext_message, html_message
    )

def send_early_hr_email(t, url=''):
    current_site = Site.objects.get_current()
    transition_url = current_site.domain + url
    profile_url = current_site.domain + '/profile'
    
    first_name = t.employee_first_name if t.employee_first_name else ''
    last_name = t.employee_last_name if t.employee_last_name else ''
    name_string = f'{ first_name } { last_name }'
    if t.type == EmployeeTransition.TRANSITION_TYPE_NEW:
        type_verb = 'starting'
    elif t.type == EmployeeTransition.TRANSITION_TYPE_CHANGE:
        type_verb = 'changing'
    elif t.type == EmployeeTransition.TRANSITION_TYPE_EXIT:
        type_verb = 'terminating'
    else:
        type_verb = 'changing'
    date_string = readable_date(t.transition_date) if t.transition_date else ''

    subject = (
        f'Just Submitted: { name_string } EIS { type_verb } { date_string }'
    )

    html_template = '../templates/email/employee-transition-fiscal-hr.html'
    html_message = render_to_string(html_template, {
        'name_string': name_string,
        'type_verb': type_verb,
        'date_string': date_string,
        'extra_message': 'This is an early notification to HR. The form has ' +
            'not been approved yet.',
        'transition_url': transition_url,
        'sender_name': '',
        'profile_url': profile_url
    })
    plaintext_message = strip_tags(html_message)

    # Send to HR employees
    to_users = Group.objects.get(name='HR Employee').user_set.all()
    to_addresses = [
        user.email for user in to_users if \
        user.employee.should_receive_email_of_type('workflows', 'transitions')
    ]
    cc_addresses = []

    send_email_multiple(
        to_addresses, cc_addresses, subject, plaintext_message, html_message
    )

def send_transition_hr_email(
    t, extra_message=None, sender_name='', sender_email='', url='',
    reassigned=False
):
    current_site = Site.objects.get_current()
    transition_url = current_site.domain + url
    profile_url = current_site.domain + '/profile'
    
    reassigned_subject = 'REASSIGNED: ' if reassigned else ''
    first_name = t.employee_first_name if t.employee_first_name else ''
    last_name = t.employee_last_name if t.employee_last_name else ''
    name = f'{ first_name } { last_name }'
    if t.type == EmployeeTransition.TRANSITION_TYPE_NEW:
        type_verb = 'starting'
    elif t.type == EmployeeTransition.TRANSITION_TYPE_CHANGE:
        type_verb = 'changing'
    elif t.type == EmployeeTransition.TRANSITION_TYPE_EXIT:
        type_verb = 'terminating'
    else:
        type_verb = 'changing'
    date = readable_date(t.transition_date) if t.transition_date else ''

    subject = f'{ reassigned_subject }{ name } EIS { type_verb } { date }'

    html_template = '../templates/email/employee-transition-fiscal-hr.html'
    html_message = render_to_string(html_template, {
        'name': name, 'type_verb': type_verb, 'date': date,
        'extra_message': extra_message, 'transition_url': transition_url,
        'sender_name': sender_name, 'profile_url': profile_url
    })
    plaintext_message = strip_tags(html_message)

    # Send to HR employees and copy hiring manager and fiscal employees
    to_users = Group.objects.get(name='HR Employee').user_set.all()
    to_addresses = [
        user.email for user in to_users if \
        user.employee.should_receive_email_of_type('workflows', 'transitions')
    ]
    cc_addresses = []
    if t.manager and t.manager.user.email:
        cc_addresses.append(t.manager.user.email)
    fiscal_users = Group.objects.get(name='Fiscal Employee').user_set.all()
    fiscal_addresses = [
        user.email for user in fiscal_users if \
        user.employee.should_receive_email_of_type('workflows', 'transitions')
    ]
    for email in fiscal_addresses:
        cc_addresses.append(email)

    send_email_multiple(
        to_addresses, cc_addresses, subject, plaintext_message, html_message
    )

def send_transition_stn_email(
        t, update=False, extra_message=None, sender_name='', url='',
        reassigned=False
    ):
    current_site = Site.objects.get_current()
    transition_url = current_site.domain + url
    profile_url = current_site.domain + '/profile'
    
    updated = 'UPDATED: ' if update else ''
    reassigned = 'REASSIGNED: ' if reassigned else ''
    first_name = t.employee_first_name if t.employee_first_name else ''
    last_name = t.employee_last_name if t.employee_last_name else ''
    name = f'{ first_name } { last_name }'
    exit = 'EXIT: ' if \
        t.type == EmployeeTransition.TRANSITION_TYPE_EXIT else ''
    date = readable_date(t.transition_date) if t.transition_date else ''

    subject = f'{ reassigned }{ updated }{ name } { exit }EIS { date }'
    
    updated_body_string = 'updated ' if update else ''
    exit_body_string = 'Exit ' if \
        t.type == EmployeeTransition.TRANSITION_TYPE_EXIT else ''
    title_name = JobTitle.objects.get(pk=t.title_id).name if t.title_id else ''
    title_string = f'{ title_name}'
    type_body_description = '. Their last day was' if \
        t.type == EmployeeTransition.TRANSITION_TYPE_EXIT else ' starting'

    html_template = '../templates/email/employee-transition-stn.html'
    html_message = render_to_string(html_template, {
        'updated_body_string': updated_body_string,
        'exit_body_string': exit_body_string, 'name': name,
        'title_string': title_string,
        'type_body_description': type_body_description, 'date': date,
        'extra_message': extra_message, 'transition_url': transition_url,
        'sender_name': sender_name, 'profile_url': profile_url
    })
    plaintext_message = strip_tags(html_message)

    send_email(
        STAFF_TRANSITION_NEWS_EMAIL, subject, plaintext_message, html_message
    )

def send_step_completion_email(si, old_si=None):
    current_site = Site.objects.get_current()
    url = f'/wf/{si.process_instance.workflow_instance.id}/processes'
    processes_url = current_site.domain + url
    profile_url = current_site.domain + '/profile'

    subject = f'Time to { si.step.name }'

    html_template = '../templates/email/workflows/complete-step.html'
    html_message = render_to_string(html_template, {
        'step': si.step.name,
        'process': si.step.process.name,
        'processes_url': processes_url,
        'completer': old_si.completed_by.name if old_si else None,
        'completed_step': old_si.step.name if old_si else None,
        'profile_url': profile_url
    })
    plaintext_message = strip_tags(html_message)

    # Send to HR employees and copy hiring manager and fiscal employees
    role = si.step.role
    if not role:
        return
    to_employees = role.members.all()
    to_addresses = [
        e.user.email for e in to_employees if \
            e.should_receive_email_of_type('workflows', 'processes')
    ]

    send_email_multiple(
        to_addresses, [], subject, plaintext_message, html_message
    )

def send_weekly_step_reminders():
    # Every week on Monday, send reminders to all employees who have
    # steps assigned to them that are not yet complete.
    current_site = Site.objects.get_current()
    url = current_site.domain + '/wf/%s/processes'
    profile_url = current_site.domain + '/profile'

    subject = 'Weekly Workflow Reminders'

    html_template = \
        '../templates/email/workflows/weekly-step-reminders.html'
    
    incomplete_workflow_instances = WorkflowInstance.objects.filter(
        active=True, complete=False
    ).prefetch_related('pis')
    employees = {}
    for wfi in incomplete_workflow_instances:
        for pi in wfi.pis.all():
            for assignee in pi.current_step_instance.step.role.members.all() if pi.current_step_instance.step.role else []:
                if assignee not in employees:
                    employees[assignee] = []
                employees[assignee].append({
                    'step': pi.current_step_instance.step.name,
                    'process': pi.process.name,
                    'days_assigned': pi.current_step_instance.duration.days,
                    'pi_url': url % wfi.pk
                })

    sent_emails = 0
    for employee, steps in employees.items():
        if not employee.should_receive_email_of_type('workflows', 'processes'):
            continue

        html_message = render_to_string(html_template, {
            'steps': steps,
            'profile_url': profile_url
        })
        plaintext_message = strip_tags(html_message)

        send_email(employee.user.email, subject, plaintext_message, html_message)
        sent_emails += 1
    
    return sent_emails

def send_employee_transition_report():
    current_site = Site.objects.get_current()
    workflows_url = current_site.domain + '/workflows/dashboard'
    profile_url = current_site.domain + '/profile'
    current_wfis = WorkflowInstance.objects.filter(
        active=True,
        complete=False,
        workflow__type__in=[
            'employee-new', 'employee-name-change', 'employee-change',
            'employee-return', 'employee-exit'
        ]
    ).order_by('transition__transition_date').prefetch_related('pis')
    current_wfis = [{
        'pk': wfi.pk,
        'percent_complete': wfi.percent_complete,
        'percent_incomplete': 100 - wfi.percent_complete,
        't': {
            'type': wfi.transition.type,
            'date': wfi.transition.transition_date,
            'past_date': wfi.transition.transition_date < datetime.now(pytz.utc) if wfi.transition.transition_date else False,
            'assignee': wfi.transition.assignee,
            'employee_first_name': wfi.transition.employee_first_name,
            'employee_last_name': wfi.transition.employee_last_name,
            'title_name': wfi.transition.title.name if wfi.transition.title else 'Title not set',
        },
        'pis': [
            {
                'name': pi.process.name,
                'current_step_name': pi.current_step_instance.step.name if pi.current_step_instance else '',
                'percent_complete': pi.percent_complete,
                'assigned_ago': pi.current_step_instance.duration.days if pi.current_step_instance else None,
                'assignees': [
                    member.name for member in pi.current_step_instance.step.role.members.all()
                ] if pi.current_step_instance and pi.current_step_instance.step and pi.current_step_instance.step.role else ['No one!']
            } for pi in wfi.pis.all()
        ]
    } for wfi in current_wfis]
    last_week_wfis = WorkflowInstance.objects.filter(
        active=True,
        complete=True,
        workflow__type__in=[
            'employee-new', 'employee-name-change', 'employee-change',
            'employee-return', 'employee-exit'
        ],
        completed_at__gte=datetime.now() - timedelta(days=10),
        completed_at__lt=datetime.now()
    )
    last_week_wfis = [{
        'pk': wfi.pk,
        'completed_at': wfi.completed_at,
        't': {
            'type': wfi.transition.type,
            'date': wfi.transition.transition_date,
            'employee_first_name': wfi.transition.employee_first_name,
            'employee_last_name': wfi.transition.employee_last_name,
            'title_name': wfi.transition.title.name if wfi.transition.title else 'Title not set',
        }  
    } for wfi in last_week_wfis]
    subject = 'Weekly Employee Transition Report'
    html_template = \
        '../templates/email/workflows/current-transitions-report.html'
    html_message = render_to_string(html_template, {
        'current_wfis': current_wfis, 'last_week_wfis': last_week_wfis,
        'workflows_url': workflows_url, 'profile_url': profile_url,
        'domain': current_site.domain
    })
    plaintext_message = strip_tags(html_message)

    # Send to the appropriate workflow admins
    to_employees = Role.objects.get(
        name='Employee Transition Management'
    ).members.all()
    to_addresses = [
        e.user.email for e in to_employees if \
        e.should_receive_email_of_type('workflows', 'transitions')
    ]

    send_email_multiple(
        to_addresses, [], subject, plaintext_message, html_message
    )
    
    return len(to_addresses)

def create_process_instances(transition):
    # Create process instances for staff transition workflows. Triggered when
    # a transition form is sent to Staff Transition News.
    onboarding_processes_start = [
        'HR Onboarding', 'IS Onboarding', 'IS Telecom Onboarding',
    ]
    onboarding_processes_start_sds = [
        'SDS Ergo', 'SDS Facilities Onboarding', 'SDS Onboarding',
        'SDS Sub Admin'
    ]
    returning_processes_start = []
    returning_processes_start_sds = []
    name_change_processes_start = ['IS Name Change']
    name_change_processes_start_sds = ['Name Change SDS Sub Admin']
    changing_processes_start = ['IS Changing']
    changing_processes_start_sds = ['SDS Changing', 'SDS Phone Changing']
    exiting_processes_start = ['IS Exiting']
    exiting_processes_start_sds = []
    wfi = transition.workflowinstance
    # Set the process names based on the transition type
    transition_process_names = []
    if (transition.type == EmployeeTransition.TRANSITION_TYPE_NEW):
        transition_process_names += onboarding_processes_start
        if (transition.is_sds):
            transition_process_names += onboarding_processes_start_sds
    elif (transition.type == EmployeeTransition.TRANSITION_TYPE_RETURN):
        transition_process_names += returning_processes_start
        if (transition.is_sds):
            transition_process_names += returning_processes_start_sds
    elif (transition.type == EmployeeTransition.TRANSITION_TYPE_NAME_CHANGE):
        transition_process_names += name_change_processes_start
        if (transition.is_sds):
            transition_process_names += name_change_processes_start_sds
    elif (transition.type == EmployeeTransition.TRANSITION_TYPE_CHANGE):
        transition_process_names += changing_processes_start
        if (transition.is_sds):
            transition_process_names += changing_processes_start_sds
    elif (transition.type == EmployeeTransition.TRANSITION_TYPE_EXIT):
        transition_process_names += exiting_processes_start
        if (transition.is_sds):
            transition_process_names += exiting_processes_start_sds
    # Create process instances for each process in the list
    for process in wfi.workflow.processes.filter(
        name__in=transition_process_names
    ):
        existing_pis = ProcessInstance.objects.filter(
            process=process, workflow_instance=wfi
        )
        if existing_pis.count() == 0:
            process.create_process_instance(wfi)
