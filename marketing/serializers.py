from rest_framework import serializers
from .models import *
from consultant.serializers import UserSerializer, ConsultantProfileSerializer
from attachments.serializers import AttachmentSerializer

User = get_user_model()


class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = '__all__'


class VendorCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vendor
        fields = '__all__'


class VendorDetailSerializer(serializers.ModelSerializer):
    company = serializers.SerializerMethodField()

    class Meta:
        model = Vendor
        fields = '__all__'

    @staticmethod
    def get_company(self):
        return self.company.name


class VendorSerializer(serializers.ModelSerializer):
    company = serializers.SerializerMethodField()
    owner = UserSerializer(read_only=True)

    class Meta:
        model = Vendor
        fields = '__all__'

    @staticmethod
    def get_company(self):
        return self.company.name


class LeadCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lead
        fields = '__all__'


class LeadSerializer(serializers.ModelSerializer):
    vendor = serializers.SerializerMethodField()
    vendor_type = serializers.SerializerMethodField()
    marketer = serializers.SerializerMethodField()

    class Meta:
        model = Lead
        fields = (
            'id', 'job_desc', 'job_title', 'location', 'vendor_type', 'vendor', 'marketer', 'status', 'created',
            'modified')

    @staticmethod
    def get_vendor(self):
        return self.vendor.company.name

    @staticmethod
    def get_vendor_type(self):
        return 'private'

    @staticmethod
    def get_marketer(self):
        return self.marketer.full_name


class LeadDetailsSerializer(serializers.ModelSerializer):
    vendor = VendorDetailSerializer()
    vendor_type = serializers.SerializerMethodField()
    marketer = serializers.SerializerMethodField()

    class Meta:
        model = Lead
        fields = ('id', 'job_desc', 'job_title', 'location', 'vendor_type', 'vendor', 'marketer', 'status', 'created',
                  'modified')

    @staticmethod
    def get_vendor_type(self):
        return 'owner'

    @staticmethod
    def get_marketer(self):
        return self.marketer.full_name


class SubmissionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Submission
        fields = '__all__'


class SubmissionDetailSerializer(serializers.ModelSerializer):
    lead = LeadDetailsSerializer(read_only=True)
    consultant = ConsultantProfileSerializer(read_only=True)
    attachments = serializers.SerializerMethodField()

    class Meta:
        model = Submission
        fields = '__all__'

    @staticmethod
    def get_attachments(self):
        return AttachmentSerializer(self.attachments.all(), many=True).data


class SubmissionSerializer(serializers.ModelSerializer):
    lead = LeadSerializer(read_only=True)
    consultant = ConsultantProfileSerializer(read_only=True)
    attachments = serializers.SerializerMethodField()

    class Meta:
        model = Submission
        fields = '__all__'

    @staticmethod
    def get_attachments(self):
        return []


class ScreeningSerializer(serializers.ModelSerializer):
    submission = SubmissionSerializer()
    guest = UserSerializer(many=True)
    ctb = UserSerializer()

    class Meta:
        model = Screening
        fields = '__all__'


class ScreeningDetailSerializer(serializers.ModelSerializer):
    submission = SubmissionDetailSerializer()
    guest = UserSerializer(many=True)
    ctb = UserSerializer()

    class Meta:
        model = Screening
        fields = '__all__'


class ScreeningCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Screening
        fields = '__all__'


class ScreeningGetSerializer(serializers.ModelSerializer):
    guest = UserSerializer(many=True)
    ctb = UserSerializer()

    class Meta:
        model = Screening
        fields = '__all__'
