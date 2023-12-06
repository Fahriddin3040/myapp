from rest_framework import serializers
from rest_framework.response import Response

from .functions import get_balance, history
from .models import Operations, User, Category
from typing import Union
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth.hashers import make_password


class UserSerializer(serializers.ModelSerializer):
	id = serializers.IntegerField(read_only=True)
	balance = serializers.SerializerMethodField(method_name='get_balance')
	password = serializers.CharField(write_only=True)
	row_password = serializers.CharField(max_length=50, write_only=True)

	def validate(self, values):
		password = values.get("password")
		row_password = values.pop("row_password")
		if password != row_password:
			raise serializers.ValidationError({"password": "Пароли не совподают"})

		password = values.get('password')
		values['password'] = make_password(password)

		return values

	class Meta:
		model = User
		fields = ('id', 'first_name', 'last_name', 'username', 'password', 'row_password', 'email', 'balance')

	def get_balance(self, obj) -> Union[float, int]:
		result = 0
		notes = Operations.objects.filter(user=obj)

		for note in notes:
			if note.typ == 1:
				result -= note.amount
			elif note.typ == 2:
				result += note.amount
		result += obj.balance

		return result


class OperationSerializer(serializers.ModelSerializer):
	category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())
	category_title = serializers.SerializerMethodField(method_name='get_category_title')
	user = serializers.StringRelatedField(read_only=True)
	balance = serializers.SerializerMethodField(read_only=True, method_name = 'get_balance')

	class Meta:
		model = Operations
		fields = ['id', 'user', 'category', 'category_title', 'balance', 'typ', 'comment', 'amount', 'date_time']

	def __init__(self, *args, **kwargs):
		super(OperationSerializer, self).__init__(*args, **kwargs)
		request = self.context.get('request')
		if request and request.user:
			user_categories = Category.objects.filter(user_id=request.user.id)
			self.fields['category'].queryset = user_categories

	def get_balance(self, obj) -> Union[float, int]:
		return get_balance(obj.user)

	def get_category_title(self, obj) -> str:
		return obj.category.title

	def get_username(self, obj) -> str:
		return obj.user.username

	def get_categories(self):
		categories = Category.objects.filter(user=self.user)
		return categories


class BalanceSerializer(serializers.Serializer):
	balance = serializers.FloatField()


class CategorySerializer(serializers.ModelSerializer):
	user = serializers.CharField(read_only=True)

	class Meta:
		model = Category
		fields = ['id', 'user', 'title']


class TokenObtainSerializer(TokenObtainPairSerializer):
	@classmethod
	def get_token(cls, user):
		token = super().get_token(user)
		token['name'] = user.username

		return token


class PasswordSerializer(serializers.ModelSerializer):
	row_password = serializers.CharField(max_length=55, write_only=True)
	id = serializers.CharField(read_only=True)

	class Meta:
		model = User
		fields = ['id', 'password', 'row_password']

	def validate(self, values):
		password = values.get('password')
		row_password = values.pop('row_password')

		if password == row_password:
			values['password'] = make_password(password)

			return values

		else:
			raise serializers.ValidationError({'password': 'Пароли не совпадают!'})


# SECURE_SSL_REDIRECT=False
# SESSION_COOKIE_SECURE=False
# CSRF_COOKIE_SECURE=False


