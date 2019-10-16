from rest_framework.response import Response
from rest_framework.generics import CreateAPIView
from .extraction import extraction
from rest_framework import status


class JobAndSkillExtraction(CreateAPIView):

    def create(self, request, *args, **kwargs):
        jd = request.data.get('jd', None)
        if jd:
            skills_and_jobs = extraction(jd)
            return Response({"results": skills_and_jobs}, status=status.HTTP_200_OK)
        else:
            return Response({"results": "JD is empty"}, status=status.HTTP_400_BAD_REQUEST)
