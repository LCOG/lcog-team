from rest_framework import routers
from rest_framework.authtoken.views import obtain_auth_token

from django.urls import include, path

from deskreservation.api_views import DeskReservationViewSet, DeskViewSet
from mainsite.api_views import (
    FileUploadViewSet, LogErrorView, SecurityMessageViewSet, TrustedIPViewSet
)
from mainsite.views import (
    obtain_auth_token_without_password, obtain_zoom_access_token
)
from meals.api_views import AddressLatLong, MealStopViewSet
from people.api_views import (
    CurrentUserView, EmployeeViewSet, GroupViewSet,
    JobTitleViewSet, PerformanceReviewViewSet, ReviewNoteViewSet,
    SignatureViewSet, TeleworkApplicationFileUploadViewSet,
    TeleworkApplicationViewSet, TeleworkSignatureViewSet, UnitViewSet,
    UserViewSet, ViewedSecurityMessageViewSet
)
from phish.api_views import (
    PhishReportViewSet, PhishAssignmentViewSet, PhishTemplateViewSet,
    TrainingAssignmentViewSet, TrainingTemplateViewSet
)
from purchases.api_views import (
    ExpenseGLViewSet, ExpenseMonthViewSet, ExpenseMonthLockViewSet,
    ExpenseStatementViewSet, ExpenseViewSet
)
from responsibilities.api_views import (
    ResponsibilityViewSet, TagViewSet as ResponsibilityTagViewSet
)
from timeoff.api_views import TimeOffRequestViewSet
from workflows.api_views import (
    EmployeeTransitionViewSet, ProcessInstanceViewSet, ProcessViewSet,
    RoleViewSet, StepChoiceViewSet, StepInstanceViewSet, StepViewSet,
    TransitionChangeViewSet, WorkflowInstanceViewSet, WorkflowViewSet
)


urlpatterns = [
    path('api-auth/', include('rest_framework.urls')),
    path('api-token-auth/', obtain_auth_token_without_password),
    path('api-token-auth-password/', obtain_auth_token),
    path('v1/current-user/', CurrentUserView.as_view(), name='current_user'),
    path(
        'v1/address-lat-long/',
        AddressLatLong.as_view(),
        name='address_lat_long'
    ),
    path('v1/zoom-access-token/', obtain_zoom_access_token),
]

router = routers.DefaultRouter(trailing_slash=False)
# People
router.register('v1/user', UserViewSet)
router.register('v1/groups', GroupViewSet)
router.register('v1/employee', EmployeeViewSet)
router.register('v1/jobtitle', JobTitleViewSet)
router.register('v1/unit', UnitViewSet)
# Responsibilities
router.register('v1/responsibilities', ResponsibilityViewSet)
router.register('v1/responsibilitytags', ResponsibilityTagViewSet)
# Desk Reservation
router.register('v1/desk', DeskViewSet)
router.register('v1/deskreservation', DeskReservationViewSet)
# Expenses
router.register('v1/expense-gl', ExpenseGLViewSet)
router.register('v1/expense', ExpenseViewSet)
router.register('v1/expense-month', ExpenseMonthViewSet)
router.register('v1/expense-month-lock', ExpenseMonthLockViewSet)
router.register('v1/expense-statement', ExpenseStatementViewSet)
# Performance Reviews
router.register('v1/review', PerformanceReviewViewSet)
router.register('v1/signature', SignatureViewSet)
router.register('v1/reviewnote', ReviewNoteViewSet)
# Phishing
router.register('v1/phish-report', PhishReportViewSet, basename='phish-report')
router.register(
    'v1/phish-template', PhishTemplateViewSet, basename='phish-template'
)
router.register(
    'v1/phish-assignment', PhishAssignmentViewSet, basename='phish-assignment'
)
router.register(
    'v1/training-template', TrainingTemplateViewSet,
    basename='training-template'
)
router.register(
    'v1/training-assignment', TrainingAssignmentViewSet,
    basename='training-assignment'
)
# Telework
router.register(
    'v1/telework-fileupload', TeleworkApplicationFileUploadViewSet,
    basename='telework-fileupload'
)
router.register('v1/teleworkapplication', TeleworkApplicationViewSet)
router.register('v1/teleworksignature', TeleworkSignatureViewSet)
# Security Messages
router.register('v1/securitymessage', SecurityMessageViewSet)
router.register('v1/viewedsecuritymessage', ViewedSecurityMessageViewSet)
# Time Off
router.register('v1/timeoffrequest', TimeOffRequestViewSet)
# Workflow
router.register('v1/process', ProcessViewSet)
router.register('v1/processinstance', ProcessInstanceViewSet)
router.register('v1/role', RoleViewSet)
router.register('v1/step', StepViewSet)
router.register('v1/stepchoice', StepChoiceViewSet)
router.register('v1/stepinstance', StepInstanceViewSet)
router.register('v1/workflow', WorkflowViewSet)
router.register('v1/workflowinstance', WorkflowInstanceViewSet)
router.register('v1/employeetransition', EmployeeTransitionViewSet)
router.register('v1/transitionchange', TransitionChangeViewSet)
# Meals on Wheels
router.register('v1/mealstop', MealStopViewSet)
# Utilities
router.register('v1/log-error', LogErrorView, basename='log-error')
router.register('v1/fileupload', FileUploadViewSet, basename='fileupload')
router.register('v1/trustedip', TrustedIPViewSet, basename='trustedip')

urlpatterns = router.urls + urlpatterns
