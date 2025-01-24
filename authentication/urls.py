from django.urls import path, include
from .views import CustomTokenObtainPairView, change_password
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('auth/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('auth/change_password/', change_password, name='change_password'),
    path('auth/password_reset/', include('django_rest_passwordreset.urls', namespace='password_reset'))
]