from django.shortcuts import render, redirect, get_object_or_404
from .models import Transaction, Category
from .forms import TransactionForm, CategoryForm, MyUserRegisterForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.core.cache import cache
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
            cache.delete(f'category_stats_{request.user.id}')
            return redirect('wallet:index')
    else:
        form = TransactionForm(user = request.user)



    transactions = Transaction.objects.for_user(request.user).order_by('-creation')
    sum_of_income = Transaction.objects.for_user(request.user).income().get_total_amount()
    sum_of_outcome = Transaction.objects.for_user(request.user).outcome().get_total_amount()
    balance = sum_of_income - sum_of_outcome
    cache_key = f'category_stats_{request.user.id}'
    categories_stats = cache.get(cache_key)
    if categories_stats is None:
        categories_stats = Category.objects.for_user(request.user).outcome().group_categories()
        cache.set(cache_key, categories_stats, 60)

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


@login_required
def transaction_update(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk, user=request.user)
    if request.method == 'POST':
        form = TransactionForm(request.POST, instance=transaction, user=request.user)
        if form.is_valid():
            form.save()
            cache.delete(f'category_stats_{request.user.id}')
            return redirect('wallet:index')
    else:
        form = TransactionForm(instance=transaction, user=request.user)

    context = {'form': form, 'transaction': transaction}
    return render(request, 'wallet/transaction_form.html', context)


@login_required
def transaction_delete(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk, user=request.user)
    if request.method == 'POST':
        transaction.delete()
        cache.delete(f'category_stats_{request.user.id}')
        return redirect('wallet:index')
    context = {'transaction': transaction}
    return render(request, 'wallet/transaction_delete.html', context)


@login_required
def categories(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            category = form.save(commit=False)
            category.user = request.user
            category.save()
            cache.delete(f'category_stats_{request.user.id}')
            return redirect('wallet:categories')
    else:
        form = CategoryForm()

    categories_list = Category.objects.for_user(request.user).order_by('name')
    income_categories = categories_list.income()
    outcome_categories = categories_list.outcome()
    context = {'income_categories': income_categories,
                'outcome_categories': outcome_categories,
                'form': form
                }
    return render(request, 'wallet/categories.html', context)


@login_required
def category_update(request, pk):
    category = get_object_or_404(Category, pk=pk, user=request.user)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            cache.delete(f'category_stats_{request.user.id}')
            return redirect('wallet:categories')
    else:
        form = CategoryForm(instance=category)

    context = {'form': form, 'category': category}
    return render(request, 'wallet/category_form.html', context)


@login_required
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk, user=request.user)
    if request.method == 'POST':
        category.delete()
        cache.delete(f'category_stats_{request.user.id}')
        return redirect('wallet:categories')
    context = {'category': category}
    return render(request, 'wallet/category_delete.html', context)


