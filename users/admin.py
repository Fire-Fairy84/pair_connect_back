from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser


class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': (
            'name',
            'photo',
            'about_me',
            'telephone',
            'linkedin_link',
            'github_link',
            'discord_link',
            'stack',
            'level',
            'prog_language',
        )}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': (
            'name',
            'email',
            'password1',
            'password2',
            'photo',
            'about_me',
            'telephone',
            'linkedin_link',
            'github_link',
            'discord_link',
            'stack',
            'level',
            'prog_language',
        )}),
    )
    list_display = ('username', 'email', 'name', 'level', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'level')
    search_fields = ('username', 'email', 'name')


admin.site.register(CustomUser, CustomUserAdmin)
