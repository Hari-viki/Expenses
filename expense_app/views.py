import calendar
from datetime import datetime

from django.contrib import messages
from django.contrib.auth import (
    authenticate,
    login,
    logout
)
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Sum
from django.db.models.functions import TruncDate
from django.http import JsonResponse
from django.shortcuts import (
    redirect,
    render
)
from django.utils import timezone

from .models import *

def signup_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email    = request.POST.get('email')
        password = request.POST.get('password')
        if CustomUser.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect('signup')
        user = CustomUser.objects.create_user(
            username=username,
            email=email,
            password=password
        )
        if request.FILES.get('profile_picture'):
            user.profile_picture = request.FILES['profile_picture']
            user.save()
        login(request, user) 
        messages.success(request, "Account created successfully")
        return redirect('home')
    return render(request, 'web/signup.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Invalid credentials")
    return render(request, 'web/login.html')

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required(login_url='login')
def home_view(request):

    today = timezone.now()
    month = today.month
    year = today.year

    exp_qs = (
        ExpensesList.objects
        .filter(user=request.user, date__month=month, date__year=year, amount__gt=0)
        .values('date')
        .annotate(total=Sum('amount'))
        .order_by('date')
    )

    labels = [e['date'].strftime("%d %b") for e in exp_qs]
    expense_data = [int(e['total']) for e in exp_qs]

    inc_qs = (
        ExpensesList.objects
        .filter(user=request.user, date__month=month, date__year=year, extra_amount__gt=0)
        .values('date')
        .annotate(total=Sum('extra_amount'))
        .order_by('date')
    )

    income_map = {e['date'].strftime("%d %b"): int(e['total']) for e in inc_qs}
    income_data = [income_map.get(label, 0) for label in labels]

    pie_exp = (
        ExpensesList.objects
        .filter(user=request.user, amount__gt=0)
        .values('description')
        .annotate(total=Sum('amount'))
    )

    pie_exp_labels = [e['description'] for e in pie_exp]
    pie_exp_values = [int(e['total']) for e in pie_exp]

    pie_inc = (
        ExpensesList.objects
        .filter( user=request.user, extra_amount__gt=0)
        .values('description')
        .annotate(total=Sum('extra_amount'))
    )

    pie_inc_labels = [e['description'] for e in pie_inc]
    pie_inc_values = [int(e['total']) for e in pie_inc]
    total_expense = (
        ExpensesList.objects
        .filter(user=request.user, amount__gt=0)
        .aggregate(total=Sum('amount'))['total'] or 0
    )
    total_income = (
        ExpensesList.objects
        .filter(user=request.user, extra_amount__gt=0)
        .aggregate(total=Sum('extra_amount')
        )['total'] or 0
    )
    current_balance = total_income - total_expense
    return render(request, 'web/home.html', {
        'labels': labels,
        'expense_data': expense_data,
        'income_data': income_data,
        'pie_exp_labels': pie_exp_labels,
        'pie_exp_values': pie_exp_values,
        'pie_inc_labels': pie_inc_labels,
        'pie_inc_values': pie_inc_values,
        'total_expense': total_expense,
        'total_income': total_income,
        'current_balance': current_balance,
        'month_name': today.strftime("%B"),
    })

@login_required(login_url='login')
def expenses_view(request):
    months = [(i, calendar.month_abbr[i]) for i in range(1, 13)]
    month = request.GET.get('month')
    search = request.GET.get('search')
    selected_bank = request.GET.get('bank')
    expenses = ExpensesList.objects.filter(
        user=request.user
    )
    if month:
        expenses = expenses.filter(
            date__month=month
        )
    if search:
        expenses = expenses.filter(
            description__icontains=search
        )
    if selected_bank:
        expenses = expenses.filter(
            bank__iexact=selected_bank.strip()
        )
    expenses = expenses.order_by('-id')
    total = expenses.aggregate(
        total=Sum('amount')
    )['total'] or 0
    bank_selection = Bank.objects.all()
    banks = (
        ExpensesList.objects
        .filter(user=request.user)
        .values_list('bank', flat=True)
        .distinct()
    )
    today = datetime.now().day
    is_first_week = today <= 7
    paginator = Paginator(expenses, 10)
    page_number = request.GET.get('page')
    expenses = paginator.get_page(page_number)
    if request.method == 'POST':
        try:
            amount = int(request.POST.get('amount', 0))
            extra_amount = int(request.POST.get('extra_amount', 0))
            if amount < 0:
                return JsonResponse({
                    'error': 'Expense amount cannot be negative'
                }, status=400)
            if extra_amount < 0:
                return JsonResponse({
                    'error': 'Extra amount cannot be negative'
                }, status=400)
        except ValueError:
            return JsonResponse({
                'error': 'Invalid amount'
            }, status=400)
        description = request.POST.get('description', '').strip()
        bank_name = request.POST.get(
            'bank',
            ''
        ).strip().upper()
        entered_total = request.POST.get('total_amount')
        entered_total = (
            int(entered_total)
            if entered_total and entered_total.strip()
            else None
        )
        current_month = timezone.now().month
        current_year = timezone.now().year

        last = ExpensesList.objects.filter(
            user=request.user,
            bank__iexact=bank_name,
            date__month=current_month,
            date__year=current_year
        ).order_by('-id').first()

        if not last:
            print("Iffff")
            if entered_total is None:
                return JsonResponse({
                    'error': 'Total amount required for first entry'
                }, status=400)
            old_balance = int(last.balance_amount)
            total_amount = entered_total
            balance = (old_balance + extra_amount - amount)

        else:
            if entered_total is not None and entered_total > 0 and amount == 0:
                old_balance = int(last.balance_amount)
                total_amount = entered_total
                balance = (old_balance + extra_amount - amount)
            else:
                old_total = int(last.total_amount)
                old_balance = int(last.balance_amount)
                total_amount = old_total
                balance = (old_balance + extra_amount - amount)

        exp = ExpensesList.objects.create(
            user=request.user,
            bank=bank_name,
            amount=amount,
            extra_amount=extra_amount,
            total_amount=total_amount,
            balance_amount=balance,
            description=description,
            date=timezone.now()
        )

        new_total = ExpensesList.objects.filter(
            user=request.user
        ).aggregate(
            total=Sum('amount')
        )['total'] or 0

        return JsonResponse({
            'date': exp.date.strftime("%b %d, %Y"),
            'total_amount': exp.total_amount,
            'amount': exp.amount,
            'extra_amount': exp.extra_amount,
            'balance': exp.balance_amount,
            'description': exp.description,
            'bank': exp.bank,
            'total_spent': new_total
        })

    return render(request, 'web/expenses.html', {
        'expenses': expenses,
        'months': months,
        'total_spent': total,
        'is_first_week': is_first_week,
        'banks': banks,
        'bank_selection': bank_selection,
        'selected_bank': selected_bank
    })

@login_required
def get_bank_total(request):
    bank = request.GET.get('bank', '').strip()
    last = ExpensesList.objects.filter(
        user=request.user,
        bank__iexact=bank
    ).order_by('-id').first()
    total_amount = 0
    current_balance = 0
    if last:
        total_amount = last.total_amount
        current_balance = last.balance_amount
    return JsonResponse({
        'total': total_amount,
        'balance': current_balance
    })

@login_required(login_url='login')
def bike_expenses_view(request):
    return render(request, 'web/bike_expenses.html')

@login_required(login_url='login')
def expense_report(request):
    expenses = ExpensesList.objects.filter(user=request.user)

    # Get all banks for dropdown
    banks = (
        ExpensesList.objects
        .filter(user=request.user)
        .values_list('bank', flat=True)
        .distinct()
        .order_by('bank')
    )

    # Filters
    from_date    = request.GET.get('from_date')
    to_date      = request.GET.get('to_date')
    selected_bank = request.GET.get('bank')

    if from_date:
        expenses = expenses.filter(date__gte=from_date)
    if to_date:
        expenses = expenses.filter(date__lte=to_date)
    if selected_bank:
        expenses = expenses.filter(bank__iexact=selected_bank.strip())

    expenses = expenses.order_by('-date', '-id')

    # Totals
    from django.db.models import Sum
    totals = expenses.aggregate(
        total_spent   = Sum('amount'),
        total_extra   = Sum('extra_amount'),
    )
    total_spent = totals['total_spent'] or 0
    total_extra = totals['total_extra'] or 0

    return render(request, 'web/report.html', {
        'expenses':      expenses,
        'banks':         banks,
        'from_date':     from_date or '',
        'to_date':       to_date   or '',
        'selected_bank': selected_bank or '',
        'total_spent':   total_spent,
        'total_extra':   total_extra,
        'total_count':   expenses.count(),
    })