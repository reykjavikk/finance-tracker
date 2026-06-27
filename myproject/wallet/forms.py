from django import forms
from .models import Transaction, Category
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['amount', 'category', 'description']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)

        super().__init__(*args, **kwargs)

        if user:
            self.fields['category'].queryset = Category.objects.filter(user=user)

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount <= 0:
            raise forms.ValidationError('Сумма транзакции должна быть больше 0')

        return amount



class MyUserRegisterForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = get_user_model()


