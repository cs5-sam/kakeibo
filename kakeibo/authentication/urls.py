from .views import CompletePasswordReset, ResetPassword, LogoutView, LoginView, VerificationView, RegistrationView, UsernameValidationView, EmailValidationView
from django.urls import path
from django.views.decorators.csrf import csrf_exempt, csrf_protect

urlpatterns = [
    path('logout',LogoutView.as_view(),name="logout"),
    path('login',LoginView.as_view(),name="login"),
    path('register',RegistrationView.as_view(),name="register"),
    path('validate-username',csrf_exempt(UsernameValidationView.as_view()),name="validate-username"),
    path('validate-email',csrf_exempt(EmailValidationView.as_view()),name="validate-email"),
    path('activate/<uidb64>/<token>', VerificationView.as_view(),name="activate"),
    path('set-new-password/<uidb64>/<token>', CompletePasswordReset.as_view(),name="reset-user-password"),
    path('request-reset-link',ResetPassword.as_view(),name="reset-password")
]
