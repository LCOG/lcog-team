import csv
import datetime

from django.core.management.base import BaseCommand
from django.core.exceptions import MultipleObjectsReturned

from people.models import Employee, PerformanceReview, PRForm


class Command(BaseCommand):
    help = 'Imports reviews after exporting from Caselle'

    def add_arguments(self, parser):
        parser.add_argument('--path', type=str)

    def handle(self, *args, **options):
        path = options['path']
        if not path:
            path = 'people/management/reviews.csv'
        
        dataReader = csv.reader(open(path), delimiter=',', quotechar='"')
        employee_review_rows = [] # Initialize
        for row in dataReader:
            # Parse row data
            if len(row):
                if row[0] in [
                    'Employee Name',
                    'Notes: ',
                    '04/19/2019 12:50 PM - clid1559"',
                    '8/1/20.\n\n12/11/2020 07:05 PM - clid1559',
                    '$2,187.68.\n06/26/2020 04:37 PM - clid1559',
                    '3/1/20.\n\n11/25/2020 06:22 PM - clid1559',
                    'step.\n\n03/04/2024 09:54 AM - clid1559',
                    '11.3.\n\n05/10/2024 04:40 PM - clid1559',
                    'Report Criteria:',
                    'Include review notes',
                    'EA Range 25 Step 6 to EA Range 25 Step 7, and then a 1-step increase on 1/1/19 from EA Range 25 Step 7 to EA Range 25 Step 8.  So, I am putting her in for this pay period (as of 6/2/19) as a 2-step increase, and I am asking Payroll to process retroactive pay for her for the period of 1/1/18 to 12/31/18 (which includes a COLA at 7/1/18) at Step 6 and for the period 1/1/19 to 6/1/19 at Step 7.\n\n06/12/2019 05:57 PM - clid1559',
                    'putting her in for this pay period (as of 6/2/19) as a 2-step increase, and I am asking Payroll to process retroactive pay for her for the period of 1/1/18 to 12/31/18 (which includes a COLA at 7/1/18) at Step 6 and for the period 1/1/19 to 6/1/19 at Step 7.\n\n06/12/2019 05:57 PM - clid1559',
                    '4.\n10/26/2024 12:15 PM - clid1559',
                    '2024\n04/12/2024 03:10 PM - clid1559',
                    'received.\n\n03/17/2024 01:33 PM - clid1559'
                ]:
                    continue
                if row[0]:
                    # Create any new reviews for the previous employee
                    if len(employee_review_rows):
                        self.process_review_rows(employee_review_rows, employee)

                    # Start a new employee section
                    try:
                        number = row[1]
                    except IndexError:
                        import pdb; pdb.set_trace();
                    try:
                        employee = Employee.objects.get(number=number)
                    except MultipleObjectsReturned:
                        import pdb; pdb.set_trace();
                    except Employee.DoesNotExist:
                        # If the employee is not otherwise in the system, ignore them
                        continue
                    employee_review_rows = []
                elif row[1] and row[1].split(' ')[0] == 'PR':
                    if row[4] and not row[9]:
                        row[9] = datetime.datetime.strftime(datetime.datetime.strptime(row[4], '%m/%d/%Y') + datetime.timedelta(days=365), '%m/%d/%Y')
                    employee_review_rows += [row]
        
        self.stdout.write(self.style.SUCCESS('Successfully imported reviews.'))

    def process_review_rows(self, rows, employee):
        '''
        Creates a review for the employee based on the most recent review in the rows
        '''
        # Get the most recent review
        filtered_rows = filter(lambda row: row[4] != '' and row[9] != '', rows) # Remove rows without a date
        sorted_rows = sorted(filtered_rows, key=lambda row: datetime.datetime.strptime(row[9], '%m/%d/%Y'))
        most_recent_row = sorted_rows[-1]
        
        # Get the most recent review information
        review_date = datetime.datetime.strptime(most_recent_row[4], '%m/%d/%Y')
        next_review_date = datetime.datetime.strptime(most_recent_row[9], '%m/%d/%Y')
        try:   
            existing_reviews = PerformanceReview.objects.filter(employee=employee, period_start_date=review_date).exists()
            if not existing_reviews:
                # review_range = next_review_date - review_date
                # TODO: Implement other review forms once we have them
                if len(rows) > 1:
                    evaluation_type = PerformanceReview.ANNUAL_EVALUATION
                    form = PRForm.objects.get(name='All - 180 - Annual PR')
                else:
                    evaluation_type = PerformanceReview.PROBATIONARY_EVALUATION
                    form = PRForm.objects.get(name='EA - 90 - Probationary PR')
                PerformanceReview.objects.create(
                    employee=employee,
                    period_start_date=review_date,
                    period_end_date=next_review_date,
                    effective_date=next_review_date + datetime.timedelta(days=1),
                    evaluation_type=evaluation_type,
                    form=form
                )
                self.stdout.write(
                    'Created review for employee {} {} for period {} - {}'.format(employee.user.first_name, employee.user.last_name, review_date, next_review_date)
                )
                
        except PerformanceReview.DoesNotExist:
            pass


