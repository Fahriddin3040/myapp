from django.urls import path
from . import views


METHODS_VOC = {
    'get': 'retrieve',  # Получение деталей объекта
    'delete': 'destroy',  # Удаление объекта
    'patch': 'update',
}

operation = views.OperationModelViewSet()
user = views.UserAPIView

urlpatterns = [

    path('profile/', views.UserAPIView.as_view(METHODS_VOC)),
    path('balance/', views.BalanceAPIView.as_view()),
    path('change_password/', views.UserPasswordAPIView.as_view({'patch': 'update'})),
    path('category/', views.CategoryApiView.as_view({'get': 'get', 'post': 'post'})),
    path('auth/register/', views.UserAPIView.as_view({'post': 'create'})),
    path('operations/', views.OperationModelViewSet.as_view({'get': 'list', 'post': 'create'})),
    path('operations/<int:pk>/', views.OperationModelViewSet.as_view({'get': 'retrieve', 'patch': 'update', 'delete': 'destroy'})),
    path('category/<int:pk>', views.CategoryApiView.as_view({'get': 'get_detail', 'patch': 'update', 'delete': 'delete'})),

]
