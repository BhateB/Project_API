from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.fields import GenericRelation

from attachments.models import Attachment
from utils_app.models import TimeStampedModel
from employee.models import Team, GENDER_CHOICE

User = get_user_model()

CONSULTANT_CHOICE = (
    ('in_marketing', 'In Marketing'),
    ('archived', 'Archived'),
    ('on_project', 'On Project'),
)


class Consultant(TimeStampedModel):
    name = models.CharField(_('Full Name'), max_length=100)
    email = models.EmailField(_('Email ID'), unique=True)
    recruiter = models.ForeignKey(User, on_delete=models.PROTECT, related_name=_('recruits'))
    marketer = models.ManyToManyField(User, related_name='marketed', blank=True)
    team = models.ForeignKey(Team, on_delete=models.PROTECT, null=True, blank=True)
    rate = models.DecimalField(_('Rate'), max_digits=6, decimal_places=2, blank=True, null=True)
    skills = models.CharField(_('Skills'), max_length=100, null=True, blank=True)
    gender = models.CharField(_('Gender'), max_length=10, choices=GENDER_CHOICE, null=True, blank=True)
    ssn = models.IntegerField(_('SSN ID'), null=True, blank=True)
    rtg = models.BooleanField(_('Ready to Go'), null=True, blank=True)
    status = models.CharField(_('status'), max_length=15, choices=CONSULTANT_CHOICE, default='in_marketing')

    def save(self, *args, **kwargs):
        """
            On save timestamps
        """
        if not self.id:
            self.created = timezone.now()
        return super(Consultant, self).save(*args, **kwargs)

    def __str__(self):
        return "{} {}".format(self.email, self.name)

    @property
    def get_attachment(self):
        return self.files.all()

    @property
    def recruiter_name(self):
        return self.recruiter.full_name


class File(TimeStampedModel):
    consultant = models.ForeignKey(Consultant, on_delete=models.CASCADE, related_name='files')
    name = models.CharField(_('Full Name'), max_length=300)
    path = models.CharField(_('Path'), max_length=300)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """
            On save timestamps
        """
        if not self.id:
            self.created = timezone.now()
        self.modified = timezone.now()
        return super(File, self).save(*args, **kwargs)


class ConsultantProfile(TimeStampedModel):
    title = models.CharField(max_length=200, blank=True, null=True)
    consultant = models.ForeignKey(Consultant, on_delete=models.CASCADE, related_name='profiles')
    owner = models.ForeignKey(User, on_delete=models.PROTECT, related_name=_('profiles'))
    is_original = models.BooleanField(_('Original Details'), default=False)
    dob = models.DateField(_('Date of birth'), blank=True, null=True)
    location = models.CharField(_('Location'), max_length=100, blank=True, null=True)
    education = models.CharField(_('Education'), max_length=100, blank=True, null=True)
    links = models.CharField(_('Links'), max_length=100, blank=True, null=True)
    visa_type = models.CharField(_('Visa Type'), max_length=20, blank=True, null=True)
    visa_start = models.DateField(_('Visa Start Date'), blank=True, null=True)
    visa_end = models.DateField(_('Visa End Date'), blank=True, null=True)
    attachments = GenericRelation(Attachment)

    def save(self, *args, **kwargs):
        """
            On save timestamps
        """
        if not self.id:
            self.created = timezone.now()
        self.modified = timezone.now()
        return super(ConsultantProfile, self).save(*args, **kwargs)

    def __str__(self):
        return self.consultant.name

    @property
    def owner_name(self):
        return self.owner.full_name

    @property
    def consultant_name(self):
        return self.consultant.name

    @property
    def recruiter_name(self):
        return self.consultant.recruiter_name

    @property
    def get_attachment(self):
        return self.attachments.all()
