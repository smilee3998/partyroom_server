from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import CustomUser


class UserAdmin(BaseUserAdmin):
    # TODO Update admin
    model = CustomUser
    list_display = ['username', 'uid', 'email', 'phone_number', 'is_staff', 'is_verified']
# class UserAdmin(BaseUserAdmin):
#     fieldsets = (
#         (None, {'fields': ('username', 'password')}),
#         (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
#         (_('Permissions'), {
#             'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
#         }),
#         (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
#         (_('user_info'), {'fields': ('phone_number', )}),
#     )
#     list_display = ('username', 'email', 'phone_number', 'first_name', 'last_name', 'is_staff')


admin.site.register(CustomUser, UserAdmin)
