from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from rest_framework.generics import RetrieveAPIView, CreateAPIView, RetrieveUpdateDestroyAPIView, ListAPIView
from rest_framework.exceptions import ValidationError

from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404
from .serializers import *

User = get_user_model()


# Signup
class RegisterView(CreateAPIView):
    serializer_class = UserSerializer
    authentication_classes = ()
    permission_classes = (AllowAny,)

    def create(self, request, *args, **kwargs):
        employee_id = request.data.get('employee_id')
        role = request.data.get('role').split(',') if request.data.get('role') else None
        email = request.data.get('email')
        name = request.data.get('name')
        phone = request.data.get('phone')
        gender = request.data.get('gender')
        password = request.data.get('password').strip()
        team = Team.objects.get(name=request.data.get('team'))
        user = User.objects.filter(employee_id=int(employee_id)).first()
        if user:
            user.email = email
            user.name = name
            user.phone = phone
            user.gender = gender
            user.save()
            for i in role:
                r = Role.objects.get(id=int(i))
                user.role.add(r)
            return Response({'result': 'user Updated'}, status=status.HTTP_400_BAD_REQUEST)
        user = User.objects.create_user(employee_id, email, name, team, gender, phone, password)
        for i in role:
            r = Role.objects.get(id=int(i))
            user.role.add(r)
        try:
            return Response({"result": self.serializer_class(user).data}, status=status.HTTP_201_CREATED)
        except ValidationError as error:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)


# Login
class LoginView(CreateAPIView):
    serializer_class = UserSerializerLogin
    authentication_classes = ()
    permission_classes = (AllowAny,)

    def create(self, request, *args, **kwargs):
        """
            Normal Login
            :param request, email, password
        """
        employee_id = request.data.get('employee_id')
        if employee_id:
            user = get_object_or_404(User, employee_id=employee_id)
        else:
            return Response({"error": "Employee Id is Empty"}, status=status.HTTP_400_BAD_REQUEST)
        user = authenticate(employee_id=user.employee_id, password=request.data.get('password').strip())
        if user:
            return Response({"result": self.serializer_class(user).data}, status=status.HTTP_202_ACCEPTED)
        return Response({"error": "Incorrect email/password"}, status=status.HTTP_400_BAD_REQUEST)


# logout
class LogoutView(RetrieveAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def retrieve(self, request, *args, **kwargs):
        """
            LogOut for authenticated user
        """
        token = get_object_or_404(Token, key=request.auth)
        token.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class Profile(RetrieveUpdateDestroyAPIView):
    serializer_class = UserSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        user_id = request.query_params.get('id', None)
        if user_id:
            user = get_object_or_404(User, id=user_id)
        else:
            user = request.user
        serializer = self.serializer_class(user)
        return Response({"results": serializer.data}, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"result": serializer.data}, status=status.HTTP_200_OK)
        return Response({"error": "Invalid data"}, status=status.HTTP_400_BAD_REQUEST)


class UserList(ListAPIView):
    serializer_class = UserSearchSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        query = request.query_params.get('query', None)
        t = request.query_params.get('type', None)
        if t == 'interview':
            users = User.objects.filter(role__name='interviewee')
        elif t == 'team':
            users = User.objects.filter(team=request.user.team, role__name='marketer')
        else:
            if query and len(query) == 0:
                return Response({"results": []}, status=status.HTTP_200_OK)
            users = User.objects.filter(full_name__icontains=query)
        serializer = self.serializer_class(users, many=True)
        return Response({"results": serializer.data}, status=status.HTTP_200_OK)


class TeamView(ListAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        teams = Team.objects.all().values('id', 'name', 'address')
        return Response({"results": teams}, status=status.HTTP_200_OK)


class UpdatePassword(CreateAPIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        current_password = request.data.get('cur_password')
        new_password = request.data.get('new_password')
        if request.user.check_password(current_password):
            request.user.set_password(new_password)
            request.user.save()
            return Response({"result": "password updated"}, status=status.HTTP_200_OK)
