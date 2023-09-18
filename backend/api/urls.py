from django.urls import path
from rest_framework_simplejwt import views as jwt_views

from .views import ImageAPIView

urlpatterns = [
    path("images/", ImageAPIView.as_view(), name="images_api"),
    path("token/", jwt_views.TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", jwt_views.TokenRefreshView.as_view(), name="token_refresh"),
]
