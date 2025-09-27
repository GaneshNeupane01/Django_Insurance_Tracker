
from django.urls import path
from users.views import ProfileView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from users.views import FacebookLoginView # Added this import
from users.views import GoogleLoginView

urlpatterns = [
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),

    path("api/facebook-login/", FacebookLoginView.as_view(), name="facebook_login"),
    path("api/profile/", ProfileView.as_view(), name="profile"),
    path("api/google-login/", GoogleLoginView.as_view(), name="google_login"),
]
