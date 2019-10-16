from django.core.management import BaseCommand
from marketing.models import Submission
from employee.models import Team,User
from discord_webhook import DiscordWebhook, DiscordEmbed
from django.utils import timezone
from .discord_bot_url import discord_url
from django.db.models import Q
from datetime import timedelta

class Command(BaseCommand):
    # Show this when the user types help
    help = "this command is for posting your payload to slack using discord app"

    # A command must define handle()
    def handle(self, *args, **options):

        # marketers = User.objects.filter(Q(role__name='marketer') | Q(role__name='admin'))

        teams = Team.objects.all()
        for team in teams:
            today_date = timezone.now().date() - timedelta(days=1)
            marketers = team.employees.filter(role__name='marketer')
            total_submissions_company = 0
            employee = ''
            for marketer in marketers:
                total_submission = Submission.objects.filter(lead__marketer=marketer).filter(
                    created=today_date).count()
                employee += '{0} : {1}'.format(marketer.full_name, total_submission) + '\n'
                total_submissions_company += total_submission

            webhook = DiscordWebhook(url=discord_url, username=team.name,
                                     content="**Submission Made on {0}**".format(today_date))
            text = 'Total Submissions = {0}'.format(total_submissions_company)
            if total_submissions_company > 0:
                embed = DiscordEmbed(description=text, color=242424)
                list = DiscordEmbed(description=employee, color=242424)
                webhook.add_embed(embed)
                webhook.add_embed(list)
            else:
                text =  'No submission for {0}'.format(today_date)
                embed = DiscordEmbed(description=text)
                webhook.add_embed(embed)



            webhook.execute()