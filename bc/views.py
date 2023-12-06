import rest_framework.exceptions
from django.contrib.auth.hashers import make_password
from django.http import HttpResponseRedirect
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema_view, extend_schema
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from .functions import history
from .serializers import OperationSerializer, UserSerializer, CategorySerializer, PasswordSerializer, BalanceSerializer
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication
from rest_framework import viewsets, status
from .models import Category, User
from . import models


@extend_schema_view(
    list=extend_schema(
        summary="Получить список постов",
    ),
    update=extend_schema(
        summary="Изменение существующего поста",
    ),
    destroy=extend_schema(
        description='Это вот, типо описание!',
    ),
    create=extend_schema(
        summary="Создание нового поста",
    ),
    retrieve=extend_schema(
        summary='Частичный возврат!'
    ),
)
class OperationModelViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    serializer_class = OperationSerializer
    queryset = models.Operations.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['date_time', 'typ', 'amount']
    search_fields = ['category__title', 'amount']

    def add_balance(self, user, data):
        data = {
            'balance': user.balance,
            'data': data
        }

        return data

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(user_id=self.request.user.id)

    def update(self, request, *args, **kwargs):
        data = request.data
        instance = self.get_object()
        serializer = self.serializer_class(instance=instance, data=data)
        serializer.is_valid(raise_exception=True)
        category = serializer.validated_data.get('category', False)

        if category and category.user != request.user:
            raise rest_framework.exceptions.ValidationError("У вас нет доступа в заданной категории!")

        serializer.save()
        return Response(serializer.data, status=201)

    @extend_schema(summary="Частичное получение", description='Возвращает определённый объект операции.')
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance=instance)
        if instance.user != request.user:
            raise rest_framework.exceptions.NotAcceptable('У вас нет доступа к этой записи!')

        return Response(serializer.data)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        user = request.user

        if page is not None:
            serializer = self.get_serializer(page, many=True)
            data = self.add_balance(user, serializer)
            return self.get_paginated_response(data=data)

        serializer = self.get_serializer(queryset, many=True)
        data = self.add_balance(user, serializer.data)
        return Response(data)

    @extend_schema(summary="Удалить операцию", description="Удаляет определённую запись.")
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()

        return Response("Запись успешно удалена!")

    def create(self, request, *args, **kwargs):
        data = request.data
        category = data.get('category', None)
        cat_obj = Category.objects.filter(id=category, user_id=request.user)

        if cat_obj:
            serializer = self.serializer_class(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.validated_data['user'] = request.user
            serializer.save(user=request.user)
            return Response(serializer.data, status=201)

        else:
            raise rest_framework.exceptions.ValidationError('Выбрана некорректная категория!!!')


@extend_schema_view(

)
class UserAPIView(viewsets.ModelViewSet):
    queryset = models.User.objects.all()
    serializer_class = UserSerializer

    def set_password(self, row_password):
        password = make_password(row_password)
        return password

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        tokens = TokenObtainPairView.as_view()
        return Response(serializer.data)

    def retrieve(self, request, *args):
        user = request.user
        serializer = self.serializer_class(user)
        return Response(serializer.data, status=201)

    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        partial = kwargs.pop('partial', False)
        instance = User.objects.get(id=request.user.id)
        serializer = self.serializer_class(instance=instance, data=request.data, partial=partial)

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)

    def destroy(self, request, *args):
        pk = request.user.id

        instance = self.queryset.filter(id=pk)
        instance.delete()

        return Response("Ваш аккаунт был успешно удалён! !")


class UserPasswordAPIView(UserAPIView):

    serializer_class = PasswordSerializer

    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        partial = kwargs.pop('partial', False)
        instance = User.objects.get(id=request.user.id)
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        user = request.user
        serializer.validated_data['user'] = user
        self.perform_update(serializer)

        return Response(serializer.data)


@extend_schema_view(
    list=extend_schema(
        summary="Получить список категорий авторизированного пользователья",
    ),
    update=extend_schema(
        summary="Изменение существующкей категории",
    ),
    destroy=extend_schema(
        summary="Удаление определённой категории",
    ),
    create=extend_schema(
        summary="Добавление категории пользователья",
    ),
    retrieve=extend_schema(
        summary='Частичный возврат!'
    ),
)
class CategoryApiView(viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    queryset = models.Category.objects.all()
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def is_unique(self, title):
        unique = bool(self.queryset.filter(title=title))

        if unique == True:
            raise rest_framework.exceptions.NotFound('Некорректно')

    def get(self, request):
        queryset = self.queryset.filter(user_id=self.request.user.id)
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)

    def raise_NOT_FOUND(self):
        raise rest_framework.exceptions.NotAcceptable('У вас нет доступа к этой записи!')

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        title = instance.title
        if instance.user == request.user:
            return super().update(request, *args,  **kwargs)

        self.raise_NOT_FOUND()

    def get_detail(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        if instance.user != request.user:
            self.raise_NOT_FOUND()

        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.is_unique(serializer.validated_data['title'])
        serializer.save(user=self.request.user)
        return Response(serializer.data)

    def delete(self, request, pk):
        instance = self.get_object()

        if instance.user != request.user:
            self.raise_NOT_FOUND()
        instance.delete()

        return Response('Выбранная категория была улалена!')


class BalanceAPIView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    serializer_class = BalanceSerializer
    queryset = models.Operations.objects

    def patch(self, request):
        user = request.user

        serializer = BalanceSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        value = serializer.validated_data['balance']
        ops_history = history(user.id)

        user.balance = value - ops_history
        user.save()

        return Response({'balance': value})


def redirect_to_note(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('/api/v1/note')
    else:
        return HttpResponseRedirect('/api/auth/login')


def login_access(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('/api/v1/auth/login/')
    else:
        return HttpResponseRedirect('/api/v1/note/')


# def tokens_for_user(user):
#     refresh = RefreshToken.for_user(user)
#
#     return {
#         'refresh': str(refresh),
#         'access': str(refresh.access.token),
#     }
