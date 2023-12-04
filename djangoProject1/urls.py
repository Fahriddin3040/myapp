from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView, TokenBlacklistView
from bc import urls, views
from drf_spectacular.views import SpectacularSwaggerView, SpectacularAPIView, SpectacularRedocView


urlpatterns = [
    path('api/v1/doc/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/v1/doc/swagger/', SpectacularSwaggerView.as_view(), name='swagger'),
    path('api/v1/doc/redoc/', SpectacularRedocView.as_view(), name='redoc'),
    path('admin/', admin.site.urls),
    path('api/v1/', include(urls.urlpatterns)),
    path('api/v1/auth/', include('rest_framework.urls')),
    path('api/v1/auth/login/', views.login_access),
    path('accounts/profile/', views.redirect_to_note, name='redirect-to-note'),
    path('api/v1/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/v1/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/v1/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('api/v1/token/blacklist/', TokenBlacklistView.as_view(), name='token_blacklist'),
]


