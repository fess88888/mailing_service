from django.urls import path
from .views import (
    UserLoginView,
    UserRegisterView,
    EmailVerifyView,
    RegistrationConfirmWaitView,
    UserProfileView,
    UserPasswordResetView,
    UserPasswordResetConfirmView,
    PasswordResetDoneView,
    PasswordResetCompleteView,
    user_list_view,
    toggle_user_block,
)

app_name = "users"

urlpatterns = [
    path("login/", UserLoginView.as_view(), name="login"),
    path("logout/", UserLoginView.as_view(), name="logout"),
    path("register/", UserRegisterView.as_view(), name="register"),
    path("profile/", UserProfileView.as_view(), name="profile"),
    path("verify-email/<uuid:token>/", EmailVerifyView.as_view(), name="verify_email"),
    path("registration-confirm/", RegistrationConfirmWaitView.as_view(), name="registration_confirm_wait"),
    path("password-reset/", UserPasswordResetView.as_view(), name="password_reset"),
    path("password-reset/done/", PasswordResetDoneView.as_view(), name="password_reset_done"),
    path("password-reset/confirm/<uidb64>/<token>/", UserPasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    path("password-reset/complete/", PasswordResetCompleteView.as_view(), name="password_reset_complete"),
    path("users-list/", user_list_view, name="user_list"),
    path("users/<int:pk>/toggle-block/", toggle_user_block, name="toggle_user_block"),
]
