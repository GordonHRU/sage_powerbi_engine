from django.contrib import admin
from .models import Program

class ProgramAdmin(admin.ModelAdmin):
    list_display = ('program_id', 'method', 'program_name', 'created_at',)
    search_fields = ('program_name',)
    list_filter = ('method', 'output_type')
    readonly_fields = ('created_at', 'updated_at', 'program_id')

admin.site.register(Program, ProgramAdmin)
