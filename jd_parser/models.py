from utils_app.models import *
from marketing.models import Lead
from django.contrib.postgres.fields import ArrayField
from django.utils.translation import ugettext_lazy as _


class JDParser(TimeStampedModel):
    jd = models.TextField(_('Job description'))
    job_title = models.CharField(max_length=50, null=True, blank=True)
    location = ArrayField(models.CharField(max_length=300), null=True, blank=True)
    lead = models.OneToOneField(Lead, on_delete=models.PROTECT, null=True, blank=True)

    def __str__(self):
        return self.job_title
