from django.db import models
from django.utils import timezone
from consultant.models import Consultant, ConsultantProfile
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.fields import GenericRelation

from attachments.models import Attachment
from utils_app.models import TimeStampedModel

User = get_user_model()

STATUS_CHOICES = (
    ('new', 'New'),
    ('sub', 'Submitted'),
    ('archived', 'Archived'),
)

SUB_CHOICES = (
    ('sub', 'Submitted'),
    ('interview', 'Interview'),
    ('project', 'Project'),
)

SCREENING_STATUS_CHOICES = (
    ('passed', 'Passed'),
    ('failed', 'Failed'),
    ('cancelled', 'Cancelled'),
    ('scheduled', 'Scheduled'),
    ('rescheduled', 'Rescheduled'),
)

SCREENING_CHOICES = (
    ('f2f', 'Face-to-Face'),
    ('video_call', 'Video Call'),
    ('telephonic', 'Voice Call'),
    ('offline_test', 'Offline Test'),
    ('online_test', 'Online Test'),
    ('video_test', 'Video Test'),
    ('screening', 'Screening'),
)


class Company(models.Model):
    name = models.CharField(_('Company'), max_length=50)
    address = models.TextField(_('Address'), null=True, blank=True)

    def __str__(self):
        return self.name


class Vendor(TimeStampedModel):
    name = models.CharField(_('Name'), max_length=50)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='vendors', null=True, blank=True)
    email = models.EmailField(_('Email'), max_length=50, null=True, blank=True)
    number = models.CharField(_('Number'), max_length=15, null=True, blank=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vendors', null=True, blank=True)

    def __str__(self):
        return "{} from {}".format(self.name, self.company)

    def save(self, *args, **kwargs):
        """
            On save timestamps
        """
        if not self.id:
            self.created = timezone.now()
        self.modified = timezone.now()
        return super(Vendor, self).save(*args, **kwargs)


class Lead(TimeStampedModel):
    job_desc = models.TextField(_('Job Description'))
    location = models.CharField(_('Location'), max_length=50, blank=True, null=True)
    job_title = models.CharField(_('Job Title'), max_length=100, blank=True, null=True)
    vendor = models.ForeignKey(Vendor, on_delete=models.PROTECT, null=True, blank=True, related_name='leads')
    marketer = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True, related_name='leads')
    status = models.CharField(_('Status'), max_length=20, choices=STATUS_CHOICES, default='new')
    source = models.CharField(_('Source of Lead'), max_length=100, blank=True, null=True)

    def save(self, *args, **kwargs):
        """
            On save timestamps
        """
        if not self.id:
            self.created = timezone.now()
        self.modified = timezone.now()
        return super(Lead, self).save(*args, **kwargs)

    def __str__(self):
        return "{0} : {1} : {2}".format(self.vendor, self.location, self.marketer)

    @property
    def marketer_name(self):
        return self.marketer.full_name

    @property
    def company(self):
        return self.vendor.company.name


class Submission(TimeStampedModel):
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, related_name='submission')
    consultant = models.ForeignKey(ConsultantProfile, on_delete=models.PROTECT, related_name='submission')
    attachments = GenericRelation(Attachment)
    rate = models.FloatField(_('Rate'), null=True, blank=True)
    client = models.CharField(_('Client'), max_length=50, null=True, blank=True)
    employer = models.CharField(_('Employer'), max_length=50)
    marketing_email = models.EmailField(_('Marketing Email'), null=True, blank=True)
    status = models.CharField(_('Status'), max_length=20, choices=SUB_CHOICES, default='sub')

    def save(self, *args, **kwargs):
        """
            On save timestamps
        """
        if not self.id:
            self.created = timezone.now()
        self.modified = timezone.now()
        return super(Submission, self).save(*args, **kwargs)

    def __str__(self):
        return "{0} : {1} : {2}".format(self.lead.marketer, self.lead.vendor.company, self.client)

    @property
    def marketer(self):
        return self.lead.marketer_name

    @property
    def consultant_name(self):
        return self.consultant.consultant_name

    @property
    def attachment(self):
        return self.attachments.all()

    @property
    def vendor(self):
        return self.lead.company


class Screening(TimeStampedModel):
    round = models.IntegerField(default=1, null=True, blank=True)
    attachments = GenericRelation(Attachment)
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE, related_name='screening')
    ctb = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True, related_name='screening')
    guest = models.ManyToManyField(User, related_name='screenings', blank=True)
    description = models.TextField(_('Description'), null=True, blank=True)
    call_details = models.TextField(_('Call Details'), null=True, blank=True)
    calendar_id = models.CharField(_('Calendar ID'), max_length=50, null=True, blank=True)
    status = models.CharField(_('Status'), max_length=20, choices=SCREENING_STATUS_CHOICES, default='scheduled')
    start_date = models.DateTimeField(_('Start Date'), null=True, blank=True)
    end_date = models.DateTimeField(_('End Date'), null=True, blank=True)
    feedback = models.CharField(_('Feedback'), max_length=200, null=True, blank=True)
    type = models.CharField(_('Type'), max_length=20, choices=SCREENING_CHOICES)

    def __str__(self):
        return " Round: {0}, CTB: {1}".format(self.round, self.ctb)

    @property
    def marketer(self):
        return self.submission.marketer

    @property
    def consultant(self):
        return self.submission.consultant_name

    @property
    def vendor(self):
        return self.submission.vendor

    @property
    def team(self):
        return self.marketer.team.name

    def save(self, *args, **kwargs):
        """
            On save timestamps
        """
        if not self.id:
            self.created = timezone.now()
        self.modified = timezone.now()
        return super(Screening, self).save(*args, **kwargs)
