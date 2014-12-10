from django.contrib import admin
from .models import TaskGroup, Task, LineItem


class TaskGroupAdmin(admin.ModelAdmin):
    pass

class TaskAdmin(admin.ModelAdmin):
    pass

class LineItemAdmin(admin.ModelAdmin):
    pass

admin.site.register(TaskGroup, TaskGroupAdmin)
admin.site.register(Task, TaskAdmin)
admin.site.register(LineItem, LineItemAdmin)