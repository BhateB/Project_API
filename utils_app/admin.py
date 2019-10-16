from django.contrib import admin
from .models import City
from marketing.admin import ExportCsvMixin


@admin.register(City)
class ProjectAdmin(admin.ModelAdmin, ExportCsvMixin):
    list_display = ('name', 'state')
    search_fields = ('name', 'state')
    actions = ["export_as_csv"]
