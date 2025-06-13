from rest_framework import viewsets, generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.middleware.csrf import get_token
from rest_framework.authtoken.models import Token
from django.contrib.auth.decorators import login_required
from .models import Income, Expense, Budget, Transaction
from .serializers import IncomeSerializer, ExpenseSerializer, BudgetSerializer, TransactionSerializer
from django.contrib.auth import authenticate, logout, update_session_auth_hash
from .forms import RegisterForm
from django.contrib.auth import login
from django.contrib import messages
from django.db.models import Sum
from rest_framework.views import APIView
from django.core.serializers.json import DjangoJSONEncoder
from django.utils.dateformat import DateFormat
from rest_framework.generics import DestroyAPIView
from rest_framework.exceptions import PermissionDenied
from django.core.mail import EmailMessage
from django.conf import settings
from .forms import ContactForm
from django.db.models.functions import TruncMonth
import calendar
import json
from io import BytesIO
import csv
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from django.http import HttpResponse


class IncomeViewSet(viewsets.ModelViewSet):
    queryset = Income.objects.all()
    serializer_class = IncomeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)


class ExpenseViewSet(viewsets.ModelViewSet):
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)


class BudgetViewSet(viewsets.ModelViewSet):
    queryset = Budget.objects.all()
    serializer_class = BudgetSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)


class TransactionListCreateAPIView(generics.ListCreateAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        data = request.data.copy()
        data['user'] = request.user.id

        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            serializer.save()
            income_total = Transaction.objects.filter(user=request.user, type='income').aggregate(total=Sum('amount'))['total'] or 0
            expense_total = Transaction.objects.filter(user=request.user, type='expense').aggregate(total=Sum('amount'))['total'] or 0

            return Response({
                "message": "Transaction added successfully!",
                "data": serializer.data,
                "income_total": income_total,
                "expense_total": expense_total
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TransactionListAPIView(generics.ListAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def get_transactions(request):
    transactions = Transaction.objects.filter(user=request.user).order_by("date")
    serializer = TransactionSerializer(transactions, many=True)
    return Response(serializer.data)


class TransactionUpdateView(generics.UpdateAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        data = request.data.copy()
        data["user"] = request.user.id

        serializer = self.get_serializer(instance, data=data, partial=partial)
        if serializer.is_valid():
            self.perform_update(serializer)
            return Response({
                "message": "Transaction updated successfully!",
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        return Response({"message": "Update failed", "errors": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)


class TransactionDeleteView(DestroyAPIView):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    def perform_destroy(self, instance):
        if instance.user != self.request.user:
            raise PermissionDenied("You do not have permission to delete this transaction.")
        instance.delete()


def get_csrf_token(request):
    return JsonResponse({"csrfToken": get_token(request)})


def index(request):
    contact_form = ContactForm()

    if request.method == "POST":
        contact_form = ContactForm(request.POST)
        if contact_form.is_valid():
            name = contact_form.cleaned_data['name']
            email = contact_form.cleaned_data['email']
            message = contact_form.cleaned_data['message']

            full_message = f"From: {name} <{email}>\n\nMessage:\n{message}"

            email_message = EmailMessage(
                subject="Contact Form Submission - Financial Tracker",
                body=full_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[settings.CONTACT_RECEIVER_EMAIL],
                headers={'Reply-To': email}
            )
            email_message.send(fail_silently=False)

            messages.success(request, "Your message has been sent successfully!")
            return redirect("index")

    return render(request, 'index.html', {'form': contact_form})


def login_page(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "Login successful! Redirecting to dashboard...")
            return redirect("dashboard")
        else:
            messages.error(request, "Invalid username or password. Please try again.")
    return render(request, "login.html")


def register(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data["password"])
            user.save()
            login(request, user)
            messages.success(request, "Registration successful! Redirecting to dashboard...")
            return redirect("dashboard")
    else:
        form = RegisterForm()

    return render(request, "register.html", {"form": form})


def logout_user(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect("index")


@login_required
def dashboard(request):
    user = request.user

    # Category-wise expense summary
    category_data = (
        Transaction.objects
        .filter(user=user, type='expense')
        .values('category')
        .annotate(total=Sum('amount'))
        .order_by('-total')
    )

    categories = [entry['category'] for entry in category_data]
    category_totals = [float(entry['total']) for entry in category_data]

    # Monthly expense summary
    monthly_data = (
        Transaction.objects
        .filter(user=user, type='expense')
        .annotate(month=TruncMonth('created_at'))
        .values('month')
        .annotate(total=Sum('amount'))
        .order_by('month')
    )

    months = [calendar.month_name[entry['month'].month] for entry in monthly_data]
    monthly_totals = [float(entry['total']) for entry in monthly_data]

    context = {
        'category_labels': json.dumps(categories),
        'category_totals': json.dumps(category_totals),
        'month_labels': json.dumps(months),
        'month_totals': json.dumps(monthly_totals),
    }

    return render(request, 'dashboard.html', context)


@login_required
def income_view(request):
    user = request.user
    incomes = Transaction.objects.filter(user=user, type='income').order_by('created_at')

    chart_data = {
        "labels": [income.created_at.strftime("%Y-%m-%d") for income in incomes],
        "amounts": [float(income.amount) for income in incomes]
    }

    income_sources = [
        {
            "date": income.created_at.strftime("%Y-%m-%d"),
            "source": income.category,
            "amount": float(income.amount)
        } for income in incomes
    ]

    context = {
        "chart_data": json.dumps(chart_data, cls=DjangoJSONEncoder),
        "income_sources": json.dumps(income_sources, cls=DjangoJSONEncoder),
    }
    return render(request, "income.html", context)


@login_required
def expense_view(request):
    user = request.user
    expenses = Transaction.objects.filter(user=user, type='expense').order_by('created_at')

    labels = [DateFormat(exp.created_at).format('M d') for exp in expenses]
    amounts = [float(exp.amount) for exp in expenses]

    chart_data = {
        'labels': labels,
        'amounts': amounts,
    }

    sources = [
        {
            'date': DateFormat(exp.created_at).format('Y-m-d'),
            'category': exp.category,
            'amount': float(exp.amount)
        } for exp in expenses
    ]

    return render(request, 'expense.html', {
        'chart_data': json.dumps(chart_data),
        'sources': json.dumps(sources),
    })


# --- Your requested CSV and PDF export views ---

@login_required
def export_transactions_csv(request):
    user = request.user
    transactions = Transaction.objects.filter(user=user).order_by('-created_at')

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="transactions.csv"'

    writer = csv.writer(response)
    writer.writerow(['Type', 'Category', 'Amount', 'Date'])

    for t in transactions:
        writer.writerow([t.type, t.category, float(t.amount), t.created_at.strftime('%Y-%m-%d')])

    return response


@login_required
def export_transactions_pdf(request):
    user = request.user
    transactions = Transaction.objects.filter(user=user).order_by('-created_at')

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="transactions.pdf"'

    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    y = height - 40

    p.setFont("Helvetica-Bold", 16)
    p.drawString(30, y, "Transaction History")
    y -= 30

    p.setFont("Helvetica-Bold", 12)
    p.drawString(30, y, "Type")
    p.drawString(100, y, "Category")
    p.drawString(250, y, "Amount")
    p.drawString(350, y, "Date")
    y -= 20

    p.setFont("Helvetica", 12)
    for t in transactions:
        if y < 40:
            p.showPage()
            y = height - 40
            p.setFont("Helvetica-Bold", 12)
            p.drawString(30, y, "Type")
            p.drawString(100, y, "Category")
            p.drawString(250, y, "Amount")
            p.drawString(350, y, "Date")
            y -= 20
            p.setFont("Helvetica", 12)

        p.drawString(30, y, t.type)
        p.drawString(100, y, t.category)
        p.drawString(250, y, f"{float(t.amount):.2f}")
        p.drawString(350, y, t.created_at.strftime('%Y-%m-%d'))
        y -= 20

    p.save()
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response


@login_required
def export_income_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="income.csv"'

    writer = csv.writer(response)
    writer.writerow(['Date', 'Source', 'Amount'])

    incomes = Transaction.objects.filter(user=request.user, type='income').order_by('-created_at')
    for income in incomes:
        writer.writerow([income.created_at.strftime('%Y-%m-%d'), income.category, float(income.amount)])

    return response


@login_required
def export_income_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="income.pdf"'

    p = canvas.Canvas(response)
    p.setFont("Helvetica-Bold", 14)
    p.drawString(100, 800, "Income Sources Report")

    y = 770
    p.setFont("Helvetica", 12)
    p.drawString(50, y, "Date")
    p.drawString(200, y, "Source")
    p.drawString(400, y, "Amount")

    incomes = Transaction.objects.filter(user=request.user, type='income').order_by('-created_at')
    for income in incomes:
        y -= 20
        if y < 50:  # go to new page if space runs out
            p.showPage()
            p.setFont("Helvetica", 12)
            y = 800
        p.drawString(50, y, income.created_at.strftime('%Y-%m-%d'))
        p.drawString(200, y, income.category)
        p.drawString(400, y, f"₹ {income.amount}")

    p.showPage()
    p.save()
    return response


@login_required
def export_expense_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="expenses.csv"'

    writer = csv.writer(response)
    writer.writerow(['Date', 'Category', 'Amount'])

    expenses = Transaction.objects.filter(user=request.user, type='expense').order_by('-created_at')
    for expense in expenses:
        writer.writerow([expense.created_at, expense.category, expense.amount])

    return response


@login_required
def export_expense_pdf(request):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="expenses.pdf"'

    p = canvas.Canvas(response)
    p.setFont("Helvetica-Bold", 14)
    p.drawString(200, 800, "Expense Report")

    y = 770
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, y, "Date")
    p.drawString(200, y, "Category")
    p.drawString(400, y, "Amount")

    p.setFont("Helvetica", 12)
    expenses = Transaction.objects.filter(user=request.user, type='expense').order_by('-created_at')
    for expense in expenses:
        y -= 20
        if y < 50:
            p.showPage()
            y = 800
        p.drawString(50, y,  expense.created_at.strftime('%Y-%m-%d'))
        p.drawString(200, y, expense.category)
        p.drawString(400, y, f"₹ {expense.amount}")

    p.showPage()
    p.save()
    return response






