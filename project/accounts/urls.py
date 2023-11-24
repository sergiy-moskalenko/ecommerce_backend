from django.urls import path

from accounts import views

urlpatterns = [
    path('register', views.RegisterView.as_view()),
    path('login', views.LoginView.as_view()),
    path('logout', views.LogoutView.as_view()),
    path('confirm-email', views.ConfirmEmailView.as_view()),
    path('password-recovery', views.PasswordRecoveryView.as_view()),
    path('set-password', views.SetNewPasswordView.as_view()),
    path('change-password', views.ChangePasswordView.as_view()),
]
