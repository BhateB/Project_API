from django.core.management import BaseCommand
from marketing.models import Screening
from django.db.models import Q
from django.utils import timezone
from discord_webhook import DiscordWebhook,DiscordEmbed
from .discord_bot_url import discord_url



class Command(BaseCommand):
    # Show this when the user types help
    help = "this command is for posting your payload to slack using discord app"

    # A command must define handle()
    def handle(self, *args, **options):
        today_date = timezone.now().date()
        screenings = Screening.objects.filter(type__in=['telephonic', 'video_call', 'voice_call', 'f2f']).filter(
            status='scheduled').filter(start_date__date=today_date)
        for screening in screenings:
            text = "CTB:{0} ::  Round:{1} :: {2} :: {3} :: {4} :: {5} :: {6}" \
                .format(screening.ctb.full_name,
                        screening.round,
                        screening.get_type_display(),
                        screening.start_date.strftime('%d/%m/%Y::%H:%M EST'),
                        screening.consultant,
                        screening.submission.client,
                        screening.marketer)
            webhook = DiscordWebhook(url=discord_url, username=screening.submission.lead.marketer.team.name,
                                     content="**The following interview has been scheduled for today**")
            embed = DiscordEmbed(description=text, color=242424)


            webhook.add_embed(embed)
            webhook.execute()






