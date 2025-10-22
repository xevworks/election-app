from django.contrib import admin
from .models import Election, Candidate, VoterToken, Vote, FraudReport


@admin.register(Election)
class ElectionAdmin(admin.ModelAdmin):
    list_display = ['year', 'start_date', 'end_date', 'is_open', 'show_results']
    list_filter = ['is_open', 'show_results', 'year']
    search_fields = ['year']
    ordering = ['-year']
    list_editable = ['is_open', 'show_results']


@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = ['name', 'election', 'vision_short', 'poster_url']
    list_filter = ['election']
    search_fields = ['name', 'vision']
    ordering = ['election', 'name']
    
    def vision_short(self, obj):
        return obj.vision[:50] + '...' if len(obj.vision) > 50 else obj.vision
    vision_short.short_description = 'Vision'


@admin.register(VoterToken)
class VoterTokenAdmin(admin.ModelAdmin):
    list_display = ['email', 'election', 'token', 'used', 'id']
    list_filter = ['election', 'used']
    search_fields = ['email', 'token']
    ordering = ['election', 'email']
    readonly_fields = ['id']
    list_editable = ['used']


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ['election', 'candidate', 'email', 'created_at']
    list_filter = ['election', 'candidate', 'created_at']
    search_fields = ['email', 'candidate__name']
    ordering = ['-created_at']
    readonly_fields = ['created_at']
    
    # Prevent editing/deleting votes for audit trail
    def has_change_permission(self, request, obj=None):
        return False
    
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser  # Only superusers can delete


@admin.register(FraudReport)
class FraudReportAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'message_short', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'email', 'message']
    ordering = ['-created_at']
    readonly_fields = ['created_at']
    
    def message_short(self, obj):
        return obj.message[:75] + '...' if len(obj.message) > 75 else obj.message
    message_short.short_description = 'Message'
