from django.urls import path
from .views import UploadViewSet
from rest_framework_simplejwt import views as jwt_views

urlpatterns = [
    path('images/', UploadViewSet.as_view(), name='images'),
    path('token/', jwt_views.TokenObtainPairView.as_view(),
         name='token_obtain_pair'),
    path('token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
]