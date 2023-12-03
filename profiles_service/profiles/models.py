from datetime import date

from django.db import models

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db.models.fields import uuid
from django.utils.translation import gettext_lazy as _


class UUIDMixin(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


# class CustomUserManager(BaseUserManager):
#     def create_user(self, email, password=None, **extra_fields):
#         if not email:
#             raise ValueError('Users must have an email address')
#         user = self.model(email=self.normalize_email(email), **extra_fields)
#         user.set_password(password)
#         user.save(using=self._db)
#         return user


class Person(UUIDMixin, AbstractBaseUser):
    class GenderChoices(models.TextChoices):
        MALE = 'M', _('Мужской')
        FEMALE = 'F', _('Женский')

    email = models.EmailField(max_length=255, unique=True, verbose_name=_("EMAIL"))
    first_name = models.CharField(max_length=50, null=True, blank=True, verbose_name=_("Имя"))
    last_name = models.CharField(max_length=50, null=True, blank=True, verbose_name=_("Фамилия"))
    date_of_birth = models.DateField(null=True, blank=True, verbose_name=_("Дата рождения"))
    profile_image = models.ImageField(upload_to='profile_images/', null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GenderChoices.choices, null=True, blank=True)
    is_active = models.BooleanField(default=True, verbose_name=_("Активен"))

    # objects = CustomUserManager()

    USERNAME_FIELD = 'email'

    class Meta:
        verbose_name = _("Пользователь")
        verbose_name_plural = _("Пользователи")
        db_table = 'client'
        ordering = ['last_name', 'first_name']

    @property
    def short_full_name(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name[0]}."
        return self.email

    @property
    def age(self) -> int | None:
        if self.date_of_birth:
            today = date.today()
            return today.year - self.date_of_birth.year - (
                    (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
            )
        return None

    @property
    def gender_display(self):
        return self.gender
