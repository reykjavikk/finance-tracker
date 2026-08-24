from django.urls import path
from . import views
from django.contrib.auth.views import LoginView, LogoutView

app_name = 'wallet'

urlpatterns = [
    path('', views.index, name = 'index'),
    path('login/', LoginView.as_view(template_name = 'wallet/login.html'), name = 'login'),
    path('logout/', LogoutView.as_view(), name = 'logout'),
    path('register/', views.register, name = 'register'),
    path('categories/', views.categories, name = 'categories'),
    path('transactions/<int:pk>/update/', views.transaction_update, name = 'transaction_update'),
    path('transactions/<int:pk>/delete/', views.transaction_delete, name = 'transaction_delete'),
    path('categories/<int:pk>/update/', views.category_update, name = 'category_update'),
    path('categories/<int:pk>/delete/', views.category_delete, name = 'category_delete')
]

