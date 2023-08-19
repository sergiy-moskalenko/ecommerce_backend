from django.contrib import admin
from django.contrib.auth.models import Group

from accounts.models import User


class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'phone_number', 'id')
    empty_value_display = '-empty-'


admin.site.register(User, UserAdmin)

admin.site.unregister(Group)
