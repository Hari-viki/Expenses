from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.db.models.functions import TruncDate
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Sum
from .models import *
from datetime import datetime
import calendar
import json

def signup_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        if CustomUser.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect('signup')
        user = CustomUser.objects.create_user(
            username=username,
            email=email,
            password=password
        )
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

    # =============================
    # 🔴 EXPENSE (amount > 0)
    # =============================
    exp_qs = (
        ExpensesList.objects
        .filter(user=request.user, date__month=month, date__year=year, amount__gt=0)
        .values('date')
        .annotate(total=Sum('amount'))
        .order_by('date')
    )

    labels = [e['date'].strftime("%d %b") for e in exp_qs]
    expense_data = [int(e['total']) for e in exp_qs]

    # =============================
    # 🟢 INCOME (amount = 0)
    # =============================
    inc_qs = (
        ExpensesList.objects
        .filter(user=request.user, date__month=month, date__year=year, amount=0)
        .values('date')
        .annotate(total=Sum('balance_amount'))
        .order_by('date')
    )

    income_map = {e['date'].strftime("%d %b"): int(e['total']) for e in inc_qs}
    income_data = [income_map.get(label, 0) for label in labels]

    # =============================
    # 🥧 EXPENSE PIE
    # =============================
    pie_exp = (
        ExpensesList.objects
        .filter(user=request.user, amount__gt=0)
        .values('description')
        .annotate(total=Sum('amount'))
    )

    pie_exp_labels = [e['description'] for e in pie_exp]
    pie_exp_values = [int(e['total']) for e in pie_exp]

    # =============================
    # 🥧 INCOME PIE
    # =============================
    pie_inc = (
        ExpensesList.objects
        .filter(user=request.user, amount=0)
        .values('description')
        .annotate(total=Sum('balance_amount'))
    )

    pie_inc_labels = [e['description'] for e in pie_inc]
    pie_inc_values = [int(e['total']) for e in pie_inc]

    return render(request, 'web/home.html', {
        'labels': labels,
        'expense_data': expense_data,
        'income_data': income_data,
        'pie_exp_labels': pie_exp_labels,
        'pie_exp_values': pie_exp_values,
        'pie_inc_labels': pie_inc_labels,
        'pie_inc_values': pie_inc_values,
        'month_name': today.strftime("%B"),
    })

@login_required(login_url='login')
def expenses_view(request):

    months = [(i, calendar.month_abbr[i]) for i in range(1, 13)]

    month = request.GET.get('month')
    search = request.GET.get('search')
    selected_bank = request.GET.get('bank')

    expenses = ExpensesList.objects.filter(user=request.user)

    # 🔹 FILTERS
    if month:
        expenses = expenses.filter(date__month=month)

    if search:
        expenses = expenses.filter(description__icontains=search)

    if selected_bank:
        expenses = expenses.filter(bank__iexact=selected_bank.strip())

    expenses = expenses.order_by('-id')

    total = expenses.aggregate(total=Sum('amount'))['total'] or 0
    bank_selection = Bank.objects.all()
    banks = (
        ExpensesList.objects
        .filter(user=request.user)
        .values_list('bank', flat=True)
        .distinct()
    )

    today = datetime.now().day
    is_first_week = today <= 7

    if request.method == 'POST':
        amount = int(request.POST.get('amount'))
        description = request.POST.get('description')
        bank_name = request.POST.get('bank').strip().upper()
        entered_total = request.POST.get('total_amount')
        entered_total = int(entered_total) if entered_total and entered_total.strip() else None

        current_month = timezone.now().month
        current_year = timezone.now().year

        # ✅ BANK-WISE LAST RECORD
        last = ExpensesList.objects.filter(
            user=request.user,
            bank__iexact=bank_name,
            date__month=current_month,
            date__year=current_year
        ).order_by('-id').first()

        if last:
            total_amount = entered_total if entered_total is not None else int(last.total_amount)

            # Use previous balance
            previous_balance = int(last.balance_amount)
            balance = previous_balance - amount

        else:
            if entered_total is None:
                return JsonResponse({'error': 'Total required'}, status=400)

            total_amount = entered_total

            # First entry
            balance = total_amount - amount

        exp = ExpensesList.objects.create(
            user=request.user,
            bank=bank_name,
            amount=amount,
            total_amount=total_amount,
            balance_amount=balance,
            description=description,
            date=timezone.now()
        )

        new_total = ExpensesList.objects.filter(user=request.user).aggregate(
            total=Sum('amount')
        )['total'] or 0

        return JsonResponse({
            'date': exp.date.strftime("%b %d, %Y"),
            'total_amount': exp.total_amount,
            'amount': exp.amount,
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
    bank = request.GET.get('bank')

    last = ExpensesList.objects.filter(
        user=request.user,
        bank__iexact=bank
    ).order_by('-id').first()

    return JsonResponse({
        'total': last.total_amount if last else ''
    })

@login_required(login_url='login')
def bike_expenses_view(request):
    return render(request, 'web/bike_expenses.html')