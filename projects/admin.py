from django.contrib import admin
from .models import Project, Session, InterestedParticipant


class ProjectAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {'fields': (
            'owner',
            'name',
            'description',
            'image',
            'active',
            'stack',
            'languages',
            'level',
        )}),
    )
    list_display = ('name', 'owner', 'date_created', 'active', 'stack', 'level')
    list_filter = ('active', 'stack', 'level')
    search_fields = ('name', 'owner__username', 'stack__name', 'level__name')
    ordering = ('-date_created',)
    readonly_fields = ('date_created',)


class SessionAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {'fields': (
            'project',
            'host',
            'description',
            'schedule_date_time',
            'duration',
            'stack',
            'level',
            'languages',
            'session_link',
            'participant_limit',
            'active',
            'public',
            'participants',
        )}),
    )
    list_display = ('description', 'project', 'schedule_date_time', 'duration', 'stack', 'level', 'active', 'public')
    list_filter = ('active', 'stack', 'level', 'public')
    search_fields = ('description', 'project__name', 'stack__name', 'level__name')
    ordering = ('-schedule_date_time',)


class InterestedParticipantAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {'fields': (
            'user',
            'session',
        )}),
    )
    list_display = ('user', 'session', 'date_created_interested')
    search_fields = ('user__username', 'session__description')
    list_filter = ('date_created_interested',)
    readonly_fields = ('date_created_interested',)


admin.site.register(Project, ProjectAdmin)
admin.site.register(Session, SessionAdmin)
admin.site.register(InterestedParticipant, InterestedParticipantAdmin)
