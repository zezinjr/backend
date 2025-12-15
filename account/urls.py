from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from account import viewsets
from account.viewsets import MyTokenObtainPairView

routers = DefaultRouter()

routers.register('menu', viewsets.MenuViewSet)
routers.register('user', viewsets.UserViewSet)
routers.register('group', viewsets.GroupViewSet, basename='group')
routers.register('user_group', viewsets.AccountGroupViewSet)
routers.register('permission', viewsets.PermissionViewSet)
routers.register('content_type', viewsets.ContentTypeViewSet)
routers.register('module', viewsets.ModuleViewSet)
routers.register('module_menu', viewsets.ModuleMenuViewSet)

urlpatterns = [
    path('token/', MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

urlpatterns += routers.urls
