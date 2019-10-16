from django.contrib import admin
from consultant.models import Consultant, ConsultantProfile, File
from marketing.admin import ExportCsvMixin


@admin.register(Consultant)
class ConsultantAdmin(admin.ModelAdmin, ExportCsvMixin):
    list_display = ('id', 'email', 'name', 'recruiter', 'team', 'gender', 'status', 'rate', 'skills', 'ssn', 'rtg')
    search_fields = ('id', 'email', 'name', 'recruiter__full_name', 'marketer__full_name', 'skills')
    actions = ["export_as_csv"]


@admin.register(File)
class ConsultantAdmin(admin.ModelAdmin, ExportCsvMixin):
    list_display = ('id', 'name', 'path', 'consultant', 'created')
    search_fields = ('id', 'name', 'path', 'consultant__name')
    actions = ["export_as_csv"]


@admin.register(ConsultantProfile)
class ConsultantProfileAdmin(admin.ModelAdmin, ExportCsvMixin):
    list_display = ('id', 'title', 'consultant', 'owner', 'dob', 'location', 'education', 'visa_type', 'is_original')
    search_fields = (
        'id', 'consultant__name', 'consultant__email', 'location', 'visa_type', 'owner__email', 'owner__full_name')
    actions = ["export_as_csv"]
