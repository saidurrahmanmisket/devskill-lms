from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'academic_id', 'email', 'first_name', 'last_name', 'role', 'is_active', 'is_staff')
    list_filter = ('role', 'is_active', 'is_staff')
    search_fields = ('username', 'academic_id', 'email', 'first_name', 'last_name')
    fieldsets = UserAdmin.fieldsets + (
        ('LMS Profile', {'fields': ('role', 'academic_id')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('LMS Profile', {'fields': ('role', 'academic_id')}),
    )
