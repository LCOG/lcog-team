import csv

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from people.models import Division, Employee, JobTitle, UnitOrProgram


class Command(BaseCommand):
    help = 'Imports employees after exporting from Caselle'

    def add_arguments(self, parser):
        parser.add_argument('--path', type=str)

    def get_title(self, title):
        new_title = title
        if title in ['Senior Financial Analyst']:
            new_title = 'Senior Financial Analyst (Government Services)'
        elif title in ['IS Data Center & Systems Manager']:
            new_title = 'Data Center and Systems Manager'
        elif title in ['GIS Senior Analyst']:
            new_title = 'GIS Senior'
        elif title in ['IS Assistant']:
            new_title = 'IS Assistant (Help Desk)'
        elif title in ['Safe Routes to School Coord.']:
            new_title = 'Safe Routes to School Coordinator'
        elif title in ['Adult Protective Servs. Specialist']:
            new_title = 'APS Specialist'
        elif title in ['APS Lead Specialist']:
            new_title = 'APS Specialist Lead Worker'
        elif title in ['Case Manager.']:
            new_title = 'Case Manager'
        elif title in ['Case Manager - Housing Navigator Focus']:
            new_title = 'Case Manager: Housing Navigator Focus'
        elif title in ['Health Promotion Disease Prevention Program Coord.']:
            new_title = 'Disease Prevention & Health Promotion Program Coordinator'
        elif title in ['Senior and Disability Services Director']:
            new_title = 'Division Director'
        elif title in ['HCW Specialist']:
            new_title = 'Home Care Worker Specialist'
        elif title in ['Licensing & Monitoring Assistant']:
            new_title = 'Licensing and Monitoring Assistant'
        elif title in ['Licensing & Monitoring Specialist']:
            new_title = 'Licensing and Monitoring Specialist'
        elif title in ['Pre Admission Screener']:
            new_title = 'Pre-Admission Screener'
        elif title in ['Senior Meals Kitchen Assistant']:
            new_title = 'Senior Meals - Kitchen Assistant'
        elif title in ['Senior Meals Site Coordinator']:
            new_title = 'Senior Meals - Site Coordinator'
        elif title in ['Senior Meals Lead']:
            new_title = 'Senior Meals Lead Worker'
        elif title in ['TAD / Case Manager']:
            new_title = 'Transition and Diversion Case Manager'
        return new_title

    def handle(self, *args, **options):
        # Set up database if new
        if not Division.objects.filter(name='Administrative Services').count():
            d = Division.objects.create(name='Administrative Services')
            UnitOrProgram.objects.create(name='-', division=d)
            UnitOrProgram.objects.create(name='Administration', division=d)
        if not Division.objects.filter(name='Government Services').count():
            d = Division.objects.create(name='Government Services')
            UnitOrProgram.objects.create(name='-', division=d)
            UnitOrProgram.objects.create(name='Business Services', division=d)
            UnitOrProgram.objects.create(name='GIS', division=d)
            UnitOrProgram.objects.create(name='Information Services', division=d)
            UnitOrProgram.objects.create(name='MetroTV Services', division=d)
            UnitOrProgram.objects.create(name='Planning Services', division=d)
            UnitOrProgram.objects.create(name='Technology Services', division=d)
            UnitOrProgram.objects.create(name='Telecom', division=d)
            UnitOrProgram.objects.create(name='Transport Services', division=d)
        if not Division.objects.filter(name='Senior & Disability Services').count():
            d = Division.objects.create(name='Senior & Disability Services')
            UnitOrProgram.objects.create(name='-', division=d)
            UnitOrProgram.objects.create(name='Area Plan', division=d)
            UnitOrProgram.objects.create(name='Senior Meals', division=d)
        if not Division.objects.filter(name='Test Division').count():
            d = Division.objects.create(name='Test Division')
            UnitOrProgram.objects.create(name='-', division=d)
            UnitOrProgram.objects.create(name='Test Unit', division=d)
        
        # Import from file
        path = options['path']
        if not path:
            path = 'people/management/employees.csv'
        
        # Keep track of all employee numbers to deactivate removed employees
        numbers_in_file = []

        dataReader = csv.reader(open(path), delimiter=',', quotechar='"')
        for row in dataReader:
            # Parse row data
            number = row[0]
            last_name = row[1]
            first_name = row[2]
            email = row[3].lower()

            if not email:
                self.stdout.write("vvvvvvvvvvvv WARNING vvvvvvvvvvv")
                self.stdout.write(
                    'No email for employee {} {}'.format(first_name, last_name)
                )
                self.stdout.write("^^^^^^^^^^^^ WARNING ^^^^^^^^^^^^")
                username = first_name[0].lower() + last_name.lower()
            else:
                username = email
            
            numbers_in_file.append(int(number))
            
            title = row[4]
            job_title, created = JobTitle.objects.get_or_create(
                name=self.get_title(title)
            )
            if created:
                self.stdout.write("vvvvvvvvvvvv WARNING vvvvvvvvvvv")
                self.stdout.write(
                    'Created job title {} for employee {} {}'.format(
                        job_title, first_name, last_name
                    )
                )
                self.stdout.write("^^^^^^^^^^^^ WARNING ^^^^^^^^^^^^")
            
            department_col_pieces = row[5].split(' ')
            if department_col_pieces[0] == 'PR':
                department_col_pieces = department_col_pieces[1:]
            if department_col_pieces[-1] == 'Admin':
                department_col_pieces = department_col_pieces[0:-1]
            if len(department_col_pieces) == 1:
                department = row[5]
            else:
                if any([
                    (department_col_pieces[1] == 'Panduro' and department_col_pieces[2] == 'Melendez'),
                    (department_col_pieces[1] == 'Magana' and department_col_pieces[2] == 'Jr.')
                ]):
                    # Deal with two last names
                    department = " ".join(department_col_pieces[0:-2])
                else:
                    department = " ".join(department_col_pieces[0:-1])
            department = department.strip()
            if department in ['Technology Services']:
                unit_or_program = UnitOrProgram.objects.get(name='Technology Services')
            elif department in ['Business Services', 'Business Services GS']:
                unit_or_program = UnitOrProgram.objects.get(name='Business Services')
            elif department in ['MetroTV Services', 'MetroTV Services GS']:
                unit_or_program = UnitOrProgram.objects.get(name='MetroTV Services')
            elif department in ['Planning Services', 'Planning Svcs', 'Planning Svcs GS', 'Planning Services GS']:
                unit_or_program = UnitOrProgram.objects.get(name='Planning Services')
            elif department in ['Administration', 'Administration FD', 'Administration GS']:
                unit_or_program = UnitOrProgram.objects.get(name='Administration')
            elif department in ['Senior & Disability Services', 'SDS', 'Senior & Disablility', 'Senior & Disablility Services', 'Senior $ Disability Services', 'Senior & Diability Services', 'S&DS']:
                unit_or_program = UnitOrProgram.objects.get(division__name='Senior & Disability Services', name='-')
            elif department in ['Govt Services', 'Gov Svs']:
                unit_or_program = UnitOrProgram.objects.get(division__name='Government Services', name='-')
            elif department in ['Transport Services', 'Transport Service', 'Transport Service GS']:
                unit_or_program = UnitOrProgram.objects.get(name='Transport Services')
            else:
                raise ValueError('Unknown department {}'.format(department))

            # Get or create user by employee number. Update user names if necessary.
            try:
                user = User.objects.get(employee__number=number)
                if user.first_name != first_name or user.last_name != last_name:
                    user.first_name = first_name
                    user.last_name = last_name
                    user.save()
                    self.stdout.write(
                        'Updated user {} {} name'.format(user.first_name, user.last_name)
                    )
                
                # TEMP: Keep @lcog-or.gov emails until Caselle is updated
                if user.email.endswith('@lcog-or.gov'):
                    username = user.email

                if user.username != username:
                    user.username = username
                    user.save()
                    self.stdout.write(
                        'Updated user {} {} username to {}'.format(user.first_name, user.last_name, user.username)
                    )
                if user.email != email:
                    # Don't update email if we're just updating from @lcog-or.gov to @lcog.org
                    if user.email.endswith('@lcog-or.gov') and email.endswith('@lcog.org'):
                        pass
                        # self.stdout.write(
                        #     'Skipping email update for user {} {} from {} to {}'
                        #         .format(user.first_name, user.last_name, user.email, email)
                        # )
                    else:
                        user.email = email
                        user.save()
                        self.stdout.write(
                            'Updated user {} {} email to {}'.format(user.first_name, user.last_name, user.email)
                        )
            except User.DoesNotExist:
                try:
                    user = User.objects.create(email=email, username=username, first_name=first_name, last_name=last_name)
                except Exception as e:
                    self.stdout.write("vvvvvvvvvvvv EXCEPTION vvvvvvvvvvv")
                    self.stdout.write(
                        'Error creating user {} {}: {}'.format(first_name, last_name, str(e))
                    )
                    self.stdout.write("^^^^^^^^^^^^ EXCEPTION ^^^^^^^^^^^^")
                    continue
                self.stdout.write(
                    'Created user {} {}'.format(user.first_name, user.last_name)
                )
                
            # Get or create employee. Activate them if they are a returning
            # employee. Update employee title and department if necessary.
            try:
                employee = Employee.objects.get(user=user)
                if not employee.active:
                    employee.active = True
                    employee.save()
                    self.stdout.write(
                        'Reactivated returning employee {} {}'.format(employee.user.first_name, employee.user.last_name)
                    )
                updated_title = employee.job_title != job_title
                updated_department = employee.unit_or_program != unit_or_program
                if updated_title or updated_department:
                    if updated_title:
                        old_title = employee.job_title
                        employee.job_title = job_title
                        employee.save()
                        self.stdout.write(
                            'Updated employee {} {} title from {} to {}'
                                .format(
                                    employee.user.first_name,
                                    employee.user.last_name,
                                    old_title,
                                    job_title
                                )
                        )
                    if updated_department:
                        employee.unit_or_program = unit_or_program
                        employee.save()
                        self.stdout.write(
                            'Updated employee {} {} department'.format(employee.user.first_name, employee.user.last_name)
                        )
            except Employee.DoesNotExist:
                employee = Employee.objects.create(user=user, number=number, job_title=job_title, unit_or_program=unit_or_program)
                self.stdout.write(
                    'Created employee {} {}'.format(employee.user.first_name, employee.user.last_name)
                )

        # Deactivate any employee not in the list
        for employee in Employee.active_objects.all():
            if employee.number not in numbers_in_file and not employee.temporary:
                employee.active = False
                employee.save()
                self.stdout.write(
                    'Deactivated employee {} {}'.format(employee.user.first_name, employee.user.last_name)
                )

        # Add managers
        dataReader = csv.reader(open(path), delimiter=',', quotechar='"')
        for row in dataReader:
            number = row[0]
            user = User.objects.get(employee__number=number)
            employee = Employee.objects.get(user=user)
            department_col_pieces = row[5].split(' ')
            if department_col_pieces[0] == 'PR':
                department_col_pieces = department_col_pieces[1:]
            if department_col_pieces[-1] == 'Admin':
                department_col_pieces = department_col_pieces[0:-1]
            if len(department_col_pieces) > 1:
                if (department_col_pieces[1] == 'Panduro' and department_col_pieces[2] == 'Melendez'):
                    # Deal with two last names
                    manager_last_name = " ".join(department_col_pieces[-2:])
                else:
                    manager_last_name = department_col_pieces[-1]
            else:
                manager_last_name = None

            if manager_last_name:
                try:
                    if manager_last_name == 'Moore':
                        manager = Employee.objects.get(organization__name="LCOG", is_executive_director=True)
                    elif manager_last_name == 'Johnson':
                        manager = Employee.objects.get(user__last_name=manager_last_name, user__first_name='Lynn')
                    elif manager_last_name == 'Goodman':
                        manager = Employee.objects.get(user__last_name=manager_last_name, user__first_name='Micah')
                    elif manager_last_name == 'Davies':
                        manager = Employee.objects.get(user__last_name=manager_last_name, user__first_name='Nancy')
                    elif manager_last_name == 'Sheelar2': # WTF
                        manager = Employee.objects.get(user__last_name='Sheelar', user__first_name='Stephanie')
                    elif manager_last_name == 'Newall': # Nicole Wilbur changed last name
                        manager = Employee.objects.get(user__last_name='Wilbur', user__first_name='Nicole')
                    elif manager_last_name == 'Crowder':
                        manager = Employee.objects.get(user__last_name='Crowder', user__first_name='Jordan')
                    elif manager_last_name == 'Wright':
                        manager = Employee.objects.get(user__last_name='Wright', user__first_name='Vicki')
                    elif manager_last_name == 'Sowards': # Sowards doesn't exist
                        manager = Employee.objects.get(user__last_name='Sheelar', user__first_name='Stephanie')
                    elif manager_last_name == 'Harris': # Currently two 'Harris' managers: Karen and Marian Harris. I have no way of distinguishing between them, so just pick one.
                        manager = Employee.objects.get(user__last_name='Harris', user__first_name='Karen')
                    elif manager_last_name == 'Thompson':
                        manager = Employee.objects.get(user__last_name='Thompson', user__first_name='Paul')
                    elif manager_last_name == 'Blair':
                        manager = Employee.objects.get(user__last_name='Blair', user__first_name='Deborah')
                    elif manager_last_name == 'Campbell':
                        manager = Employee.objects.get(user__last_name='Campbell', user__first_name='Laura')
                    elif manager_last_name == 'Callister':
                        manager = Employee.objects.get(user__last_name='Callister', user__first_name='Jacob')
                    elif manager_last_name == 'Wilson':
                        manager = Employee.objects.get(user__last_name='Wilson', user__first_name='Daniel')
                    else:
                        try:
                            manager = Employee.active_objects.get(user__last_name=manager_last_name)
                        except Employee.MultipleObjectsReturned:
                            self.stdout.write("vvvvvvvvvvvv EXCEPTION vvvvvvvvvvv")
                            self.stdout.write(
                                'Multiple managers with last name {}'.format(manager_last_name)
                            )
                            self.stdout.write("^^^^^^^^^^^^ EXCEPTION ^^^^^^^^^^^^")
                            manager = Employee.objects.get(user__email='dwilson@lcog-or.gov')
                    if employee.manager != manager:
                        employee.manager = manager
                        employee.save()
                        self.stdout.write(
                            'Added manager {} {} for employee {} {}'.format(manager.user.first_name, manager.user.last_name, employee.user.first_name, employee.user.last_name)
                        )
                except Employee.DoesNotExist:
                    pass
        
        self.stdout.write(self.style.SUCCESS('Successfully imported users.'))