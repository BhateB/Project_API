from django.contrib import admin
from .models import JDParser
from marketing.admin import ExportCsvMixin


@admin.register(JDParser)
class ProjectAdmin(admin.ModelAdmin, ExportCsvMixin):
    list_display = ('id', 'jd', 'job_title', 'location', 'created', 'modified')
    search_fields = ('skills', 'job_title', 'location')
    actions = ["export_as_csv"]
