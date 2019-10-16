from marketing.models import *
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.fields import GenericRelation

from attachments.models import Attachment
from utils_app.models import TimeStampedModel

PROJECT_CHOICES = (
    ('joined', 'Joined'),
    ('not_joined', 'Not Joined'),
    ('extended', 'Extended'),
    ('fired', 'Fired'),
    ('completed', 'Completed'),
    ('failure-compliance_term', 'Failure Compliance Term'),
    ('con_declined', 'Failure Consultant Declined'),
    ('cancelled', 'Failure Cancelled'),
    ('dual_offer', 'Failure Dual Offer'),
)


class Project(TimeStampedModel):
    submission = models.OneToOneField(Submission, on_delete=models.PROTECT, related_name='project')
    consultant_joined = models.ForeignKey(Consultant, on_delete=models.PROTECT, null=True, blank=True,
                                          related_name='project')
    status = models.CharField(_('Status'), max_length=20, choices=PROJECT_CHOICES, null=True, blank=True)
    payment_term = models.IntegerField(_('Payment Term'), null=True, blank=True)
    invoicing_period = models.IntegerField(_('Invoicing Period'), null=True, blank=True)
    start_time = models.DateField(_('Start Time'), null=True, blank=True)
    end_time = models.DateField(_('End Time'), null=True, blank=True)
    feedback = models.TextField(_('Reason of Failure'), null=True, blank=True)
    duration = models.CharField(_('Duration'), max_length=50, null=True, blank=True)
    location = models.CharField(_('Location Of Client'), max_length=300, null=True, blank=True)
    city = models.CharField(_('City of Client'), max_length=25, null=True, blank=True)
    attachments = GenericRelation(Attachment)

    def save(self, *args, **kwargs):
        """
            On save timestamps
        """
        if not self.id:
            self.created = timezone.now()
        self.modified = timezone.now()
        return super(Project, self).save(*args, **kwargs)

    def __str__(self):
        return self.submission.consultant.consultant.name

    @property
    def consultant(self):
        return self.submission.consultant_name

    @property
    def vendor(self):
        return self.submission.vendor

    @property
    def marketer(self):
        return self.submission.marketer

    @property
    def team(self):
        return self.submission.lead.marketer.team.name
