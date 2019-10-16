from django.contrib import admin
from .models import Attachment
from marketing.admin import ExportCsvMixin


@admin.register(Attachment)
class AttachmentAdmin(admin.ModelAdmin, ExportCsvMixin):
    list_display = ('id', 'content_type', 'creator', 'attachment_type', 'content_object')
    search_fields = ('id', 'content_type', 'creator', 'attachment_type')
    actions = ["export_as_csv"]
