import datetime
# import requests

from django.contrib.auth.models import User
from django.core import mail
from django.test import TestCase

from rest_framework.test import APIRequestFactory, APIClient

from mainsite.helpers import send_pr_reminder_emails
from people.models import Employee, PerformanceReview, Signature, SignatureReminder


class BaseEmailRemindersTestCase(TestCase):
    def setUp(self):
        employee_user = User.objects.create(username="employee", first_name="Employee", last_name="Person", email="employee@lcog-or.gov")
        manager_user = User.objects.create(username="manager", first_name="Manager", last_name="Person", email="manager@lcog-or.gov")
        program_manager_user = User.objects.create(username="programmanager", first_name="Program", last_name="Manager", email="programmanager@lcog-or.gov")
        deputy_director_user = User.objects.create(username="deputydirector", first_name="Deputy", last_name="Director", email="deputydirector@lcog-or.gov")
        division_director_user = User.objects.create(username="divisiondirector", first_name="Division", last_name="Director", email="divisiondirector@lcog-or.gov")
        hr_manager_user = User.objects.create(username="hrmanager", first_name="HR", last_name="Manager", email="hrmanager@lcog-or.gov")
        executive_director_user = User.objects.create(username="executivedirector", first_name="Executive", last_name="Director", email="executivedirector@lcog-or.gov")

        self.employee_employee = Employee.objects.create(user=employee_user)
        self.manager_employee = Employee.objects.create(user=manager_user)
        self.program_manager_employee = Employee.objects.create(user=program_manager_user)
        self.deputy_director_employee = Employee.objects.create(user=deputy_director_user)
        self.division_director_employee = Employee.objects.create(user=division_director_user, is_division_director=True)
        self.hr_manager_employee = Employee.objects.create(user=hr_manager_user, is_hr_manager=True)
        self.executive_director_employee = Employee.objects.create(user=executive_director_user, is_executive_director=True)

        self.employee_employee.manager = self.manager_employee
        self.manager_employee.manager = self.program_manager_employee
        self.program_manager_employee.manager = self.deputy_director_employee
        self.deputy_director_employee.manager = self.division_director_employee
        self.division_director_employee.manager = self.executive_director_employee
        self.hr_manager_employee.manager = self.executive_director_employee
        self.employee_employee.save()
        self.manager_employee.save()
        self.program_manager_employee.save()
        self.deputy_director_employee.save()
        self.division_director_employee.save()
        self.hr_manager_employee.save()


class ManagerWritesEvaluationTestCase(BaseEmailRemindersTestCase):
    def test_empty_emails(self):
        notifications = send_pr_reminder_emails()
        self.assertEqual(notifications, {})
    
    def test_manager_reminded_to_complete_review(self):
        # 60 days out
        pr = PerformanceReview.objects.create(
            employee=self.employee_employee,
            period_start_date=datetime.date.today(),
            period_end_date=datetime.date.today(),
            effective_date=datetime.date.today() + datetime.timedelta(60)
        )
        all_notifications = send_pr_reminder_emails()
        # There are the correct number of people receiving notifications
        self.assertEqual(len(all_notifications.keys()), 1)
        notifications = all_notifications[list(all_notifications.keys())[0]]
        # There are the correct numnber of notifications of the correct type
        self.assertEqual(len(notifications['review_to_write']), 1)
        self.assertEqual(len(notifications['review_to_write_other']), 0)
        self.assertEqual(len(notifications['signature_required']), 0)
        self.assertEqual(len(notifications['signature_required_other']), 0)

        # 45 days out
        pr = PerformanceReview.objects.create(
            employee=self.employee_employee,
            period_start_date=datetime.date.today(),
            period_end_date=datetime.date.today(),
            effective_date=datetime.date.today() + datetime.timedelta(45)
        )
        all_notifications = send_pr_reminder_emails()
        # There are the correct number of people receiving notifications
        self.assertEqual(len(all_notifications.keys()), 1)
        notifications = all_notifications[list(all_notifications.keys())[0]]
        # There are the correct numnber of notifications of the correct type
        self.assertEqual(len(notifications['review_to_write']), 2)
        self.assertEqual(len(notifications['review_to_write_other']), 0)
        self.assertEqual(len(notifications['signature_required']), 0)
        self.assertEqual(len(notifications['signature_required_other']), 0)

        # 30 days out
        pr = PerformanceReview.objects.create(
            employee=self.employee_employee,
            period_start_date=datetime.date.today(),
            period_end_date=datetime.date.today(),
            effective_date=datetime.date.today() + datetime.timedelta(30)
        )
        all_notifications = send_pr_reminder_emails()
        # There are the correct number of people receiving notifications
        self.assertEqual(len(all_notifications.keys()), 2)
        manager_notifications = all_notifications[self.manager_employee.user.email]
        program_manager_notifications = all_notifications[self.program_manager_employee.user.email]
        # There are the correct numnber of notifications of the correct type
        self.assertEqual(len(manager_notifications['review_to_write']), 3)
        self.assertEqual(len(manager_notifications['review_to_write_other']), 0)
        self.assertEqual(len(manager_notifications['signature_required']), 0)
        self.assertEqual(len(manager_notifications['signature_required_other']), 0)
        self.assertEqual(len(program_manager_notifications['review_to_write']), 0)
        self.assertEqual(len(program_manager_notifications['review_to_write_other']), 1)
        self.assertEqual(len(program_manager_notifications['signature_required']), 0)
        self.assertEqual(len(program_manager_notifications['signature_required_other']), 0)

        # 29 days out
        pr = PerformanceReview.objects.create(
            employee=self.employee_employee,
            period_start_date=datetime.date.today(),
            period_end_date=datetime.date.today(),
            effective_date=datetime.date.today() + datetime.timedelta(29)
        )
        all_notifications = send_pr_reminder_emails()
        # There are the correct number of people receiving notifications
        self.assertEqual(len(all_notifications.keys()), 2)
        manager_notifications = all_notifications[self.manager_employee.user.email]
        program_manager_notifications = all_notifications[self.program_manager_employee.user.email]
        # There are the correct numnber of notifications of the correct type
        self.assertEqual(len(manager_notifications['review_to_write']), 4)
        self.assertEqual(len(manager_notifications['review_to_write_other']), 0)
        self.assertEqual(len(manager_notifications['signature_required']), 0)
        self.assertEqual(len(manager_notifications['signature_required_other']), 0)
        self.assertEqual(len(program_manager_notifications['review_to_write']), 0)
        self.assertEqual(len(program_manager_notifications['review_to_write_other']), 2)
        self.assertEqual(len(program_manager_notifications['signature_required']), 0)
        self.assertEqual(len(program_manager_notifications['signature_required_other']), 0)

    def test_employee_reminded_to_sign_own_review(self):
        pr = PerformanceReview.objects.create(
            employee=self.employee_employee,
            period_start_date=datetime.date.today(),
            period_end_date=datetime.date.today(),
            effective_date=datetime.date.today() + datetime.timedelta(60)
        )
        # TODO: Manager completes review which triggers initial reminder to Employee
        # update_data = {
        #     'action_other': 'null',
        #     'factor_initiative': "N",
        #     # description_reviewed_employee: true,
        #     # evaluation_comments_employee: "I think this seems goodsdfsfsgsrgasdfsdf",
        #     # evaluation_goals_manager: "afaa",
        #     # evaluation_opportunities: "Some opportunitya",
        #     # evaluation_successes: "So great!",
        #     # evaluation_type: "P",
        #     # factor_analysis: "N",
        #     # factor_communication: "N",
        #     # factor_dependability: "N",
        #     # factor_initiative: "N",
        #     # factor_interpersonal: "N",
        #     # factor_job_knowledge: "N",
        #     # factor_management: "NA",
        #     # factor_professionalism: "N",
        #     # factor_supervision: "NA",
        #     # factor_work_habits: "N",
        #     # factor_work_quality: "N",
        #     # factor_work_quantity: "N",
        #     # probationary_evaluation_type: "N",
        #     # step_increase: "Y",
        #     # top_step_bonus: "Y"
        # }
        # client = APIClient()
        # client.post(f'/api/v1/review/{pr.pk}', {'factor_initiative': 'N'}, format='json')
        # pr2 = PerformanceReview.objects.get(pk=pr.pk)
        # print("PR2FI", pr2.factor_initiative)
        # self.assertEqual(pr2.factor_initiative, 'N')
        # import pdb; pdb.set_trace()
        
        # headers = {'Authorization': 'Token 05c5ab7d90b00e4278ec37ffb8394953e4a8c97e'}
        # requests.put(f'http://lcog-team:8000/api/v1/review/{pr.pk}', data=update_data, headers=headers)
        # import pdb; pdb.set_trace()

        # http.put(`api/v1/review/${pk}`, data)


        # action_other: null
        # description_reviewed_employee: true
        # evaluation_comments_employee: "I think this seems goodsdfsfsgsrgasdfsdf"
        # evaluation_goals_manager: "afaa"
        # evaluation_opportunities: "Some opportunitya"
        # evaluation_successes: "So great!"
        # evaluation_type: "P"
        # factor_analysis: "N"
        # factor_communication: "N"
        # factor_dependability: "N"
        # factor_initiative: "N"
        # factor_interpersonal: "N"
        # factor_job_knowledge: "N"
        # factor_management: "NA"
        # factor_professionalism: "N"
        # factor_supervision: "NA"
        # factor_work_habits: "N"
        # factor_work_quality: "N"
        # factor_work_quantity: "N"
        # probationary_evaluation_type: "N"
        # step_increase: "Y"
        # top_step_bonus: "Y"

        pr.description_reviewed_employee = True
        pr.evaluation_goals_manager: 'Some goals'
        pr.evaluation_opportunities: 'Some opportunities'
        pr.evaluation_successes: 'So great!'
        pr.evaluation_type: 'P'
        pr.factor_analysis: 'N'
        pr.factor_communication: 'N'
        pr.factor_dependability: 'N'
        pr.factor_initiative: 'N'
        pr.factor_interpersonal: 'N'
        pr.factor_job_knowledge: 'N'
        pr.factor_management: 'NA'
        pr.factor_professionalism: 'N'
        pr.factor_supervision: 'NA'
        pr.factor_work_habits: 'N'
        pr.factor_work_quality: 'N'
        pr.factor_work_quantity: 'N'
        pr.probationary_evaluation_type: 'N'
        pr.step_increase: 'Y'
        pr.top_step_bonus: 'Y'
        
        # TODO: Not needed once we make the API call above
        pr.status = PerformanceReview.EVALUATION_WRITTEN
        
        pr.save()

        # 2 days after review completed
        SignatureReminder.objects.all().delete() # Clear other reminders
        reminder = SignatureReminder.objects.create(
            review=pr, employee=self.employee_employee,
            next_date=datetime.date.today()
        )
        reminder.date = datetime.date.today() - datetime.timedelta(2)
        reminder.save()
        all_notifications = send_pr_reminder_emails()
        # There are the correct number of people receiving notifications
        self.assertEqual(len(all_notifications.keys()), 2)
        employee_notifications = all_notifications[self.employee_employee.user.email]
        manager_notifications = all_notifications[self.manager_employee.user.email]
        # There are the correct numnber of notifications of the correct type
        self.assertEqual(len(employee_notifications['review_to_write']), 0)
        self.assertEqual(len(employee_notifications['review_to_write_other']), 0)
        self.assertEqual(len(employee_notifications['signature_required']), 1)
        self.assertEqual(len(employee_notifications['signature_required_other']), 0)
        self.assertEqual(len(manager_notifications['review_to_write']), 0)
        self.assertEqual(len(manager_notifications['review_to_write_other']), 0)
        self.assertEqual(len(manager_notifications['signature_required']), 1)
        self.assertEqual(len(manager_notifications['signature_required_other']), 0)
        
        # 3 days after review completed
        SignatureReminder.objects.all().delete() # Clear other reminders
        reminder = SignatureReminder.objects.create(
            review=pr, employee=self.employee_employee,
            next_date=datetime.date.today() + datetime.timedelta(1)
        )
        reminder.date = datetime.date.today() - datetime.timedelta(1)
        reminder.save()
        all_notifications = send_pr_reminder_emails()
        # There are the correct number of people receiving notifications
        self.assertEqual(len(all_notifications.keys()), 1)
        manager_notifications = all_notifications[self.manager_employee.user.email]
        # There are the correct numnber of notifications of the correct type
        self.assertEqual(len(manager_notifications['review_to_write']), 0)
        self.assertEqual(len(manager_notifications['review_to_write_other']), 0)
        self.assertEqual(len(manager_notifications['signature_required']), 1)
        self.assertEqual(len(manager_notifications['signature_required_other']), 0)

        # 7 days after review completed
        SignatureReminder.objects.all().delete() # Clear other reminders
        reminder = SignatureReminder.objects.create(
            review=pr, employee=self.employee_employee,
            next_date=datetime.date.today()
        )
        reminder.date = datetime.date.today() - datetime.timedelta(7)
        reminder.save()
        all_notifications = send_pr_reminder_emails()
        # There are the correct number of people receiving notifications
        self.assertEqual(len(all_notifications.keys()), 2)
        employee_notifications = all_notifications[self.employee_employee.user.email]
        manager_notifications = all_notifications[self.manager_employee.user.email]
        # There are the correct numnber of notifications of the correct type
        self.assertEqual(len(employee_notifications['review_to_write']), 0)
        self.assertEqual(len(employee_notifications['review_to_write_other']), 0)
        self.assertEqual(len(employee_notifications['signature_required']), 1)
        self.assertEqual(len(employee_notifications['signature_required_other']), 0)
        self.assertEqual(len(manager_notifications['review_to_write']), 0)
        self.assertEqual(len(manager_notifications['review_to_write_other']), 0)
        self.assertEqual(len(manager_notifications['signature_required']), 1)
        self.assertEqual(len(manager_notifications['signature_required_other']), 1)

    def test_manager_reminded_to_sign_evaluation_they_wrote(self):
        pr = PerformanceReview.objects.create(
            status=PerformanceReview.EVALUATION_WRITTEN,
            employee=self.employee_employee,
            period_start_date=datetime.date.today(),
            period_end_date=datetime.date.today(),
            effective_date=datetime.date.today() + datetime.timedelta(60),
            description_reviewed_employee=True,
            evaluation_goals_manager='Some goals',
            evaluation_opportunities='Some opportunities',
            evaluation_successes='So great!',
            evaluation_type='P',
            factor_analysis='N',
            factor_communication='N',
            factor_dependability='N',
            factor_initiative='N',
            factor_interpersonal='N',
            factor_job_knowledge='N',
            factor_management='NA',
            factor_professionalism='N',
            factor_supervision='NA',
            factor_work_habits='N',
            factor_work_quality='N',
            factor_work_quantity='N',
            probationary_evaluation_type='N',
            step_increase='Y',
            top_step_bonus='Y'
        )

        # Initial reminder
        all_notifications = send_pr_reminder_emails()
        # There are the correct number of people receiving notifications
        self.assertEqual(len(all_notifications.keys()), 2)
        employee_notifications = all_notifications[self.employee_employee.user.email]
        manager_notifications = all_notifications[self.manager_employee.user.email]
        # There are the correct numnber of notifications of the correct type
        self.assertEqual(len(employee_notifications['review_to_write']), 0)
        self.assertEqual(len(employee_notifications['review_to_write_other']), 0)
        self.assertEqual(len(employee_notifications['signature_required']), 1)
        self.assertEqual(len(employee_notifications['signature_required_other']), 0)
        self.assertEqual(len(manager_notifications['review_to_write']), 0)
        self.assertEqual(len(manager_notifications['review_to_write_other']), 0)
        self.assertEqual(len(manager_notifications['signature_required']), 1)
        self.assertEqual(len(manager_notifications['signature_required_other']), 0)

        # 7 days after initial reminder
        reminder = SignatureReminder.objects.get(employee=self.manager_employee)
        reminder.date -= datetime.timedelta(7)
        reminder.next_date -= datetime.timedelta(7)
        reminder.save()
        all_notifications = send_pr_reminder_emails()
        # There are the correct number of people receiving notifications
        self.assertEqual(len(all_notifications.keys()), 2)
        manager_notifications = all_notifications[self.manager_employee.user.email]
        program_manager_notifications = all_notifications[self.program_manager_employee.user.email]
        # There are the correct numnber of notifications of the correct type
        self.assertEqual(len(manager_notifications['review_to_write']), 0)
        self.assertEqual(len(manager_notifications['review_to_write_other']), 0)
        self.assertEqual(len(manager_notifications['signature_required']), 1)
        self.assertEqual(len(manager_notifications['signature_required_other']), 0)
        self.assertEqual(len(program_manager_notifications['review_to_write']), 0)
        self.assertEqual(len(program_manager_notifications['review_to_write_other']), 0)
        self.assertEqual(len(program_manager_notifications['signature_required']), 0)
        self.assertEqual(len(program_manager_notifications['signature_required_other']), 1)

    def test_program_manager_reminded_to_sign_evaluation(self):
        pr = PerformanceReview.objects.create(
            status=PerformanceReview.EVALUATION_WRITTEN,
            employee=self.employee_employee,
            period_start_date=datetime.date.today(),
            period_end_date=datetime.date.today(),
            effective_date=datetime.date.today() + datetime.timedelta(60),
            description_reviewed_employee=True,
            evaluation_goals_manager='Some goals',
            evaluation_opportunities='Some opportunities',
            evaluation_successes='So great!',
            evaluation_type='P',
            factor_analysis='N',
            factor_communication='N',
            factor_dependability='N',
            factor_initiative='N',
            factor_interpersonal='N',
            factor_job_knowledge='N',
            factor_management='NA',
            factor_professionalism='N',
            factor_supervision='NA',
            factor_work_habits='N',
            factor_work_quality='N',
            factor_work_quantity='N',
            probationary_evaluation_type='N',
            step_increase='Y',
            top_step_bonus='Y'
        )
        Signature.objects.create(review=pr, employee=self.employee_employee)
        Signature.objects.create(review=pr, employee=self.manager_employee)

        # Initial reminder
        all_notifications = send_pr_reminder_emails()
        # There are the correct number of people receiving notifications
        self.assertEqual(len(all_notifications.keys()), 1)
        program_manager_notifications = all_notifications[self.program_manager_employee.user.email]
        # There are the correct numnber of notifications of the correct type
        self.assertEqual(len(program_manager_notifications['review_to_write']), 0)
        self.assertEqual(len(program_manager_notifications['review_to_write_other']), 0)
        self.assertEqual(len(program_manager_notifications['signature_required']), 1)
        self.assertEqual(len(program_manager_notifications['signature_required_other']), 0)

        # 7 days after initial reminder
        reminder = SignatureReminder.objects.get(employee=self.program_manager_employee)
        reminder.date -= datetime.timedelta(7)
        reminder.next_date -= datetime.timedelta(7)
        reminder.save()
        all_notifications = send_pr_reminder_emails()
        # There are the correct number of people receiving notifications
        self.assertEqual(len(all_notifications.keys()), 2)
        program_manager_notifications = all_notifications[self.program_manager_employee.user.email]
        deputy_director_notifications = all_notifications[self.deputy_director_employee.user.email]
        # There are the correct numnber of notifications of the correct type
        self.assertEqual(len(program_manager_notifications['review_to_write']), 0)
        self.assertEqual(len(program_manager_notifications['review_to_write_other']), 0)
        self.assertEqual(len(program_manager_notifications['signature_required']), 1)
        self.assertEqual(len(program_manager_notifications['signature_required_other']), 0)
        self.assertEqual(len(deputy_director_notifications['review_to_write']), 0)
        self.assertEqual(len(deputy_director_notifications['review_to_write_other']), 0)
        self.assertEqual(len(deputy_director_notifications['signature_required']), 0)
        self.assertEqual(len(deputy_director_notifications['signature_required_other']), 1)

    def test_deputy_director_reminded_to_sign_evaluation(self):
        pr = PerformanceReview.objects.create(
            status=PerformanceReview.EVALUATION_WRITTEN,
            employee=self.employee_employee,
            period_start_date=datetime.date.today(),
            period_end_date=datetime.date.today(),
            effective_date=datetime.date.today() + datetime.timedelta(60),
            description_reviewed_employee=True,
            evaluation_goals_manager='Some goals',
            evaluation_opportunities='Some opportunities',
            evaluation_successes='So great!',
            evaluation_type='P',
            factor_analysis='N',
            factor_communication='N',
            factor_dependability='N',
            factor_initiative='N',
            factor_interpersonal='N',
            factor_job_knowledge='N',
            factor_management='NA',
            factor_professionalism='N',
            factor_supervision='NA',
            factor_work_habits='N',
            factor_work_quality='N',
            factor_work_quantity='N',
            probationary_evaluation_type='N',
            step_increase='Y',
            top_step_bonus='Y'
        )
        Signature.objects.create(review=pr, employee=self.employee_employee)
        Signature.objects.create(review=pr, employee=self.manager_employee)
        Signature.objects.create(review=pr, employee=self.program_manager_employee)

        # Initial reminder
        all_notifications = send_pr_reminder_emails()
        # There are the correct number of people receiving notifications
        self.assertEqual(len(all_notifications.keys()), 1)
        deputy_director_notifications = all_notifications[self.deputy_director_employee.user.email]
        # There are the correct numnber of notifications of the correct type
        self.assertEqual(len(deputy_director_notifications['review_to_write']), 0)
        self.assertEqual(len(deputy_director_notifications['review_to_write_other']), 0)
        self.assertEqual(len(deputy_director_notifications['signature_required']), 1)
        self.assertEqual(len(deputy_director_notifications['signature_required_other']), 0)

        # 7 days after initial reminder
        reminder = SignatureReminder.objects.get(employee=self.deputy_director_employee)
        reminder.date -= datetime.timedelta(7)
        reminder.next_date -= datetime.timedelta(7)
        reminder.save()
        all_notifications = send_pr_reminder_emails()
        # There are the correct number of people receiving notifications
        self.assertEqual(len(all_notifications.keys()), 2)
        deputy_director_notifications = all_notifications[self.deputy_director_employee.user.email]
        division_director_notifications = all_notifications[self.division_director_employee.user.email]
        # There are the correct numnber of notifications of the correct type
        self.assertEqual(len(deputy_director_notifications['review_to_write']), 0)
        self.assertEqual(len(deputy_director_notifications['review_to_write_other']), 0)
        self.assertEqual(len(deputy_director_notifications['signature_required']), 1)
        self.assertEqual(len(deputy_director_notifications['signature_required_other']), 0)
        self.assertEqual(len(division_director_notifications['review_to_write']), 0)
        self.assertEqual(len(division_director_notifications['review_to_write_other']), 0)
        self.assertEqual(len(division_director_notifications['signature_required']), 0)
        self.assertEqual(len(division_director_notifications['signature_required_other']), 1)

    def test_division_director_reminded_to_sign_evaluation(self):
        pr = PerformanceReview.objects.create(
            status=PerformanceReview.EVALUATION_WRITTEN,
            employee=self.employee_employee,
            period_start_date=datetime.date.today(),
            period_end_date=datetime.date.today(),
            effective_date=datetime.date.today() + datetime.timedelta(60),
            description_reviewed_employee=True,
            evaluation_goals_manager='Some goals',
            evaluation_opportunities='Some opportunities',
            evaluation_successes='So great!',
            evaluation_type='P',
            factor_analysis='N',
            factor_communication='N',
            factor_dependability='N',
            factor_initiative='N',
            factor_interpersonal='N',
            factor_job_knowledge='N',
            factor_management='NA',
            factor_professionalism='N',
            factor_supervision='NA',
            factor_work_habits='N',
            factor_work_quality='N',
            factor_work_quantity='N',
            probationary_evaluation_type='N',
            step_increase='Y',
            top_step_bonus='Y'
        )
        Signature.objects.create(review=pr, employee=self.employee_employee)
        Signature.objects.create(review=pr, employee=self.manager_employee)
        Signature.objects.create(review=pr, employee=self.program_manager_employee)
        Signature.objects.create(review=pr, employee=self.deputy_director_employee)

        # Initial reminder
        all_notifications = send_pr_reminder_emails()
        # There are the correct number of people receiving notifications
        self.assertEqual(len(all_notifications.keys()), 1)
        division_director_notifications = all_notifications[self.division_director_employee.user.email]
        # There are the correct numnber of notifications of the correct type
        self.assertEqual(len(division_director_notifications['review_to_write']), 0)
        self.assertEqual(len(division_director_notifications['review_to_write_other']), 0)
        self.assertEqual(len(division_director_notifications['signature_required']), 1)
        self.assertEqual(len(division_director_notifications['signature_required_other']), 0)

        # 7 days after initial reminder
        reminder = SignatureReminder.objects.get(employee=self.division_director_employee)
        reminder.date -= datetime.timedelta(7)
        reminder.next_date -= datetime.timedelta(7)
        reminder.save()
        all_notifications = send_pr_reminder_emails()
        # There are the correct number of people receiving notifications
        self.assertEqual(len(all_notifications.keys()), 2)
        division_director_notifications = all_notifications[self.division_director_employee.user.email]
        executive_director_notifications = all_notifications[self.executive_director_employee.user.email]
        # There are the correct numnber of notifications of the correct type
        self.assertEqual(len(division_director_notifications['review_to_write']), 0)
        self.assertEqual(len(division_director_notifications['review_to_write_other']), 0)
        self.assertEqual(len(division_director_notifications['signature_required']), 1)
        self.assertEqual(len(division_director_notifications['signature_required_other']), 0)
        self.assertEqual(len(executive_director_notifications['review_to_write']), 0)
        self.assertEqual(len(executive_director_notifications['review_to_write_other']), 0)
        self.assertEqual(len(executive_director_notifications['signature_required']), 0)
        self.assertEqual(len(executive_director_notifications['signature_required_other']), 1)
    
    def test_hr_manager_reminded_to_sign_evaluation(self):
        pr = PerformanceReview.objects.create(
            status=PerformanceReview.EVALUATION_WRITTEN,
            employee=self.employee_employee,
            period_start_date=datetime.date.today(),
            period_end_date=datetime.date.today(),
            effective_date=datetime.date.today() + datetime.timedelta(60),
            description_reviewed_employee=True,
            evaluation_goals_manager='Some goals',
            evaluation_opportunities='Some opportunities',
            evaluation_successes='So great!',
            evaluation_type='P',
            factor_analysis='N',
            factor_communication='N',
            factor_dependability='N',
            factor_initiative='N',
            factor_interpersonal='N',
            factor_job_knowledge='N',
            factor_management='NA',
            factor_professionalism='N',
            factor_supervision='NA',
            factor_work_habits='N',
            factor_work_quality='N',
            factor_work_quantity='N',
            probationary_evaluation_type='N',
            step_increase='Y',
            top_step_bonus='Y'
        )
        Signature.objects.create(review=pr, employee=self.employee_employee)
        Signature.objects.create(review=pr, employee=self.manager_employee)
        Signature.objects.create(review=pr, employee=self.program_manager_employee)
        Signature.objects.create(review=pr, employee=self.deputy_director_employee)
        
        # Initial reminder
        self.assertEqual(SignatureReminder.objects.count(), 0)
        Signature.objects.create(review=pr, employee=self.division_director_employee)
        self.assertEqual(SignatureReminder.objects.count(), 1)
        
        pr.status = PerformanceReview.EVALUATION_APPROVED
        pr.save()

        # Subsequent reminder
        reminder = SignatureReminder.objects.get(employee=self.hr_manager_employee)
        reminder.date -= datetime.timedelta(2)
        reminder.next_date -= datetime.timedelta(2)
        reminder.save()
        all_notifications = send_pr_reminder_emails()
        # There are the correct number of people receiving notifications
        self.assertEqual(len(all_notifications.keys()), 1)
        hr_manager_notifications = all_notifications[self.hr_manager_employee.user.email]
        # There are the correct numnber of notifications of the correct type
        self.assertEqual(len(hr_manager_notifications['review_to_write']), 0)
        self.assertEqual(len(hr_manager_notifications['review_to_write_other']), 0)
        self.assertEqual(len(hr_manager_notifications['signature_required']), 1)
        self.assertEqual(len(hr_manager_notifications['signature_required_other']), 0)

        # 7 days after initial reminder
        reminder.delete()
        reminder = SignatureReminder.objects.get(employee=self.hr_manager_employee)
        reminder.date -= datetime.timedelta(7)
        reminder.next_date -= datetime.timedelta(7)
        reminder.save()
        all_notifications = send_pr_reminder_emails()
        # There are the correct number of people receiving notifications
        self.assertEqual(len(all_notifications.keys()), 2)
        hr_manager_notifications = all_notifications[self.hr_manager_employee.user.email]
        executive_director_notifications = all_notifications[self.executive_director_employee.user.email]
        # There are the correct numnber of notifications of the correct type
        self.assertEqual(len(hr_manager_notifications['review_to_write']), 0)
        self.assertEqual(len(hr_manager_notifications['review_to_write_other']), 0)
        self.assertEqual(len(hr_manager_notifications['signature_required']), 1)
        self.assertEqual(len(hr_manager_notifications['signature_required_other']), 0)
        self.assertEqual(len(executive_director_notifications['review_to_write']), 0)
        self.assertEqual(len(executive_director_notifications['review_to_write_other']), 0)
        self.assertEqual(len(executive_director_notifications['signature_required']), 0)
        self.assertEqual(len(executive_director_notifications['signature_required_other']), 1)
    
    def test_executive_director_reminded_to_sign_evaluation(self):
        pr = PerformanceReview.objects.create(
            status=PerformanceReview.EVALUATION_WRITTEN,
            employee=self.employee_employee,
            period_start_date=datetime.date.today(),
            period_end_date=datetime.date.today(),
            effective_date=datetime.date.today() + datetime.timedelta(60),
            description_reviewed_employee=True,
            evaluation_goals_manager='Some goals',
            evaluation_opportunities='Some opportunities',
            evaluation_successes='So great!',
            evaluation_type='P',
            factor_analysis='N',
            factor_communication='N',
            factor_dependability='N',
            factor_initiative='N',
            factor_interpersonal='N',
            factor_job_knowledge='N',
            factor_management='NA',
            factor_professionalism='N',
            factor_supervision='NA',
            factor_work_habits='N',
            factor_work_quality='N',
            factor_work_quantity='N',
            probationary_evaluation_type='N',
            step_increase='Y',
            top_step_bonus='Y'
        )
        Signature.objects.create(review=pr, employee=self.employee_employee)
        Signature.objects.create(review=pr, employee=self.manager_employee)
        Signature.objects.create(review=pr, employee=self.program_manager_employee)
        Signature.objects.create(review=pr, employee=self.deputy_director_employee)
        Signature.objects.create(review=pr, employee=self.division_director_employee)
        pr.status = PerformanceReview.EVALUATION_APPROVED
        pr.save()
        
        # Initial reminder
        self.assertEqual(SignatureReminder.objects.count(), 1)
        Signature.objects.create(review=pr, employee=self.hr_manager_employee)
        self.assertEqual(SignatureReminder.objects.count(), 2)
        
        pr.status = PerformanceReview.EVALUATION_HR_PROCESSED
        pr.save()

        # Subsequent reminder
        reminder = SignatureReminder.objects.get(employee=self.executive_director_employee)
        reminder.date -= datetime.timedelta(2)
        reminder.next_date -= datetime.timedelta(2)
        reminder.save()
        all_notifications = send_pr_reminder_emails()
        # There are the correct number of people receiving notifications
        self.assertEqual(len(all_notifications.keys()), 1)
        executive_director_notifications = all_notifications[self.executive_director_employee.user.email]
        # There are the correct numnber of notifications of the correct type
        self.assertEqual(len(executive_director_notifications['review_to_write']), 0)
        self.assertEqual(len(executive_director_notifications['review_to_write_other']), 0)
        self.assertEqual(len(executive_director_notifications['signature_required']), 1)
        self.assertEqual(len(executive_director_notifications['signature_required_other']), 0)

        # 7 days after initial reminder
        reminder.delete()
        reminder = SignatureReminder.objects.get(employee=self.executive_director_employee)
        reminder.date -= datetime.timedelta(7)
        reminder.next_date -= datetime.timedelta(7)
        reminder.save()
        all_notifications = send_pr_reminder_emails()
        # There are the correct number of people receiving notifications
        self.assertEqual(len(all_notifications.keys()), 2)
        executive_director_notifications = all_notifications[self.executive_director_employee.user.email]
        hr_manager_notifications = all_notifications[self.hr_manager_employee.user.email]
        # There are the correct numnber of notifications of the correct type
        self.assertEqual(len(executive_director_notifications['review_to_write']), 0)
        self.assertEqual(len(executive_director_notifications['review_to_write_other']), 0)
        self.assertEqual(len(executive_director_notifications['signature_required']), 1)
        self.assertEqual(len(executive_director_notifications['signature_required_other']), 0)
        self.assertEqual(len(hr_manager_notifications['review_to_write']), 0)
        self.assertEqual(len(hr_manager_notifications['review_to_write_other']), 0)
        self.assertEqual(len(hr_manager_notifications['signature_required']), 0)
        self.assertEqual(len(hr_manager_notifications['signature_required_other']), 1)
