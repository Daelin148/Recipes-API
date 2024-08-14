from django.conf import settings
from django.contrib import admin

from .models import Follower, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'email', 'username', 'first_name', 'last_name',)
    list_filter = ('email', 'username',)
    search_fields = ('email', 'username',)
    empty_value_display = settings.EMPTY_VALUE_DISPLAY


@admin.register(Follower)
class FollowerAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'author',)
    list_filter = ('user', 'author',)
    search_fields = ('user', 'author',)
    empty_value_display = settings.EMPTY_VALUE_DISPLAY
