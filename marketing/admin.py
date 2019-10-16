import csv
from marketing.models import *
from django.contrib import admin
from django.http import HttpResponse


class ExportCsvMixin:
    def export_as_csv(self, request, queryset):
        meta = self.model._meta
        field_names = [field.name for field in meta.fields]

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename={}.csv'.format(meta)
        writer = csv.writer(response)

        writer.writerow(field_names)
        for obj in queryset:
            row = writer.writerow([getattr(obj, field) for field in field_names])

        return response

    export_as_csv.short_description = "Export Selected To CSV "


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin, ExportCsvMixin):
    list_display = ('id', 'name', 'address', 'vendor_display')
    search_fields = ('id', 'name')
    actions = ["export_as_csv"]

    def vendor_display(self, obj):
        return ", ".join([
            child.name for child in obj.vendors.all()
        ])

    vendor_display.short_description = "Vendor"


@admin.register(Vendor)
class VendorAdmin(admin.ModelAdmin, ExportCsvMixin):
    list_display = ('id', 'name', 'email', 'number', 'company', 'owner')
    search_fields = ('name', 'email', 'company__name', 'owner__email', 'owner__full_name', 'owner__employee_id')
    actions = ["export_as_csv"]


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin, ExportCsvMixin):
    list_display = ('id', 'job_title', 'location', 'source', 'status', 'marketer', 'vendor', 'sub_display')
    search_fields = ('job_desc', 'status', 'marketer__full_name', 'vendor__name')
    actions = ["export_as_csv"]

    def sub_display(self, obj):
        return ", ".join([
            child.consultant.consultant.name for child in obj.submission.all()
        ])

    sub_display.short_description = "Submission"


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin, ExportCsvMixin):
    list_display = (
        'id', 'lead', 'rate', 'consultant', 'vendor', 'client', 'marketing_email', 'status', 'screening_display')
    search_fields = ('consultant__consultant__name', 'status', 'lead__marketer__full_name')
    actions = ["export_as_csv"]

    def screening_display(self, obj):
        return ", ".join([
            child.ctb.full_name for child in obj.screening.all()
        ])

    screening_display.short_description = "Screening"


@admin.register(Screening)
class ScreeningAdmin(admin.ModelAdmin, ExportCsvMixin):
    list_display = ('id', 'submission', 'ctb', 'status', 'type', 'round', 'call_details', 'calendar_id', 'start_date', 'end_date')
    search_fields = ('submission__consultant__name', 'ctb', 'status', 'type', 'calendar_id')
    actions = ["export_as_csv"]
