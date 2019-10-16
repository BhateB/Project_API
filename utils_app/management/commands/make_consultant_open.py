from django.core.management import BaseCommand
from marketing.models import Submission, Consultant
from employee.models import Team
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q


class Command(BaseCommand):
    # Show this when the user types help
    help = "this command is for Consultant who have been inactive "

    # A command must define handle()
    def handle(self, *args, **options):
        upperlimit = timezone.now().date() - timedelta(days=45)
        lower_limit = timezone.now().date() - timedelta(days=46)

        consultants = Consultant.objects.filter(
            Q(created__lte=upperlimit) |
            Q(created__gt=lower_limit)
        )

        if consultants:
            team = Team.objects.get(name='open')
            for consultant in consultants:
                consultant.team = team
                consultant.save()



