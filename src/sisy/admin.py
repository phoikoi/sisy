from django.contrib import admin
from sisy.models import Task

class TaskAdmin(admin.ModelAdmin):
    readonly_fields = ('created_at','modified_at','running', '_extra_data','_func_info')
    list_display = ('label', 'schedule', 'next_run', 'enabled')

admin.site.register(Task, TaskAdmin)