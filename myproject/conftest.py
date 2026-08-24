import pytest

from django.contrib.auth import get_user_model

from wallet.models import Category, Transaction


@pytest.fixture
def user(db):
    return get_user_model().objects.create_user(username='testuser', password='Test12345!')


@pytest.fixture
def auth_client(client, user):
    client.force_login(user)
    return client


@pytest.fixture
def income_category(user, db):
    return Category.objects.create(name='Зарплата', type='IN', user=user)


@pytest.fixture
def outcome_category(user, db):
    return Category.objects.create(name='Продукты', type='OUT', user=user)


@pytest.fixture
def transaction(user, outcome_category, db):
    return Transaction.objects.create(amount=100.50, category=outcome_category, user=user, description='Покупка')
