from django.contrib import admin
from .models import Audit, Requirement, Inspection, InspectionResult

@admin.register(Audit)
class AuditAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)

@admin.register(Requirement)
class RequirementAdmin(admin.ModelAdmin):
    list_display = ('text', 'audit')
    search_fields = ('text',)

@admin.register(Inspection)
class InspectionAdmin(admin.ModelAdmin):
    list_display = ('id', 'audit', 'user', 'created_at', 'completed_at')
    search_fields = ('audit__name', 'user__username')

@admin.register(InspectionResult)
class InspectionResultAdmin(admin.ModelAdmin):
    list_display = ('inspection', 'requirement', 'is_met', 'comment')
    search_fields = ('inspection__audit__name', 'requirement__text')