from rest_framework import serializers
from .models import *
from employee.serializers import UserSerializer

User = get_user_model()


class ConsultantProfileSerializer(serializers.ModelSerializer):
    owner = serializers.SerializerMethodField()

    @staticmethod
    def get_owner(self):
        return self.owner.full_name

    class Meta:
        model = ConsultantProfile
        fields = '__all__'


class FileSerializer(serializers.ModelSerializer):
    consultant = serializers.SerializerMethodField()

    @staticmethod
    def get_consultant(self):
        return self.consultant.name

    class Meta:
        model = File
        fields = '__all__'


class ConsultantSerializer(serializers.ModelSerializer):
    recruiter = UserSerializer()
    marketer = UserSerializer(many=True)
    profiles = serializers.SerializerMethodField()
    attachments = serializers.SerializerMethodField()
    team = serializers.SerializerMethodField()

    @staticmethod
    def get_attachments(self):
        return FileSerializer(self.files.all(), many=True).data

    @staticmethod
    def get_team(self):
        return self.team.name

    @staticmethod
    def get_profiles(self):
        return ConsultantProfileSerializer(self.profiles.all(), many=True).data

    class Meta:
        model = Consultant
        fields = ('id', 'name', 'team', 'email', 'rate', 'skills', 'ssn', 'rtg', 'gender', 'created', 'recruiter',
                  'modified', 'marketer', 'attachments', 'profiles', 'status')

