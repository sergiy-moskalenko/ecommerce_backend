from django.urls import path

from accounts import views

urlpatterns = [
    path('register', views.RegisterView.as_view()),
    path('login', views.LoginView.as_view()),
    path('logout', views.LogoutView.as_view()),
    path('email-verify', views.VerifyEmailView.as_view()),
    path('password-reset', views.PasswordResetEmailView.as_view()),
    path('password-reset-done', views.PasswordResetDoneView.as_view()),
    path('change-password/<int:pk>', views.ChangePasswordView.as_view()),
]
