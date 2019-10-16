from rest_framework import status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from django.contrib.contenttypes.models import ContentType
from rest_framework.authentication import TokenAuthentication
from rest_framework.generics import CreateAPIView, RetrieveUpdateDestroyAPIView

from .serializers import *


class AttachmentView(RetrieveUpdateDestroyAPIView, CreateAPIView):
    serializer_class = AttachmentSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        object_id = self.request.query_params.get('object_id', None)
        obj_type = self.request.query_params.get("obj_type", None)
        attachment_type = self.request.query_params.get("type", None)
        try:
            obj_content_type = ContentType.objects.get(model=obj_type)
            queryset = Attachment.objects.filter(object_id=object_id, content_type=obj_content_type).order_by('-created')
            if attachment_type:
                queryset = queryset.filter(attachment_type=attachment_type)
            serializer = self.serializer_class(queryset, many=True)
            return Response({"results": serializer.data}, status=status.HTTP_200_OK)
        except Exception as error:
            return Response({"error": str(error)}, status=status.HTTP_400_BAD_REQUEST)

    def create(self, request, *args, **kwargs):
        re = request.data
        try:
            content_type = ContentType.objects.get(model=re['obj_type'])
            object_id = re['object_id']
            attachment = Attachment.objects.create(
                object_id=object_id,
                content_type=content_type,
                attachment_type=re['attachment_type'],
                attachment_file=request.FILES.get('file'),
                creator=request.user
            )

            serializer = self.serializer_class(attachment)
            return Response({"results": serializer.data}, status=status.HTTP_201_CREATED)
        except Exception as error:
            return Response({"error": str(error)}, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        try:
            attachment = get_object_or_404(Attachment, id=request.data.get('id'))
            attachment.attachment_file = request.FILES.get('file')
            attachment.save()
            serializer = self.serializer_class(attachment)
            return Response({"results": serializer.data}, status=status.HTTP_202_ACCEPTED)
        except Exception as error:
            return Response({"error": str(error)}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        try:
            attachment_id = self.request.query_params.get('attachment_id', None)
            attachment = get_object_or_404(Attachment, id=attachment_id)
            attachment.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as error:
            return Response({"error": str(error)}, status=status.HTTP_400_BAD_REQUEST)
