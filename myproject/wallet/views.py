from django.shortcuts import render, redirect
from .models import Transaction, Category
from .forms import TransactionForm, MyUserRegisterForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.db.models import Sum, DecimalField
from django.db.models.functions import Coalesce

base_categories = (
    ('Зарплата', 'IN'),
    ('Фриланс', 'IN'),
    ('Продукты', 'OUT'),
    ('Одежда', 'OUT'),
)

@login_required
def index(request):
    if request.method == 'POST':
        form = TransactionForm(request.POST, user=request.user)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.user = request.user
            transaction.save()
            return redirect('wallet:index')
    else:
        form = TransactionForm(user = request.user)



    transactions = Transaction.objects.for_user(request.user).order_by('-creation')
    sum_of_income = Transaction.objects.for_user(request.user).income().get_total_amount()
    sum_of_outcome = Transaction.objects.for_user(request.user).outcome().get_total_amount()
    balance = sum_of_income - sum_of_outcome
    categories_stats = Category.objects.for_user(request.user).outcome().group_categories()

    context = {'transactions': transactions,
                'form': form,
               'income': sum_of_income,
               'outcome': sum_of_outcome,
               'balance': balance,
               'categories': categories_stats
               }
    return render(request, 'wallet/index.html', context)


def register(request):
    if request.method == 'POST':
        form = MyUserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            for name, cat_id in base_categories:
                Category.objects.create(name=name, type=cat_id, user=user)
            login(request, user)
            return redirect('wallet:index')
    else:
        form = MyUserRegisterForm()

    return render(request, 'wallet/register.html', context={'form': form})


