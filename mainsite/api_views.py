import csv
from datetime import datetime
from io import StringIO
from ipaddress import ip_address
import json
import traceback

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404

from mainsite.helpers import record_error
from mainsite.models import MaintenanceMode, SecurityMessage, TrustedIPAddress
from mainsite.serializers import (
    FileUploadSerializer, SecurityMessageSerializer,
    TrustedIPSerializer
)
from people.models import PerformanceReview
from purchases.models import (
    Expense, ExpenseCard, ExpenseStatement, ExpenseStatementItem
)

class LargeResultsSetPagination(PageNumberPagination):
    page_size = 1000
    page_size_query_param = 'page_size'

# class EitherAuthenticatedOrOnSafelistPermission(permissions.BasePermission):
#     """
#     Ensure the request's IP address is on the safe list configured in Django
#     settings.
#     """

#     def has_permission(self, request, view):
#         is_authenticated = request.user.is_authenticated
#         if is_authenticated:
#             return True
        
#         remote_addr = request.META['REMOTE_ADDR']

#         # Allow if address is in the list of safe IPs in Django settings
#         for valid_ip in settings.REST_FRAMEWORK_TRUSTED_IPS_LIST:
#             if remote_addr == valid_ip or remote_addr.startswith(valid_ip):
#                 return True
#         # Allow if address is in the list of safe IPs in Django backend
#         for valid_ip in TrustedIPAddress.objects.all():
#             if remote_addr == valid_ip:
#                 return True
        
#         return False


class MaintenanceStatusView(viewsets.ViewSet):
    """
    Check if the site is in maintenance mode.
    This endpoint is publicly accessible (no authentication required).
    """
    permission_classes = []  # Allow unauthenticated access

    def list(self, request):
        maintenance = MaintenanceMode.get_instance()
        return Response({
            'enabled': maintenance.enabled,
            'message': maintenance.message
        })


class LogErrorView(viewsets.ViewSet):

    def create(self, request):
        record_error(
            json.dumps(request.data), None, request, traceback.format_exc()
        )
        return Response("Client error recorded", status=202)


class TrustedIPViewSet(viewsets.ViewSet):
    """
    Viewset listing trusted IP addresses
    """

    serializer_class = TrustedIPSerializer

    def list(self, request):
        admin_ips = []
        for ip in TrustedIPAddress.objects.all():
            current_ip = ip_address(ip.address)
            admin_ips.append(str(current_ip))
            if ip.address_range_end:
                range_end = ip_address(ip.address_range_end)
                while current_ip < range_end:
                    current_ip += 1
                    admin_ips.append(str(current_ip))
        settings_ips = settings.REST_FRAMEWORK_TRUSTED_IPS_LIST
        trusted_ips = list(admin_ips) + settings_ips
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            client_ip = x_forwarded_for.split(',')[0]
        else:
            client_ip = request.META.get('REMOTE_ADDR')
        return Response(client_ip in trusted_ips)


class FileUploadViewSet(viewsets.ViewSet):
    serializer_class = FileUploadSerializer
    
    def create(self, request):
        files = request.FILES.values()
        if not files:
            return Response(data="Missing files", status=400)
        app_label = request.data.get('content_type_app_label')
        model = request.data.get('content_type_model')
        if not app_label or not model:
            return Response(data="Missing content type", status=400)
        # TODO: Trying to generalize this with content_type in case we want to
        # use this for generic models, but maybe this is not necessary as there
        # will always be custom requirements.
        # content_type = ContentType.objects.get(app_label=app_label, model=model)
        object_pk = request.data.get('object_pk')
        data = {}
        if request.data.get('data'):
            data = json.loads(request.data.get('data'))
        
        if model == 'performancereview':
            if not object_pk:
                return Response(data="Missing object PK", status=400)
            try:
                pr = PerformanceReview.objects.get(pk=object_pk)
            except PerformanceReview.DoesNotExist:
                return Response(data="Invalid PR PK", status=400)
            for file in files:
                pr.signed_position_description = file
            pr.save()
            return Response(
                data=request.build_absolute_uri(
                    pr.signed_position_description.url
                ),
                status=200
            )
        elif model == 'expensestatement':
            statements = []
            month = data.get('month')
            year = data.get('year')
            if not month or not year:
                return Response(data="Missing month or year", status=400)
            for file in files:
                rows = file.read().decode('utf-8').split('\n')
                items = []
                for row in rows[1:]:
                    try: 
                        if row == '':
                            continue
                        # Parse CSV row with python in case there are commas
                        # in the description, e.g.
                        s_row=StringIO(row)
                        row_items=list(
                            csv.reader(s_row, skipinitialspace=True)
                        )[0]
                        acct = row_items[0].replace('\"','')
                        t_date = row_items[2]
                        desc = row_items[4].replace('\"','').rstrip()
                        amt = row_items[5]
                        items.append({
                            'card': acct[-4:],
                            'date':
                                datetime.strptime(t_date, '%m/%d/%Y').date(),
                            'description': desc,
                            'amount': float(amt)
                        })
                    except Exception as e:
                        m = 'Error processing an expense statement'
                        if acct:
                            m += ' for account ending in {}'.format(acct[-4:])
                        record_error(m, e, request, traceback.format_exc())
                        return Response(data=m, status=400)
                if len(items):
                    ec = ExpenseCard.objects.get_or_create(
                        last4=items[0]['card']
                    )[0]
                    es, created = ExpenseStatement.objects.get_or_create(
                        card=ec, month=month, year=year
                    )
                    if created:
                        for item in items:
                            ExpenseStatementItem.objects.create(
                                statement=es,
                                date=item['date'],
                                description=item['description'],
                                amount=item['amount']
                            )
                        statements.append(
                            request.build_absolute_uri(es)
                        )
            if not statements:
                return Response(data="No new statements uploaded", status=200)
            else:
                return Response(data=statements, status=201)
        elif model == 'expense':
            if not object_pk:
                return Response(data="Missing object PK", status=400)
            try:
                expense = Expense.objects.get(pk=object_pk)
            except Expense.DoesNotExist:
                return Response(data="Invalid Expense PK", status=400)
            for file in files:
                expense.receipt = file
            expense.save()
            return Response(
                data=request.build_absolute_uri(expense.receipt.url),
                status=200
            )


class SecurityMessageViewSet(viewsets.ModelViewSet):
    """
    A simple ViewSet for viewing the current Security Message.
    """

    queryset = SecurityMessage.objects.all()
    serializer_class = SecurityMessageSerializer

    def retrieve(self, request, pk=None):
        user = request.user
        if user.is_authenticated:
            queryset = SecurityMessage.objects.all()
        else:
            queryset = SecurityMessage.objects.none()
        security_message = get_object_or_404(queryset, pk=pk)
        serializer = SecurityMessageSerializer(security_message, 
            context={'request': request})
        return Response(serializer.data)
    
    def list(self, request):
        user = request.user
        if user.is_authenticated:
            if user.is_staff:
                queryset = SecurityMessage.objects.all()
            else:
                queryset = SecurityMessage.objects.filter(employee__user=user)
        else:
            queryset = SecurityMessage.objects.none()
        serializer = SecurityMessageSerializer(
            queryset, many=True, context={'request': request}
        )
        return Response(serializer.data)

    @action(detail=False)
    def get_latest_security_message(self, request):
        security_message = SecurityMessage.objects.filter(active=True).latest()
        serialized_message = SecurityMessageSerializer(security_message,
            context={'request': request})
        return Response(serialized_message.data)