from django.contrib import admin
from .models import User, Group

# Register your models here.
class UserAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'username', "email")
    search_fields = ('username','email',)
    readonly_fields = ('user_id', )

class GroupAdmin(admin.ModelAdmin):
    list_display = ('group_id', 'group_name', 'created_at')
    search_fields = ('group_name',)
    readonly_fields = ('created_at', 'updated_at', 'group_id')

admin.site.register(User, UserAdmin)
admin.site.register(Group, GroupAdmin)

