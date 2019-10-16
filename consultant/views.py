from django.db.models import Q, Count
from django.db import transaction
from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.generics import CreateAPIView, RetrieveUpdateDestroyAPIView

from utils_app.mailing import send_email
from utils_app.calendar_api import SCRUM_MASTER
from .serializers import *
from datetime import datetime


class ConsultantView(RetrieveUpdateDestroyAPIView, CreateAPIView):
    serializer_class = ConsultantSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        query = request.query_params.get('query', None)
        consultant_id = request.query_params.get('consultant_id', None)
        page = int(request.query_params.get("page", 1))
        last, first = page * 10, page * 10 - 10

        try:
            if consultant_id:
                consultant = get_object_or_404(Consultant, id=request.query_params.get('consultant_id'))
                serializer = self.serializer_class(consultant)
                return Response({"results": serializer.data}, status=status.HTTP_200_OK)

            elif query:
                consultants = Consultant.objects.filter(name__icontains=request.query_params.get('query'))[first:last]

            else:
                consultants = Consultant.objects.filter(
                    (Q(status='in_marketing', team__name='open') & ~Q(marketer=request.user)) |
                    Q(status='in_marketing', marketer=request.user))[first:last]
            serializer = self.serializer_class(consultants, many=True)
            return Response({"results": serializer.data}, status=status.HTTP_200_OK)
        except Exception as error:
            return Response({"error": str(error)}, status=status.HTTP_400_BAD_REQUEST)

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        re = request.data
        consultant = Consultant.objects.filter(email__iexact=re['email'])
        if consultant:
            try:

                dob = datetime.strptime(re["dob"], "%Y-%m-%d") if re['dob'] != 'None' and re['dob'] else None
                visa_start = datetime.strptime(re["visa_start"], "%Y-%m-%d") if re['visa_start'] != 'None' and re[
                    'visa_start'] else None
                visa_end = datetime.strptime(re["visa_end"], "%Y-%m-%d") if re['visa_end'] != 'None' and re[
                    'visa_end'] else None

                consultant = consultant[0]
                consultant.name = re['name']
                consultant.email = re['email']
                consultant.rate = re['rate']
                consultant.skills = ", ".join(i for i in re['skills']) if len(re['skills']) > 0 else None
                consultant.ssn = re['ssn']
                consultant.gender = re['gender']
                consultant.rtg = True if re['rtg'] == "RTG" else False
                consultant.status = 'in_marketing'
                consultant.save()

                consultant_profile = ConsultantProfile.objects.get(consultant=consultant, is_original=True)
                consultant_profile.title = "original"
                consultant_profile.dob = dob
                consultant_profile.location = ", ".join(i for i in re['location']) if len(re['location']) > 0 else None
                consultant_profile.education = re['education']
                consultant_profile.visa_type = re['visa_type']
                consultant_profile.visa_start = visa_start
                consultant_profile.visa_end = visa_end
                consultant_profile.save()

                for i in re["attachment"]:
                    File.objects.create(
                        name=i["title"],
                        path=i["attached_file"],
                        consultant=consultant)

            except Exception as error:
                return Response({"error": str(error)}, status=status.HTTP_400_BAD_REQUEST)

            return Response({"result": "Updated"}, status=status.HTTP_202_ACCEPTED)
        try:
            recruiter = get_object_or_404(User, email=re['recruiter'])

            dob = datetime.strptime(re["dob"], "%Y-%m-%d") if re['dob'] != 'None' and re['dob'] else None
            visa_start = datetime.strptime(re["visa_start"], "%Y-%m-%d") if re['visa_start'] != 'None' and re[
                'visa_start'] else None
            visa_end = datetime.strptime(re["visa_end"], "%Y-%m-%d") if re['visa_end'] != 'None' and re[
                'visa_end'] else None

            consultant = Consultant.objects.create(
                name=re['name'],
                email=re['email'],
                recruiter=recruiter,
                rate=re['rate'],
                skills=", ".join(i for i in re['skills']) if len(re['skills']) > 0 else None,
                ssn=re['ssn'],
                gender=re['gender'],
                team=recruiter.team,
                rtg=True if re['rtg'] == "RTG" else False,
                status='in_marketing',
            )

            ConsultantProfile.objects.create(
                consultant=consultant,
                is_original=True,
                title="Original",
                owner=recruiter,
                dob=dob,
                location=", ".join(i for i in re['location']) if len(re['location']) > 0 else None,
                education=re['education'],
                visa_type=re['visa_type'],
                visa_start=visa_start,
                visa_end=visa_end
            )

            for i in re["attachment"]:
                File.objects.create(
                    name=i["title"],
                    path=i["attached_file"],
                    consultant=consultant)

            return Response({"result": "success"}, status=status.HTTP_201_CREATED)
        except Exception as error:
            return Response({"error": str(error)}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        try:
            consultant = Consultant.objects.filter(email__iexact=request.data.get('email'))
            if consultant:
                consultant = consultant[0]
                consultant.status = 'archived'
                consultant.save()
                return Response({"results": "Updated"}, status=status.HTTP_202_ACCEPTED)
            return Response({"results": "Not found"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as error:
            return Response({"error": str(error)}, status=status.HTTP_400_BAD_REQUEST)


class ConsultantBenchView(RetrieveUpdateDestroyAPIView):
    serializer_class = ConsultantSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        team = request.query_params.get('team', None)
        query = request.query_params.get('query', None)
        map_view = request.query_params.get("map", None)
        location = request.query_params.get('location', None)
        search_type = request.query_params.get('type', 'all')
        page = int(request.query_params.get("page", 1))
        last, first = page * 10, page * 10 - 10

        try:
            if map_view:
                consultants = ConsultantProfile.objects.filter(is_original=True).values('location').annotate(
                    total=Count('location')).order_by('total')
                return Response({"results": consultants}, status=status.HTTP_200_OK)

            elif team:
                if team == 'all':
                    consultants = Consultant.objects.filter(status='in_marketing')
                else:
                    consultants = Consultant.objects.filter(status='in_marketing', team__name=team)

            elif location:
                consultants = Consultant.objects.filter(profiles__location__icontains=location,
                                                        profiles__is_original=True)[first:last]

            elif query:
                if search_type == 'name':
                    consultants = Consultant.objects.filter(name__icontains=query)
                elif search_type == 'recruiter':
                    consultants = Consultant.objects.filter(recruiter__full_name__icontains=query)
                elif search_type == 'location':
                    consultants = Consultant.objects.filter(profiles__location__icontains=query)
                elif search_type == 'email':
                    consultants = Consultant.objects.filter(email__istartswith=query)
                else:
                    consultants = Consultant.objects.filter(
                        Q(name__icontains=query) |
                        Q(email__istartswith=query) |
                        Q(recruiter__full_name__istartswith=query) |
                        Q(skills__istartswith=query) |
                        Q(profiles__location__icontains=query)
                    )
            else:
                consultants = Consultant.objects.filter(status='in_marketing', team__in=[request.user.team.name, 'open'])

            total = consultants.count()
            serializer = self.serializer_class(consultants[first:last], many=True)
            return Response({"results": serializer.data, "total": total}, status=status.HTTP_200_OK)
        except Exception as error:
            return Response({"error": str(error)}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        consultant_id = request.data.get('consultant')
        consultant = get_object_or_404(Consultant, id=consultant_id)
        roles = request.user.roles
        if 'superadmin' not in roles and ('admin' not in roles or consultant.team != request.user.team):
            return Response({"error": "dont have access"}, status=status.HTTP_400_BAD_REQUEST)
        team = request.data.get('team', None)
        if team:
            consultant.team = get_object_or_404(Team, name=team)
            consultant.save()
            return Response({"results": "changed"}, status=status.HTTP_200_OK)
        marketer = get_object_or_404(User, id=request.data.get('marketer'))
        if marketer.employee_id in consultant.marketer.all().values_list('employee_id', flat=True):
            return Response({"result": "Marketer already assigned to this consultant"}, status=406)

        consultant.marketer.add(marketer)
        consultant.modified = timezone.now()
        consultant.save()
        serializer = self.serializer_class(consultant)

        if consultant.team == 'open':
            scrum_master = [SCRUM_MASTER[marketer.team.name], marketer.email]
        else:
            scrum_master = [SCRUM_MASTER[consultant.team.name], marketer.email]

        try:
            subject = "Consultant Assignment"
            template = '../templates/po_created.html'
            mail_data = {
                'subject': subject,
                'to': scrum_master,
                'template': template,
                'context': {
                    'name': 'Ayushi Mundra',
                    'con': 'Ayushi Mundra',
                    'con_email': 'sarang.m@consultadd.in',
                    'vendor': 'Vendor',
                    'vendorContact': 'VendorContact',
                    'client': 'Client',
                    'clientContact': 'ClientContact',
                    'comp': 'Ayushi',
                    'type': 'type',
                    'start': "",
                    'rate': 90,
                    'net_term': 5,
                    'invoicing_term': 30,
                    'con_rate': 90,
                    'sub_title': 'Title',
                    'reporting_details': 'Ayushi Mundra'
                }

            }
            # send_email(mail_data)
        except Exception as error:
            return Response({"error": str(error)}, status=status.HTTP_200_OK)
        return Response({"results": serializer.data}, status=status.HTTP_200_OK)

    def delete(self, request, *args, **kwargs):
        consultant_id = request.query_params.get('consultant', None)
        consultant = get_object_or_404(Consultant, id=consultant_id)
        roles = request.user.roles
        if 'superadmin' not in roles and ('admin' not in roles or consultant.team != request.user.team):
            return Response({"error": "dont have access"}, status=status.HTTP_400_BAD_REQUEST)
        marketer_id = request.query_params.get('marketer', None)
        try:
            marketer = get_object_or_404(User, id=marketer_id)
            if marketer.employee_id not in consultant.marketer.all().values_list('employee_id', flat=True):
                return Response({"results": "Marketer already removed from this consultant"}, status=406)
            consultant.marketer.remove(marketer)
            serializer = self.serializer_class(consultant)
            return Response({"results": serializer.data}, status=status.HTTP_200_OK)
        except Exception as error:
            return Response({"error": str(error)}, status=status.HTTP_400_BAD_REQUEST)


class ConsultantProfileView(RetrieveUpdateDestroyAPIView, CreateAPIView):
    serializer_class = ConsultantProfileSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        try:
            profile_id = request.query_params.get("profile_id", None)
            profile = get_object_or_404(ConsultantProfile, id=profile_id)
            serializer = self.serializer_class(profile)
            return Response({"result": serializer.data}, status=status.HTTP_200_OK)
        except Exception as error:
            return Response({"error": str(error)}, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request, *args, **kwargs):
        re = request.data
        try:
            title = request.data.get('title').strip()
            if len(title) == 0:
                title = "{} :: {} :: {}".format(re['dob'], re["location"], re["education"])
            con_profile = ConsultantProfile(
                consultant_id=re['consultant'],
                title=title,
                owner=request.user,
                is_original=False
            )
            serializer = self.serializer_class(con_profile, data=re)
            serializer.is_valid(raise_exception=400)
            serializer.save()
            return Response({"result": serializer.data}, status=status.HTTP_201_CREATED)
        except Exception as error:
            return Response({"error": str(error)}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        try:
            con_profile = ConsultantProfile.objects.get(id=request.data.get('id'))
            serializer = self.serializer_class(con_profile, data=request.data)
            return Response({"result": serializer.data}, status=status.HTTP_202_ACCEPTED)
        except Exception as error:
            return Response({"error": str(error)}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        try:
            con_profile = ConsultantProfile.objects.get(id=request.data.get('con_profile'))
            con_profile.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as error:
            return Response({"error": str(error)}, status=status.HTTP_400_BAD_REQUEST)


class FileView(CreateAPIView):
    serializer_class = FileSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        try:
            email = request.data.get('email')
            attachment = request.data.get('attachment')
            if email:
                consultant = get_object_or_404(Consultant, email=email)
                file = File.objects.create(
                    name=attachment["title"],
                    path=attachment["attached_file"],
                    consultant=consultant
                )
                serializer = self.serializer_class(file)
                return Response({"result": serializer.data}, status=status.HTTP_201_CREATED)
            return Response({"result": "Consultant not found"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as error:
            return Response({"error": str(error)}, status=status.HTTP_400_BAD_REQUEST)
