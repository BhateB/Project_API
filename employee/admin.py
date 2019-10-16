from django.contrib import admin
from employee.models import *
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserCreationForm
from django import forms
from django.utils.translation import ugettext_lazy as _
from marketing.admin import ExportCsvMixin


@admin.register(User)
class CustomUserAdmin(UserAdmin, ExportCsvMixin):
    fieldsets = ((None, {'fields': ('team', 'employee_id', 'username', 'email', 'password')}),
                 ('Personal info', {'fields': ('full_name', 'avatar', 'phone', 'gender', 'role')}),
                 ('Permissions', {'fields': ('is_active', 'is_superuser', 'is_staff', 'user_permissions')}),
                 ('Important dates', {'fields': ('last_login', 'date_joined')}),
                 )

    list_display = ('id', 'employee_id', 'email', 'full_name', 'team', 'gender', 'is_active', 'roles', 'consultant_assigned')
    search_fields = ('email', 'employee_id', 'first_name', 'id', 'username', 'team__name')
    actions = ["export_as_csv"]

    def roles(self, obj):
        return ", ".join([
            role.name for role in obj.role.all()
        ])

    roles.short_description = "Roles"

    def consultant_assigned(self, obj):
        return ", ".join([
            user.name for user in obj.marketed.all()
        ])

    consultant_assigned.short_description = "Consultant Assigned"


class UserCreationFormExtended(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super(UserCreationFormExtended, self).__init__(*args, **kwargs)
        self.fields['employee_id'] = forms.IntegerField(label=_("Employee-ID"))
        self.fields['username'] = forms.IntegerField(label=_("Username"))
        self.fields['email'] = forms.EmailField(label=_("E-mail"), max_length=75)


UserAdmin.add_form = UserCreationFormExtended
UserAdmin.add_fieldsets = (
    (None, {
        'classes': ('wide',),
        'fields': ('employee_id', 'username', 'email', 'gender', 'password1', 'password2',)
    }),
)


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'address')
    search_fields = ('name',)


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)
