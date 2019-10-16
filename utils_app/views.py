from datetime import date, timedelta, datetime, timezone
from rest_framework.authentication import TokenAuthentication
from rest_framework.generics import ListAPIView, CreateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .models import City
from dhooks import Webhook, Embed


def get_custom_time_filter(self, filter_by):
    if filter_by == 'today':
        queryset = self.objects.filter(created__gte=date.today())
    elif filter_by == 'month':
        start_of_month = date.today().replace(day=1)
        queryset = self.objects.filter(created__gte=start_of_month)
    elif filter_by == 'week':
        date1 = date.today()
        start_of_week = date1.today() - timedelta(date1.weekday())
        queryset = self.objects.filter(created__gte=start_of_week)
    elif filter_by == 'last_week':
        last_day = timezone.now().date() - timedelta(days=7)
        queryset = self.objects.filter(created__gte=last_day)
    else:
        queryset = self.objects.all()
    return queryset


class CitiesView(ListAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        query = request.query_params.get('query', None)
        if len(query) == 0:
            return Response({"results": [], 'total': 0}, status=status.HTTP_200_OK)
        if query:
            city = City.objects.filter(name__istartswith=query).values('id', 'name', 'state')
        else:
            city = City.objects.all().values('id', 'name', 'state')
        total = city.count()
        return Response({"results": city, 'total': total}, status=status.HTTP_200_OK)


class DiscordSendMessage(CreateAPIView):

    def create(self, request, *args, **kwargs):
        hook = Webhook(
            'https://discordapp.com/api/webhooks/580280563609632788/nIzYKAXp_QPYNXS_RebHyzdk9gZp'
            'L7BR9KuP_nOijZ-sUJVPhc9zhKPc_QTfeq9Hi_2S')
        amount = '500 USD'
        remark = 'Pleasure doing business'
        sender = 'John Smith'
        date = datetime.now()

        embed = Embed(
            description='A deposit of  been  made by Sender Name'.format('amount'),
            color=0x1e0f3,
            timestamp='now'  # sets the timestamp to current time
        )

        image1 = 'https://media.licdn.com/dms/image/C4D0BAQHxMPzB45mHUA/company-logo_200_200/0?e=' \
                 '2159024400&v=beta&t=OM8YJr5OScQ-AbkEurppCfj_w9aqC6pHSkOtThp7esc'
        image2 = 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcS_3JhISl_lgiXtYERmGDczpO7' \
                 'fgk_OODRdclyxCs2IsN1deJdJkg'

        embed.set_author(name='Paypal Deposit', icon_url=image2)
        embed.add_field(name='Sender Name', value=sender)
        embed.add_field(name='Amount', value=amount)
        embed.add_field(name='Remark', value=remark)
        embed.add_field(name='Date', value=date.strftime('%d-%m-%Y %X'))

        # embed.set_footer(text='Created by ConsultAdd Inc.', icon_url=image1)

        embed.set_thumbnail(image1)
        # embed.set_image(image2)

        hook.send(embed=embed)
        return Response({'results': 'success', }, status=status.HTTP_200_OK)
