from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models import Sum, DecimalField
from django.db.models.functions import Coalesce

class CategoryQuerySet(models.QuerySet):
    def for_user(self, user):
        return self.filter(user = user)

    def income(self):
        return self.filter(type = 'IN')

    def outcome(self):
        return self.filter(type = 'OUT')

    def group_categories(self):
        return self.annotate(total_spent = Coalesce(Sum('transactions__amount'), 0, output_field=DecimalField(max_digits=10, decimal_places=2)))

class TransactionQuerySet(models.QuerySet):
    def for_user(self, user):
        return self.filter(user = user)

    def income(self):
        return self.filter(category__type = 'IN')

    def outcome(self):
        return self.filter(category__type = 'OUT')

    def get_total_amount(self):
        return self.aggregate(total = Sum('amount'))['total'] or 0

class User(AbstractUser):  # 2 usages
    pass


class Category(models.Model):  # 7 usages
    objects = CategoryQuerySet.as_manager()
    class CategoryChoices(models.TextChoices):
        INCOME = "IN", "Доход"
        OUTCOME = "OUT", 'Расход'

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='categories')
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=3, choices=CategoryChoices.choices, default=CategoryChoices.INCOME)

    def __str__(self):
        # noinspection PyUnresolvedReferences
        return f"{self.name}:{self.get_type_display()}"


class Transaction(models.Model):  # 6 usages
    objects = TransactionQuerySet.as_manager()
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='transactions')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='transactions')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    creation = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        # noinspection PyUnresolvedReferences
        return f"{self.user}: category - {self.category.get_type_display()}, amount - {self.amount}"