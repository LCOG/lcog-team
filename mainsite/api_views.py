from datetime import datetime
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
from mainsite.models import SecurityMessage, TrustedIPAddress
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
    # permission_classes = [IsAuthenticated]

    # def list(self, request):
    #     queryset = PerformanceReview.objects.all()
    #     serializer = PerformanceReviewFileUploadSerializer(queryset, many=True, context={'request': request})
    #     return Response(serializer.data)
    
    # def retrieve(self, request, pk=None):
    #     queryset = PerformanceReview.objects.all()
    #     pr = get_object_or_404(queryset, pk=pk)
    #     serializer = PerformanceReviewFileUploadSerializer(pr, context={'request': request})
    #     return Response(serializer.data)
    
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
                        row_items = row.split(',')
                        acct = row_items[0].replace('\"','')
                        t_date = row_items[2]
                        desc = row_items[4].replace('\"','').rstrip()
                        amt = row_items[5]
                        items.append({
                            'card': int(acct[-4:]),
                            'date':
                                datetime.strptime(t_date, '%m/%d/%Y').date(),
                            'description': desc,
                            'amount': float(amt)
                        })
                    except IndexError:
                        pass
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
        queryset = SecurityMessage.objects.all()
        security_message = get_object_or_404(queryset, pk=pk)
        serializer = SecurityMessageSerializer(security_message, 
            context={'request': request})
        return Response(serializer.data)

    @action(detail=False)
    def get_latest_security_message(self, request):
        security_message = SecurityMessage.objects.filter(active=True).latest()
        serialized_message = SecurityMessageSerializer(security_message,
            context={'request': request})
        return Response(serialized_message.data)