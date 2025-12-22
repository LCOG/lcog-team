from django.contrib.auth.models import User

from rest_framework import status, viewsets
from rest_framework.response import Response

from phish.models import PhishReport
from phish.serializers import PhishReportSerializer


class PhishReportViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Phish Reports to be viewed or edited.
    """
    queryset = PhishReport.objects.all().order_by('-pk')
    serializer_class = PhishReportSerializer

    def get_queryset(self):
        """
        Show nothing to unauthenticated users.
        """
        user = self.request.user
        employee = getattr(user, 'employee', None)
        if user.is_authenticated:
            if user.is_superuser:
                return super().get_queryset()
            else:
                if employee and employee.can_view_phish():
                    return PhishReport.objects.for_employee(employee)
                else:
                    return PhishReport.objects.none()
        else:
            queryset = PhishReport.objects.none()
        return queryset

    def create(self, request, *args, **kwargs):
        """
        Create a PhishReport with employee email and email message.
        """
        employee_email = request.data.get('employee_email')
        email_message = request.data.get('email_message')
        
        if not employee_email or not email_message:
            return Response(
                {'error': 'employee_email and email_message are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get or create employee based on email
        try:
            user = User.objects.get(email=employee_email)
            employee = user.employee
        except User.DoesNotExist:
            return Response(
                {'error': 'User with this email does not exist'},
                status=status.HTTP_404_NOT_FOUND
            )
        except AttributeError:
            return Response(
                {'error': 'User does not have an associated employee profile'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        phish_report = PhishReport.objects.create(
            employee=employee,
            message=email_message
        )
        
        serializer = self.get_serializer(phish_report)
        return Response(serializer.data, status=status.HTTP_201_CREATED)