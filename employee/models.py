from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.contrib.auth.models import BaseUserManager


GENDER_CHOICE = (
    ('male', 'Male'),
    ('female', 'Female')
)


class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, employee_id, email, name, team=None, gender=None, phone=None, password=None):
        """
            Create and save a user with the given username, email, and password.
        """
        if not email:
            raise ValueError('Users must have an email address')
        email = self.normalize_email(email)
        user = self.model(
            employee_id=int(employee_id),
            username=int(employee_id),
            email=email,
            team=team,
            full_name=name,
            gender=gender,
        )

        user.phone = phone
        user.set_password(password)
        user.is_active = True
        user.save()
        return user

    def create_superuser(self, employee_id, password):
        """
            Creates and saves a superuser with the given email and password.
        """
        user = self.create_user(
            employee_id,
            "admin@px.com",
            "Consultadd Admin",
            password=password
        )
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class Team(models.Model):
    name = models.CharField(max_length=50)
    address = models.CharField(max_length=300, blank=True)

    def __str__(self):
        return self.name


class Role(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name


class User(AbstractUser, PermissionsMixin):
    """
    Custom employee realization based on Django AbstractUser and PermissionMixin.
    """
    email = models.EmailField(_('Email'))
    employee_id = models.IntegerField(_('Employee ID'), unique=True)
    full_name = models.CharField(max_length=100, blank=True)
    avatar = models.ImageField(upload_to='avatar/', blank=True, null=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    gender = models.CharField(_('Gender'), choices=GENDER_CHOICE, max_length=10, null=True, blank=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)
    team = models.ForeignKey(Team, on_delete=models.PROTECT, related_name='employees', null=True, blank=True)
    role = models.ManyToManyField(Role, related_name='roles')

    objects = UserManager()

    USERNAME_FIELD = 'employee_id'
    REQUIRED_FIELDS = []

    class Meta:
        app_label = 'employee'

    def __str__(self):
        return self.email

    @property
    def roles(self):
        role_list = []
        for role in self.role.all():
            role_list.append(role.name)
        return role_list
