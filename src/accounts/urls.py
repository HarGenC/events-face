from django.urls import path

from .views import CustomTokenRefreshView, LoginView, LogoutView, RegisterView

urlpatterns = [
    path("register", RegisterView.as_view(), name="auth-register"),
    path("login", LoginView.as_view(), name="auth-login"),
    path("token/refresh", CustomTokenRefreshView.as_view(), name="token_refresh"),
    path("logout", LogoutView.as_view(), name="auth-logout"),
]
