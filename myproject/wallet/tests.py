import pytest
from decimal import Decimal

from django.urls import reverse

from django.contrib.auth import get_user_model

from .models import Category, Transaction
from .forms import TransactionForm, CategoryForm


# Модели и QuerySet

@pytest.mark.django_db
def test_category_str(outcome_category):
    assert str(outcome_category) == 'Продукты:Расход'


@pytest.mark.django_db
def test_transaction_str(transaction):
    text = str(transaction)
    assert transaction.user.username in text
    assert str(transaction.amount) in text


@pytest.mark.django_db
def test_queryset_for_user(user, transaction):
    other_user = get_user_model().objects.create_user(username='other', password='Test12345!')
    other_category = Category.objects.create(name='Такси', type='OUT', user=other_user)
    other_transaction = Transaction.objects.create(amount=10, category=other_category, user=other_user)

    qs = Transaction.objects.for_user(user)
    assert transaction in qs
    assert other_transaction not in qs


@pytest.mark.django_db
def test_income_and_outcome(user, income_category, outcome_category):
    Transaction.objects.create(amount=1000, category=income_category, user=user)
    Transaction.objects.create(amount=300, category=outcome_category, user=user)

    assert Transaction.objects.for_user(user).income().count() == 1
    assert Transaction.objects.for_user(user).outcome().count() == 1


@pytest.mark.django_db
def test_get_total_amount(user, outcome_category):
    Transaction.objects.create(amount=100, category=outcome_category, user=user)
    Transaction.objects.create(amount=50.25, category=outcome_category, user=user)

    total = Transaction.objects.for_user(user).outcome().get_total_amount()
    assert total == Decimal('150.25')


@pytest.mark.django_db
def test_group_categories(user, outcome_category):
    Transaction.objects.create(amount=100, category=outcome_category, user=user)
    Transaction.objects.create(amount=40, category=outcome_category, user=user)

    stats = Category.objects.for_user(user).outcome().group_categories()
    assert stats[0].total_spent == Decimal('140.00')


# Формы

@pytest.mark.django_db
def test_transaction_form_rejects_zero(user, outcome_category):
    form = TransactionForm(data={'amount': 0, 'category': outcome_category.pk}, user=user)
    assert not form.is_valid()


@pytest.mark.django_db
def test_transaction_form_valid(user, outcome_category):
    form = TransactionForm(data={'amount': 99.99, 'category': outcome_category.pk, 'description': ''}, user=user)
    assert form.is_valid()


@pytest.mark.django_db
def test_category_form_valid():
    form = CategoryForm(data={'name': 'Кино', 'type': 'OUT'})
    assert form.is_valid()


# Представления

def test_index_requires_login(client):
    response = client.get(reverse('wallet:index'))
    assert response.status_code == 302
    assert reverse('wallet:login') in response.url


@pytest.mark.django_db
def test_index_shows_transactions(auth_client, transaction):
    response = auth_client.get(reverse('wallet:index'))
    assert response.status_code == 200
    assert transaction.category.name in response.content.decode()


@pytest.mark.django_db
def test_register_creates_base_categories(client, db):
    response = client.post(reverse('wallet:register'), {
        'username': 'newuser',
        'password1': 'Test12345!',
        'password2': 'Test12345!',
    })
    assert response.status_code == 302
    user = get_user_model().objects.get(username='newuser')
    assert Category.objects.filter(user=user).count() == 4


@pytest.mark.django_db
def test_transaction_create(auth_client, outcome_category, user):
    response = auth_client.post(reverse('wallet:index'), {
        'amount': '250.75',
        'category': outcome_category.pk,
        'description': 'Тестовая покупка',
    })
    assert response.status_code == 302
    assert Transaction.objects.filter(user=user).count() == 1


@pytest.mark.django_db
def test_transaction_update(auth_client, transaction):
    response = auth_client.post(reverse('wallet:transaction_update', args=[transaction.pk]), {
        'amount': '999.99',
        'category': transaction.category.pk,
        'description': transaction.description,
    })
    assert response.status_code == 302
    transaction.refresh_from_db()
    assert transaction.amount == Decimal('999.99')


@pytest.mark.django_db
def test_transaction_delete(auth_client, transaction):
    confirm_page = auth_client.get(reverse('wallet:transaction_delete', args=[transaction.pk]))
    assert confirm_page.status_code == 200

    response = auth_client.post(reverse('wallet:transaction_delete', args=[transaction.pk]))
    assert response.status_code == 302
    assert not Transaction.objects.filter(pk=transaction.pk).exists()


@pytest.mark.django_db
def test_categories_page(auth_client, outcome_category):
    response = auth_client.get(reverse('wallet:categories'))
    assert response.status_code == 200
    assert outcome_category.name in response.content.decode()


@pytest.mark.django_db
def test_category_create(auth_client, user):
    response = auth_client.post(reverse('wallet:categories'), {
        'name': 'Кино',
        'type': 'OUT',
    })
    assert response.status_code == 302
    assert Category.objects.filter(name='Кино', user=user).exists()


@pytest.mark.django_db
def test_category_update(auth_client, outcome_category):
    response = auth_client.post(reverse('wallet:category_update', args=[outcome_category.pk]), {
        'name': 'Супермаркет',
        'type': 'OUT',
    })
    assert response.status_code == 302
    outcome_category.refresh_from_db()
    assert outcome_category.name == 'Супермаркет'


@pytest.mark.django_db
def test_category_delete_removes_transactions(auth_client, transaction, outcome_category):
    response = auth_client.post(reverse('wallet:category_delete', args=[outcome_category.pk]))
    assert response.status_code == 302
    assert not Category.objects.filter(pk=outcome_category.pk).exists()
    assert not Transaction.objects.filter(pk=transaction.pk).exists()


# Чужие данные трогать нельзя

@pytest.mark.django_db
def test_cannot_edit_others_transaction(client, db):
    owner = get_user_model().objects.create_user(username='owner', password='Test12345!')
    category = Category.objects.create(name='Продукты', type='OUT', user=owner)
    foreign_transaction = Transaction.objects.create(amount=500, category=category, user=owner)

    client.force_login(get_user_model().objects.create_user(username='intruder', password='Test12345!'))
    response = client.get(reverse('wallet:transaction_update', args=[foreign_transaction.pk]))
    assert response.status_code == 404
