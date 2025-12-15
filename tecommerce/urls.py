from django.contrib import admin
from django.shortcuts import redirect
from django.urls import path, include, reverse
from rest_framework_simplejwt.views import TokenRefreshView

from account.viewsets import MyTokenObtainPairView

urlpatterns = [
    path('api/', lambda request: redirect(reverse('api-root'))),
    path('admin/', admin.site.urls),
    path('api-auth/', include('rest_framework.urls')),
    path('api/core/', include('core.urls'), name='api-root'),
    path('api/account/', include('account.urls')),
    path('auth/token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
