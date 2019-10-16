from rest_framework import serializers
from .models import Project
from marketing.serializers import SubmissionSerializer, ScreeningGetSerializer
from attachments.serializers import AttachmentSerializer


class ProjectCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = '__all__'


class ProjectSerializer(serializers.ModelSerializer):
    submission = SubmissionSerializer()
    attachments = serializers.SerializerMethodField()
    interview = serializers.SerializerMethodField()
    check_list = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = '__all__'

    @staticmethod
    def get_attachments(self):
        return AttachmentSerializer(self.attachments.all(), many=True).data

    @staticmethod
    def get_interview(self):
        return ScreeningGetSerializer(self.submission.screening.all(), many=True).data

    @staticmethod
    def get_check_list(self):
        msa = self.attachments.filter(attachment_type='msa').count()
        work_order = self.attachments.filter(attachment_type='work_order').count()
        both = self.attachments.filter(attachment_type='work_order_msa').count()
        return {"msa": msa, "work_order": work_order, "both": both}
