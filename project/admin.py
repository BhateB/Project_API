from django.contrib import admin
from .models import Project
from marketing.admin import ExportCsvMixin


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin, ExportCsvMixin):
    list_display = ('id', 'submission', 'start_time', 'end_time', 'payment_term', 'invoicing_period', 'duration',
                    'location', 'city', 'consultant_joined', 'status', 'created', 'modified')
    search_fields = ('consultant_joined__name', 'status', 'duration', 'start_time', 'end_time', 'city')
    actions = ["export_as_csv"]
