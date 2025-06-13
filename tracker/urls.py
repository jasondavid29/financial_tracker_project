from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import IncomeViewSet, ExpenseViewSet, BudgetViewSet, login_page, register, TransactionListAPIView, \
    TransactionUpdateView
from . import views
from .views import TransactionListCreateAPIView
from .views import get_csrf_token
from .views import get_transactions


router = DefaultRouter()
router.register('income', IncomeViewSet)
router.register('expense', ExpenseViewSet)
router.register('budget', BudgetViewSet)

urlpatterns = [
    path('', views.index, name='index'),
    path('transactions/', TransactionListCreateAPIView.as_view(), name='transaction-list-create'),
    path("transactions/history/", TransactionListAPIView.as_view(), name="transaction-history"),
    path('transactions/update/<int:pk>/', TransactionUpdateView.as_view(), name='transaction-update'),
    path("transactions/delete/<int:pk>/", views.TransactionDeleteView.as_view(), name="transaction-delete"),
    path("get-csrf-token/", get_csrf_token, name="get_csrf_token"),
    path("login/", login_page, name="login"),
    path("register/", register, name="register"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("logout/", views.logout_user, name="logout"),
    path('income/', views.income_view, name='income'),  # This is your income chart page
    path('expense/', views.expense_view, name='expense'),
    path('export/csv/', views.export_transactions_csv, name='export_csv'),
    path('export/pdf/', views.export_transactions_pdf, name='export_pdf'),
    path('export-income-csv/', views.export_income_csv, name='export_income_csv'),
    path('export-income-pdf/', views.export_income_pdf, name='export_income_pdf'),
    path('export-expense-csv/', views.export_expense_csv, name='export_expense_csv'),
    path('export-expense-pdf/', views.export_expense_pdf, name='export_expense_pdf'),

]
