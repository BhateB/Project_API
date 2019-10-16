import os
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

User = get_user_model()


ATTACHMENT_TYPE = (
    ('recordings', 'Interview Recordings'),
    ('resume', 'Resume'),
    ('results', 'Assessment Results'),
    ('misc', 'Miscellaneous'),
    ('ssn', 'SSN'),
    ('photo_id', 'Miscellaneous'),
    ('visa', 'Visa Docs'),
    ('academic', 'Academic Docs'),
    ('timesheet', 'Timesheet'),
    ('work_order', 'Work Order'),
    ('msa', 'MSA/Agreement'),
    ('work_order_msa', 'Work Order and MSA/Agreement'),
)


def attachment_upload(instance, filename):
    """Stores the attachment in a "per module/appname/primary key" folder"""
    return 'attachments/{app}_{model}/{pk}/{filename}'.format(
        app=instance.content_object._meta.app_label,
        model=instance.content_object._meta.object_name.lower(),
        pk=instance.content_object.pk,
        filename=filename,
    )


class AttachmentManager(models.Manager):
    def attachments_for_object(self, obj):
        object_type = ContentType.objects.get_for_model(obj)
        return self.filter(content_type__pk=object_type.id, object_id=obj.pk)


class Attachment(models.Model):
    objects = AttachmentManager()

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    creator = models.ForeignKey(User, related_name="created_attachments", on_delete=models.CASCADE)
    attachment_file = models.FileField(_('attachment'), upload_to=attachment_upload)
    attachment_type = models.CharField(choices=ATTACHMENT_TYPE, blank=True, null=True, max_length=500)
    created = models.DateTimeField(_('created'), auto_now_add=True)
    modified = models.DateTimeField(_('modified'), auto_now=True)

    class Meta:
        verbose_name = _("attachment")
        verbose_name_plural = _("attachments")
        ordering = ['-created']
        permissions = (
            ('delete_foreign_attachments', _('Can delete foreign attachments')),
        )

    def __str__(self):
        return _('{username} attached {filename}').format(
            username=self.creator.full_name,
            filename=self.attachment_file.name,
        )

    @property
    def filename(self):
        return os.path.split(self.attachment_file.name)[1]
