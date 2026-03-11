from datetime import timedelta
from django.contrib.auth.models import Group
from django.contrib.sites.models import Site
from django.utils import timezone

from mainsite.helpers import send_email_multiple
from people.models import PerformanceReview


def send_manager_pr_notices():
    # Notification #0
    one_year_from_now = timezone.now() + timedelta(days=365)
    upcoming_reviews = PerformanceReview.objects.filter(
        period_end_date__lte=one_year_from_now,
        period_end_date__gte=timezone.now(),
        employee__active=True
    ).exclude(
        status=PerformanceReview.EVALUATION_HR_PROCESSED,
    ).order_by('period_end_date')

    # CC 'PR Completed Employees' group on all emails
    cc_group = Group.objects.get(name='PR Completed Employees').user_set.all()
    cc_emails = [user.email for user in cc_group]
    
    # Group reviews by manager
    manager_dict = {}
    for review in upcoming_reviews:
        manager = review.employee.manager
        try:
            if manager.pk not in manager_dict:
                print(f'Adding manager {manager.name} to manager_dict')
                manager_dict[manager.pk] = {
                    'manager': manager,
                    'reviews': []
                }
            manager_dict[manager.pk]['reviews'].append(review)
        except AttributeError as e:
            print(f'Error processing review {review.pk}: {e}')
            # Handle case where manager is None
            continue
    count = 0
    for manager_id, manager_data in manager_dict.items():
        current_site = Site.objects.get_current()
        url = current_site.domain + '/reviews/dashboard'
        body = f'Below is a list of your team\'s next review dates. See all here: {url}\n\n'
        html_body = f'<p>Below is a list of your team\'s next review dates. See all here: <a href="{url}">{url}</a></p><ul>'
        for review in manager_data['reviews']:
            if review.evaluation_type == \
            PerformanceReview.PROBATIONARY_EVALUATION:
                suffix = ' (Probationary)'
            else:
                suffix = ''
            body += f'- {review.employee.name}: {review.period_end_date.strftime("%m/%d/%Y")}{suffix}\n'
            html_body += f'<li>{review.employee.name}: {review.period_end_date.strftime("%m/%d/%Y")}{suffix}</li>'
        html_body += '</ul>'
        if manager_data['manager'].manager is not None and \
            not manager_data['manager'].manager.is_executive_director:
            cc_list = cc_emails + [manager_data['manager'].manager.user.email]
        else:
            cc_list = cc_emails
        send_email_multiple(
            [manager_data['manager'].user.email],
            cc_list,
            'Next Review Dates',
            body,
            html_body
        )
        count += 1
    return count