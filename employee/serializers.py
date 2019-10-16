from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
from .models import Team, Role

User = get_user_model()


class TeamSerializer(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ('name',)


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ('name',)


class UserSerializer(serializers.ModelSerializer):
    team = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'employee_id', 'email', 'full_name', 'avatar', 'team', 'roles', 'gender', 'phone', 'is_staff')

    @staticmethod
    def get_team(self):
        return self.team.name


# Login
class UserSerializerLogin(UserSerializer):
    token = serializers.SerializerMethodField()
    team = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'employee_id', 'full_name', 'email', 'token', 'avatar', 'team', 'roles')

    @staticmethod
    def get_token(user):
        token, created = Token.objects.get_or_create(user=user)
        return token.key

    @staticmethod
    def get_team(self):
        return self.team.name


class UserSearchSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='full_name')

    class Meta:
        model = User
        fields = ('id', 'name', 'email', 'roles')
