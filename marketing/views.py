from datetime import datetime, timedelta, date
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView, RetrieveUpdateDestroyAPIView, RetrieveUpdateAPIView, \
    RetrieveAPIView

from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404
from django.db.models import Count, Q, F
from django.db import transaction
from .serializers import *
from utils_app.notification import send_notification
from attachments.models import Attachment
from project.models import Project
from utils_app.views import get_custom_time_filter
from utils_app.calendar_api import book_calendar, get_inteviews, update_calendar, delete_calendar_booking, SCRUM_MASTER
from .utils import email_parser_from_file
from discord_webhook import DiscordWebhook, DiscordEmbed
from utils_app.management.commands.discord_bot_url import discord_url


def discord_webhook(username, content, text):
    webhook = DiscordWebhook(url=discord_url, username=username,
                             content=content)
    embed = DiscordEmbed(description=text, color=242424)

    webhook.add_embed(embed)
    webhook.execute()


class CompanyView(RetrieveUpdateAPIView, CreateAPIView):
    serializer_class = CompanySerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        query = request.query_params.get("query", None)
        page = int(request.query_params.get("page", 1))
        last, first = page * 10, page * 10 - 10
        # data = {
        #     'user': request.user,
        #     'employee_id': 1111,
        #     'message': 'hello',
        #     'level': 'info',
        #     'verb': 'action',
        # }
        # send_notification(self, data)
        try:
            if len(query) == 0:
                return Response({"results": [], "total": 0}, status=status.HTTP_200_OK)
            if query:
                company = Company.objects.filter(name__contains=query)
                total = company.count()
                serializer = self.serializer_class(company[first:last], many=True)
                return Response({"results": serializer.data, "count": total}, status=status.HTTP_200_OK)
            queryset = Company.objects.all()
            total = queryset.count()
            data = queryset[first:last].values('id', 'name')
            return Response({"results": data, "total": total}, status=status.HTTP_200_OK)
        except Exception as error:
            return Response({"error": str(error)}, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request, *args, **kwargs):
        try:
            name = request.data.get('name').strip().lower()
            company, created = Company.objects.get_or_create(name=name)
            if created:
                company.address = request.data.get('address').strip()
                company.save()
                serializer = self.serializer_class(company)
                return Response({"result": serializer.data}, status=status.HTTP_201_CREATED)
            return Response({"result": "Company already exist"}, status=status.HTTP_406_NOT_ACCEPTABLE)
        except Exception as error:
            return Response({"error": str(error)}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        try:
            company = get_object_or_404(Company, id=request.data.get('id'))
            serializer = self.serializer_class(company, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({"result": serializer.data}, status=status.HTTP_201_CREATED)
            return Response({"result": str(serializer.errors)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as error:
            return Response({"error": str(error)}, status=status.HTTP_400_BAD_REQUEST)


class VendorView(RetrieveUpdateAPIView, CreateAPIView):
    serializer_class = VendorSerializer
    create_serializer_class = VendorCreateSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        try:
            company_id = request.query_params.get('company_id')
            vendor = Vendor.objects.filter(company_id=company_id, owner=request.user)
            data = vendor.values('id', 'name', 'email', 'number', 'company__name')
            return Response({"result": data}, status=status.HTTP_200_OK)
        except Exception as error:
            return Response({"error": str(error)}, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request, *args, **kwargs):
        email = request.data.get('email')
        vendor = Vendor.objects.filter(email__iexact=email)
        if vendor:
            return Response({"error": "already exists"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            vendor = Vendor(
                name=request.data.get('name').strip(),
                owner=request.user
            )
            serializer = self.create_serializer_class(vendor, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({"result": serializer.data}, status=status.HTTP_201_CREATED)
            return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as error:
            return Response({"error": str(error)}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        vendor = get_object_or_404(Vendor, id=request.data.get("vendor_id"))
        if vendor.owner != request.user:
            return Response({"error": "You cant edit this Vendor"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            serializer = self.serializer_class(vendor, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({"result": serializer.data}, status=status.HTTP_201_CREATED)
            return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as error:
            return Response({"error": str(error)}, status=status.HTTP_400_BAD_REQUEST)


class LeadView(RetrieveUpdateDestroyAPIView, CreateAPIView):
    serializer_class = LeadSerializer
    create_serializer_class = LeadCreateSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        lead_id = request.query_params.get('lead_id', None)
        query = request.query_params.get('query', None)
        city = request.query_params.get('city', None)
        search = request.query_params.get('search', None)
        filter_by = request.query_params.get('filter', 'all')
        page = int(request.query_params.get("page", 1))
        last, first = page * 10, page * 10 - 10

        lead = get_custom_time_filter(Lead, filter_by=filter_by)
        try:
            if query == 'map':
                leads = lead.filter(Q(marketer=self.request.user)).values('location'). \
                    annotate(total=Count('location')).order_by('total')
                return Response({"results": leads}, status=status.HTTP_200_OK)

            if query == 'archived':
                leads = lead.annotate(submission_count=Count('submission')).filter(
                    Q(marketer=self.request.user) & Q(status='archived')).order_by('-modified')

            elif lead_id:
                leads = Lead.objects.annotate(submission_count=Count('submission')).filter(
                    id=lead_id, marketer=request.user).order_by('-modified')

            elif search:
                leads = Lead.objects.annotate(submission_count=Count('submission')).filter(
                    Q(job_title__icontains=search) |
                    Q(location__icontains=search) |
                    Q(vendor__name__icontains=search) |
                    Q(vendor__email__icontains=search) |
                    Q(vendor__company__name__icontains=search) &
                    Q(marketer=request.user))

            elif city:
                leads = lead.annotate(submission_count=Count('submission')).filter(
                    Q(marketer=self.request.user, location__iexact=city) & ~Q(status='archived')).order_by('-modified')

            else:
                leads = lead.annotate(submission_count=Count('submission')).filter(
                    Q(marketer=self.request.user) & ~Q(status='archived')).order_by('-modified')

            total = leads.count()
            new = leads.filter(status='new').count()
            sub = leads.filter(status='sub').count()
            archive = leads.filter(status='archived').count()

            data_counts = {
                "new": new,
                "sub": sub,
                "archive": archive,
                "total": total,
            }

            data = leads[first:last].annotate(
                company_name=F('vendor__company__name')
            ).values('id', 'job_desc', 'location', 'job_title', 'source',
                     'company_name', 'vendor__name', 'vendor__email', 'vendor__number',
                     'status', 'created', 'modified', 'submission_count')

            return Response({"results": data, "counts": data_counts}, status=status.HTTP_200_OK)
        except Lead.DoesNotExist as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.create_serializer_class(data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                lead = Lead.objects.get(id=serializer.data["id"])
                lead.marketer = request.user
                lead.vendor_id = request.data.get('vendor')
                lead.save()
                return Response({"result": self.serializer_class(lead).data}, status=status.HTTP_201_CREATED)
            return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as error:
            return Response({"error": str(error)}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        archive_status = request.query_params.get('status', None)
        if archive_status:
            for lead_id in request.data.get("lead_ids"):
                try:
                    lead = Lead.objects.get(id=lead_id)
                    lead.status = 'archived'
                    lead.save()
                except Exception as error:
                    return Response({"error": str(error)}, status=status.HTTP_400_BAD_REQUEST)
            return Response({"result": "updates"}, status=status.HTTP_202_ACCEPTED)

        try:
            lead = get_object_or_404(Lead, id=request.data.get("lead_id"))
            serializer = self.create_serializer_class(lead, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({"result": serializer.data}, status=status.HTTP_202_ACCEPTED)
            return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as error:
            return Response({"error": str(error)}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        try:
            lead = get_object_or_404(Lead, id=request.data.get("lead_id"))
            lead.status = 'archived'
            lead.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as error:
            return Response({"error": str(error)}, status=status.HTTP_400_BAD_REQUEST)


class SubmissionView(RetrieveUpdateAPIView, CreateAPIView):
    serializer_class = SubmissionSerializer
    detail_serializer_class = SubmissionDetailSerializer
    create_serializer_class = SubmissionCreateSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        sub_id = request.query_params.get('sub_id', None)
        lead_id = request.query_params.get('lead_id', None)
        query = request.query_params.get('query', None)
        consultant_id = request.query_params.get('consultant_id', None)
        filter_by = request.query_params.get('filter', 'all')
        page = int(request.query_params.get("page", 1))
        last, first = page * 10, page * 10 - 10

        try:
            if sub_id:
                sub = get_object_or_404(Submission, id=sub_id)
                if sub.lead.vendor.owner == request.user:
                    serializer = self.detail_serializer_class(sub)
                    return Response({"results": serializer.data}, status=status.HTTP_200_OK)
                else:
                    serializer = self.serializer_class(sub)
                    return Response({"results": serializer.data}, status=status.HTTP_200_OK)

            elif lead_id:
                sub = Submission.objects.filter(lead_id=lead_id, lead__marketer=request.user).order_by('-modified')

            elif consultant_id:
                sub = Submission.objects.filter(consultant__consultant__id=consultant_id,
                                                consultant__consultant__team__name__in=['open', request.user.team.name])

            elif query:
                if 'admin' in request.user.roles:
                    sub = Submission.objects.filter(
                        Q(lead__marketer__team=request.user.team) &
                        Q(client__icontains=query) |
                        Q(lead__job_title__icontains=query) |
                        Q(lead__location__icontains=query) |
                        Q(lead__vendor__company__name__icontains=query) |
                        Q(consultant__consultant__name__icontains=query)
                    )
                else:
                    sub = Submission.objects.filter(
                        Q(lead__marketer=request.user) &
                        Q(client__icontains=query) |
                        Q(lead__job_title__icontains=query) |
                        Q(lead__location__icontains=query) |
                        Q(lead__vendor__company__name__icontains=query) |
                        Q(consultant__consultant__name__icontains=query)
                    )

            else:
                sub = get_custom_time_filter(Submission, filter_by)
                if 'admin' in request.user.roles:
                    sub = sub.filter(
                        Q(lead__marketer__team=request.user.team) |
                        Q(consultant__consultant__team__name='open') &
                        Q(status__in=['sub', 'interview'])).order_by('-modified')
                else:
                    sub = sub.filter(
                        Q(lead__marketer=request.user, ) |
                        Q(consultant__consultant__team__name='open') &
                        Q(status__in=['sub', 'interview'])).order_by('-modified')

            total = sub.count()
            submission = sub.filter(status='sub').count()
            interview = sub.filter(status='interview').count()
            project = sub.filter(status='project').count()

            sub_data = {
                'total': total,
                'sub': submission,
                'interview': interview,
                'project': project
            }
            data = sub[first:last].annotate(
                consultant_name=F('consultant__consultant__name'),
                company_name=F('lead__vendor__company__name'),
                marketer_name=F('lead__marketer__full_name'),
                location=F('lead__location')
            ).values('id', 'client', 'employer', 'status', 'created', 'modified', 'rate',
                     'company_name', 'consultant_name', 'marketer_name', 'location')

            return Response({"results": data, "counts": sub_data}, status=status.HTTP_200_OK)
        except Exception as error:
            return Response({"error": str(error)}, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request, *args, **kwargs):
        try:
            re = request.data
            sub = Submission.objects.create(
                lead_id=re['lead'],
                consultant_id=re['consultant'],
                client=re['client'],
                rate=re['rate'],
                employer=re['employer'],
                marketing_email=re['marketing_email'],
            )
            sub.lead.status = 'sub'
            sub.lead.save()
            content_type = ContentType.objects.get(model='submission')
            attachment = Attachment.objects.create(
                object_id=sub.id,
                content_type=content_type,
                attachment_type='resume',
                attachment_file=request.FILES.get('file'),
                creator=request.user
            )

            # print(attachment.attachment_file.path)
            serializer = self.serializer_class(sub)
            try:
                email_parsed = email_parser_from_file(attachment.attachment_file.path)
            except:
                email_parsed = 'not found'
            return Response({"result": serializer.data, 'email': email_parsed}, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": e}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        try:
            sub = Submission.objects.get(id=request.data.get("sub_id"))
            serializer = self.create_serializer_class(sub, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({"result": serializer.data}, status=status.HTTP_201_CREATED)
            return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as error:
            return Response({"error": str(error)}, status=status.HTTP_400_BAD_REQUEST)


class ScreeningView(RetrieveUpdateDestroyAPIView, CreateAPIView):
    serializer_class = ScreeningSerializer
    detail_serializer_class = ScreeningDetailSerializer
    create_serializer_class = ScreeningCreateSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        screening_id = request.query_params.get('screening_id', None)
        calendar_id = request.query_params.get('calendar_id', None)
        consultant_id = request.query_params.get('consultant_id', None)
        query = request.query_params.get('query', None)
        page = int(request.query_params.get('page', 1))
        last, first = page * 10, page * 10 - 10

        try:
            if calendar_id:
                screening = get_object_or_404(Screening, calendar_id=calendar_id)
                if request.user in [screening.submission.lead.marketer, screening.ctb] + list(screening.guest.all()):
                    serializer = self.detail_serializer_class(screening)
                else:
                    serializer = self.serializer_class(screening)

                return Response({"results": serializer.data}, status=status.HTTP_200_OK)
            elif screening_id:
                screening = get_object_or_404(Screening, id=screening_id)
                if request.user in [screening.submission.lead.marketer, screening.ctb] + list(screening.guest.all()):
                    serializer = self.detail_serializer_class(screening)
                else:
                    serializer = self.serializer_class(screening)

                return Response({"results": serializer.data}, status=status.HTTP_200_OK)

            elif query:
                if 'admin' in request.user.roles:
                    queryset = Screening.objects.filter(
                        (Q(submission__status='interview') &
                         Q(submission__lead__marketer__team=request.user.team)) &
                        (Q(submission__client__icontains=query) |
                         Q(submission__lead__vendor__company__name__icontains=query) |
                         Q(submission__consultant__consultant__name__icontains=query))
                    )
                else:
                    queryset = Screening.objects.filter(
                        (Q(submission__status='interview') &
                         Q(submission__lead__marketer=request.user)) & (
                                Q(submission__client__icontains=query) |
                                Q(submission__lead__vendor__company__name__icontains=query) |
                                Q(submission__consultant__consultant__name__icontains=query))
                    )

            elif consultant_id:
                queryset = Screening.objects.filter(submission__consultant__consultant__id=consultant_id,
                                                    submission__lead__marketer=request.user)

            else:
                if 'admin' in request.user.roles:
                    queryset = Screening.objects.filter(submission__lead__marketer__team=request.user.team,
                                                        submission__status='interview')
                else:
                    queryset = Screening.objects.filter(submission__lead__marketer=request.user,
                                                        submission__status='interview')

            total = queryset.count()

            scheduled = queryset.filter(status='scheduled').count()
            rescheduled = queryset.filter(status='rescheduled').count()
            failed = queryset.filter(status='failed').count()
            passed = queryset.filter(status='passed').count()
            cancelled = queryset.filter(status='cancelled').count()

            screen_data = {
                'total': total,
                'scheduled': scheduled,
                'rescheduled': rescheduled,
                'failed': failed,
                'passed': passed,
                'cancelled': cancelled
            }

            data = queryset[first:last].annotate(
                consultant_name=F('submission__consultant__consultant__name'),
                company_name=F('submission__lead__vendor__company__name'),
                marketer_name=F('submission__lead__marketer__full_name'),
                client=F('submission__client'),
                ctb_name=F('ctb__full_name')

            ).values('id', 'round', 'calendar_id', 'status', 'start_date', 'end_date', 'type', 'submission_id',
                     'ctb_name', 'marketer_name', 'consultant_name', 'client', 'company_name')

            return Response({"results": data, "count": screen_data}, status=status.HTTP_200_OK)
        except Exception as error:
            return Response({"error": str(error)}, status=status.HTTP_400_BAD_REQUEST)

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        submission_id = request.data['submission']
        try:
            sub = Screening.objects.filter(submission_id=submission_id).exclude(submission__status='cancelled'). \
                order_by('-created')
            serializer = self.create_serializer_class(data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                screening = Screening.objects.get(id=serializer.data['id'])
                if request.FILES.get('file', None):
                    content_type = ContentType.objects.get(model='screening')
                    Attachment.objects.create(
                        object_id=screening.id,
                        content_type=content_type,
                        attachment_type='misc',
                        attachment_file=request.FILES.get('file'),
                        creator=request.user
                    )
                if sub:
                    round_count = sub.first().round
                    screening.round = round_count + 1
                    screening.save()
                else:
                    sub = Submission.objects.get(id=int(serializer.data['submission']))
                    sub.status = 'interview'
                    sub.save()
                ctb = screening.ctb.email
                guest = [{"email": user.email} for user in screening.guest.all()]
                attendees = [
                                {'email': request.user.email},
                                {'email': ctb},
                                {'email': SCRUM_MASTER[request.user.team.name]}
                            ] + guest
                event = {
                    "start": serializer.data["start_date"],
                    "end": serializer.data["end_date"],
                    "attendees": attendees,
                    # "summary": request.data["summary"],
                    "description": request.data["description"],
                    "consultant": screening.submission.consultant.consultant,
                    "consultant_profile": screening.submission.consultant,
                    "submission": screening.submission,
                    "lead": screening.submission.lead,
                    "user": request.user
                }
                cal_res = {
                    'id': "error"
                }
                # try:
                #     cal_res = book_calendar(event)
                #     screening.calendar_id = cal_res['id']
                #     screening.save()
                # except Exception as error:
                #     return Response({"result": "Calendar event creation failed", "error": str(error)},
                #                     status=status.HTTP_400_BAD_REQUEST)

                t = date.today()
                if t == screening.start_date.date() and screening.type in ['video_call', 'telephonic']:
                    text = "CTB:{0} ::  Round:{1} :: {2} :: {3} :: {4} :: {5} :: {6}" \
                        .format(screening.ctb.full_name,
                                screening.round,
                                screening.get_type_display(),
                                screening.start_date.time(),
                                screening.consultant,
                                screening.submission.client,
                                screening.marketer)
                    content = "**Interview scheduled**"
                    discord_webhook(screening.team, content, text)

                return Response({"result": serializer.data, 'event_id': cal_res['id']}, status=status.HTTP_201_CREATED)
            return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as error:
            return Response({"error": str(error)}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        try:
            re = request.data
            start_date = re.get('start_date', None)
            end_date = re.get('end_date', None)
            screening = get_object_or_404(Screening, id=request.data.get("screening_id"))
            if start_date and end_date:
                if screening.start_date == re['start_date'] and screening.end_date == re['end_date']:
                    screening.status = 'rescheduled'
                    screening.save()
                    t = date.today()
                    if t == screening.start_date.date() and screening.type in ['video_call', 'telephonic']:
                        text = "CTB:{0} ::  Round:{1} :: {2} :: {3} :: {4} :: {5} :: {6}" \
                            .format(screening.ctb.full_name,
                                    screening.round,
                                    screening.get_type_display(),
                                    screening.start_date.time(),
                                    screening.consultant,
                                    screening.submission.client,
                                    screening.marketer)
                        content = "**Interview Updated**"
                        discord_webhook(screening.team, content, text)
            serializer = self.create_serializer_class(screening, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                ctb = screening.ctb.email
                guest = [{"email": user.email} for user in screening.guest.all()]
                attendees = [
                                {'email': request.user.email},
                                {'email': ctb},
                                {'email': SCRUM_MASTER[request.user.team.name]}
                            ] + guest

                event = {
                    "start": serializer.data["start_date"],
                    "end": serializer.data["end_date"],
                    "attendees": attendees,
                    # "summary": request.data["summary"],
                    "description": request.data["description"],
                }
                cal_res = {
                    'id': "error"
                }
                # try:
                #     cal_res = update_calendar(request.data.get("event_id"), event)
                # except Exception as error:
                #     return Response({"result": "Calendar event update failed", "error": str(error)},
                #                     status=status.HTTP_400_BAD_REQUEST)
                return Response({"result": serializer.data, "event_id": cal_res['id']}, status=status.HTTP_201_CREATED)
            return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as error:
            return Response({"error": str(error)}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        try:
            screening = get_object_or_404(Screening, id=request.data.get("screening_id"))
            if screening.round == 1:
                sub = Submission.objects.get(id=screening.submission.id)
                sub.status = 'sub'
                sub.save()
            screening.status = 'cancelled'
            screening.save()
            # try:
            #     delete_calendar_booking(request.data["event_id"])
            # except Exception as error:
            #     return Response({"result": "Calendar event deletion failed", "error": str(error)},
            #                     status=status.HTTP_202_ACCEPTED)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as error:
            return Response({"error": str(error)}, status=status.HTTP_400_BAD_REQUEST)


class CalendarInterviews(RetrieveUpdateDestroyAPIView):
    serializer_class = ScreeningSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        start = request.query_params.get('start', None)
        end = request.query_params.get('end', None)
        email = request.query_params.get('email', None)
        start_time = datetime.strptime(start, "%Y-%m-%d")
        end_time = datetime.strptime(end, "%Y-%m-%d")
        start_time = start_time.strftime("%Y-%m-%dT")
        end_time = end_time.strftime("%Y-%m-%dT")
        event = {
            "email": email,
            "start": start_time,
            "end": end_time
        }
        try:
            data, visibility = get_inteviews(event)
            return Response({"result": data, "visibility": visibility}, status=status.HTTP_200_OK)
        except Exception as error:
            return Response({"error": str(error)}, status=status.HTTP_400_BAD_REQUEST)


class Suggestions(RetrieveAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        t = request.query_params.get('type', None)
        page = int(request.query_params.get('page', 1))
        last, first = page * 10, page * 10 - 10

        try:
            if t == 'sub':
                client_name = request.query_params.get('client_name', None)
                con_name = request.query_params.get('con_name', None)
                lead_id = request.query_params.get('lead_id', None)
                lead = get_object_or_404(Lead, id=lead_id)
                if client_name:
                    queryset = Submission.objects.filter(
                        Q(consultant__consultant__name__icontains=con_name) &
                        Q(client__icontains=client_name)
                    )
                else:
                    queryset = Submission.objects.filter(
                        Q(consultant__consultant__name__icontains=con_name) &
                        Q(lead__vendor__company__name=lead.company)
                    )

                total = queryset.count()
                data = queryset[first:last].annotate(
                    consultant_name=F('consultant__consultant__name'),
                    marketer_name=F('lead__marketer__full_name'),
                    company_name=F('lead__vendor__company__name'),
                    job_title=F('lead__job_title'),
                    location=F('lead__location')

                ).values('id', 'client', 'consultant_name', 'created', 'marketer_name', 'company_name',
                         'status', 'job_title', 'location')

            else:
                sub_id = request.query_params.get('sub_id')
                sub = get_object_or_404(Submission, id=sub_id)
                queryset = Screening.objects.filter(
                    Q(submission__consultant__consultant=sub.consultant.consultant,
                      submission__client__contains=sub.client) |
                    Q(submission__consultant__consultant=sub.consultant.consultant,
                      submission__lead__vendor__company=sub.vendor) |
                    Q(submission__client__contains=sub.client)
                )
                total = queryset.count()
                data = queryset[first:last].annotate(
                    consultant_name=F('submission__consultant__consultant__name'),
                    company_name=F('submission__lead__vendor__company__name'),
                    marketer_name=F('submission__lead__marketer__full_name'),
                    client=F('submission__client'),
                    ctb_name=F('ctb__full_name')

                ).values('submission', 'ctb_name', 'round', 'feedback', 'type', 'marketer_name', 'consultant_name',
                         'start_date', 'end_date', 'company_name', 'client')

            return Response({"result": data, "total": total}, status=status.HTTP_200_OK)
        except Exception as error:
            return Response({"error": str(error)}, status=status.HTTP_400_BAD_REQUEST)
