from django.db.models import Q, F
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView, RetrieveUpdateDestroyAPIView
from django.shortcuts import get_object_or_404
from django.db import transaction
from .serializers import *
from marketing.models import Submission
from django.contrib.contenttypes.models import ContentType
from attachments.models import Attachment
from utils_app.mailing import send_email_attachment_multiple
from marketing.views import discord_webhook


class ProjectView(RetrieveUpdateDestroyAPIView, CreateAPIView):
    serializer_class = ProjectSerializer
    create_serializer_class = ProjectCreateSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    @staticmethod
    def mail(self, request, submission, po_type):
        try:
            mail_data = {
                'to': ['sarang.m@consultadd.in'],
                'subject': 'Offer letter',
                'template': 'po_created.html',
                'context': {
                    'marketer_name': submission.marketer,
                    'consultant_name': submission.consultant.consultant.name,
                    'consultant_email': submission.consultant.consultant.email,
                    'vendor_name': submission.lead.vendor.name,
                    'vendor_email': submission.lead.vendor.email,
                    'vendor_number': submission.lead.vendor.number,
                    'client_name': submission.client,
                    'client_address': self.location + self.city,
                    'type': po_type,
                    'start': request['start_time'],
                    'rate': submission.rate,
                    'payment_term': '',
                    'invoicing_period': '',
                    'con_rate': int(submission.consultant.consultant.rate),
                    'job_title': submission.lead.job_title,
                    'employer': submission.employer,
                }
            }
            # send_email_attachment_multiple(mail_data)
            return mail_data
        except Exception as error:
            return Response({"error": str(error)}, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, *args, **kwargs):
        project_id = request.query_params.get('project_id', None)
        query = request.query_params.get('query', None)
        page = int(request.query_params.get("page", 1))
        last, first = page * 10, page * 10 - 10

        try:
            if project_id:
                project = get_object_or_404(Project, id=project_id)
                serializer = self.serializer_class(project)
                return Response({"result": serializer.data}, status=status.HTTP_200_OK)

            elif query:
                project = Project.objects.filter(
                    Q(submission__lead__marketer=request.user) & (
                            Q(submission__consultant__consultant__name__istartswith=query) |
                            Q(submission__client__istartswith=query)
                    )
                )

            else:
                project = Project.objects.filter(submission__lead__marketer__team=request.user.team)

            total = project.count()
            joined = project.filter(status='joined').count()
            not_joined = project.filter(status='not_joined').count()
            extended = project.filter(status='extended').count()

            data_count = {
                'total': total,
                'joined': joined,
                'not_joined': not_joined,
                'extended': extended
            }

            data = project[first:last].annotate(
                consultant_name=F('submission__consultant__consultant__name'),
                company_name=F('submission__lead__vendor__company__name'),
                marketer_name=F('submission__lead__marketer__full_name'),
                client=F('submission__client'),
                rate=F('submission__rate'),
            ).values('id', 'client', 'rate', 'consultant_name', 'marketer_name', 'company_name')

            return Response({"results": data, "counts": data_count}, status=status.HTTP_200_OK)
        except Exception as error:
            return Response({"error": str(error)}, status=status.HTTP_400_BAD_REQUEST)

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        sub_id = request.data.get('submission')
        try:
            sub = get_object_or_404(Submission, id=sub_id)
            if sub.status == 'project':
                return Response({"error": "Project already exist"}, status=status.HTTP_406_NOT_ACCEPTABLE)
            serializer = self.create_serializer_class(data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                content_type = ContentType.objects.get(model='project')
                # file = request.FILES.get('file', None)
                # if file:
                #     Attachment.objects.create(
                #         object_id=serializer['id'],
                #         content_type=content_type,
                #         attachment_type=request.data['attachment_type'],
                #         attachment_file=file,
                #         creator=request.user
                #     )
                project = Project.objects.get(id=serializer.data['id'])
                sub.status = 'project'
                sub.consultant.consultant.status = 'on_project'
                sub.save()
                text = "**Employer -\t {0} \nMarketer Name - {1} \nConsultant Name - {2} \nClient - \t{3} \n" \
                       "Technology Role - {4} \nLocation - \t{5} \nStart Date - \t{6} \n"\
                    .format(project.team, project.marketer, project.consultant, project.submission.client,
                            project.submission.lead.job_title, project.city, str(project.start_time.date()))
                content = "**Offer**"
                discord_webhook(project.team, content, text)
                # self.mail(serializer.data, sub, 'created')
                return Response({"result": serializer.data}, status=status.HTTP_201_CREATED)
            return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as error:
            return Response({"error": str(error)}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        try:
            project = get_object_or_404(Project, id=request.data.get("project_id"))
            serializer = self.create_serializer_class(project, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                sub = get_object_or_404(Submission, id=serializer.data["submission"])
                self.mail(serializer.data, sub, 'updated')
                return Response({"result": serializer.data}, status=status.HTTP_201_CREATED)
            return Response({"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as error:
            return Response({"error": str(error)}, status=status.HTTP_400_BAD_REQUEST)
