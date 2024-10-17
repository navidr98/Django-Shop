from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .forms import UserCreationForm, UserChangeForm
from .models import User
from django.contrib.auth.models import Group


class UserAdmin(BaseUserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm

    list_display = ('email', 'phone_number', 'is_admin')
    list_filter = ('is_admin',)

    fieldsets = (
        (None, {'fields':('email', 'phone_number', 'password')}),
        ('Permissions', {'fields':('is_active', 'is_admin', 'last_login')}),
    )

    add_fieldsets = (
        (None, {'fields':('email', 'phone_number', 'password1', 'password2')}),
    )

    search_fields = ('email', )
    ordering = ('email', )
    filter_horizontal = ()

admin.site.unregister(Group)
admin.site.register(User, UserAdmin)