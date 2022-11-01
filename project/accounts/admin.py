from django.contrib import admin

from accounts.models import User


class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'phone_number', 'id')
    empty_value_display = '-empty-'


admin.site.register(User, UserAdmin)
