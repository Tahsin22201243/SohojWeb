# invest/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # home page
    path('register/', views.register, name='register'),  # register page
    path('login/', views.user_login, name='login'),      # login page
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    path('profile/balance/', views.balance_view, name='profile_balance'),
    path('profile/bank/', views.bank_view, name='profile_bank'),
    path('profile/change-password/', views.change_password_view, name='profile_change_password'),
    path('profile/<int:user_id>/kyc/download/', views.download_kyc, name='download_kyc'),
    path('investment/<int:investment_id>/receipt/', views.download_receipt, name='download_receipt'),
    path('update/<int:update_id>/edit/', views.edit_update, name='edit_update'),
    path('update/<int:update_id>/delete/', views.delete_update, name='delete_update'),
    # add more routes as needed
]
