from typing import Union
from django.db import models
from django.contrib.auth.models import AbstractUser
from rest_framework.authtoken.models import Token


class User(AbstractUser):
    username = models.CharField(max_length=60, unique=True)
    email = models.EmailField(unique=True)
    balance = models.FloatField(default=0)


class Operations(models.Model):
    TYP = [
        (1, 'Росход'),
        (2, 'Доход'),
    ]
    user = models.ForeignKey(to='User', on_delete=models.CASCADE, verbose_name='Ползователь')
    category = models.ForeignKey(to='Category', on_delete=models.CASCADE, verbose_name="Категория", default=1)
    typ = models.IntegerField(choices=TYP, verbose_name='Тип')
    amount = models.FloatField(verbose_name='Сумма')
    date_time = models.DateTimeField(auto_now=True, verbose_name='Время создания')
    comment = models.CharField(max_length=75, default='')


class Category(models.Model):
    title = models.CharField(max_length=125, verbose_name='Название категории:')
    user = models.ForeignKey('User', on_delete=models.CASCADE, verbose_name='Пользователь')

    @staticmethod
    def get_categories(user):
        return Category.objects.filter(user_id=user.id)

    def __str__(self):
        return self.title





