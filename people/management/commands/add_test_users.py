import json
import os

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from rest_framework.authtoken.models import Token

from people.models import Employee, JobTitle, UnitOrProgram


class Command(BaseCommand):
    help = 'Adds test users for development'

    def handle(self, *args, **options):
        # Passwords
        __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
        f = open(os.path.join(__location__, 'test_user_data.json'))
        pw_data = json.load(f)
        
        unit = UnitOrProgram.objects.get(name='Test Unit')
        ed = Employee.objects.get(is_executive_director=True)

        # Division Director
        dd = User.objects.get_or_create(username='divisiondirector', email='divisiondirector@lcog-or.gov', first_name='Division', last_name='Director')[0]
        dd.set_password(pw_data['divisiondirector'])
        dd.save()
        Token.objects.get_or_create(user=dd)
        dd_title = JobTitle.objects.get_or_create(name='Director')[0]
        dd_e = Employee.objects.get_or_create(user=dd, manager=ed, unit_or_program=unit, job_title=dd_title, is_division_director=True)[0]

        # Program Manager
        pm = User.objects.get_or_create(username='programmanager', email='programmanager@lcog-or.gov', first_name='Program', last_name='Manager')[0]
        pm.set_password(pw_data['programmanager'])
        pm.save()
        Token.objects.get_or_create(user=pm)
        pm_title = JobTitle.objects.get_or_create(name='Program Manager')[0]
        pm_e = Employee.objects.get_or_create(user=pm, manager=dd_e, unit_or_program=unit, job_title=pm_title)[0]

        # Manager
        man = User.objects.get_or_create(username='manager', email='manager@lcog-or.gov', first_name='Manager', last_name='Person')[0]
        man.set_password(pw_data['manager'])
        man.save()
        Token.objects.get_or_create(user=man)
        man_title = JobTitle.objects.get_or_create(name='Manager')[0]
        man_e = Employee.objects.get_or_create(user=man, manager=pm_e, unit_or_program=unit, job_title=man_title)[0]

        em_title = JobTitle.objects.get_or_create(name='Employee')[0]
        
        # Employee 1
        em_1 = User.objects.get_or_create(username='employee1', email='employee1@lcog-or.gov', first_name='Employee', last_name='One')[0]
        em_1.set_password(pw_data['employee1'])
        em_1.save()
        Token.objects.get_or_create(user=em_1)
        Employee.objects.get_or_create(user=em_1, manager=man_e, unit_or_program=unit, job_title=em_title)[0]

        # Employee 2
        em_2 = User.objects.get_or_create(username='employee2', email='employee2@lcog-or.gov', first_name='Employee', last_name='Two')[0]
        em_2.set_password(pw_data['employee2'])
        em_2.save()
        Token.objects.get_or_create(user=em_2)
        Employee.objects.get_or_create(user=em_2, manager=man_e, unit_or_program=unit, job_title=em_title)[0]

        # Employee 3
        em_3 = User.objects.get_or_create(username='employee3', email='employee3@lcog-or.gov', first_name='Employee', last_name='Three')[0]
        em_3.set_password(pw_data['employee3'])
        em_3.save()
        Token.objects.get_or_create(user=em_3)
        Employee.objects.get_or_create(user=em_3, manager=man_e, unit_or_program=unit, job_title=em_title)[0]

        # IS Employee
        is_emp = User.objects.get_or_create(username='isemployee', email='isemployee@lcog-or.gov', first_name='IS', last_name='Employee')[0]
        is_emp.set_password(pw_data['isemployee'])
        is_emp.save()
        Token.objects.get_or_create(user=is_emp)
        is_emp_title = JobTitle.objects.get_or_create(name='LAN Administrator')[0]
        Employee.objects.get_or_create(user=is_emp, manager=man_e, unit_or_program=unit, job_title=is_emp_title)[0]
        
        self.stdout.write(self.style.SUCCESS('Successfully created test users.'))
