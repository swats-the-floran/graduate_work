from datetime import date

from django.db import models

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db.models.fields import uuid
from django.utils.translation import gettext_lazy as _


class UUIDMixin(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class TimeStampedMixin(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class CustomPersonManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Users must have an email address')
        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.save(using=self._db)
        return user


class Person(UUIDMixin, TimeStampedMixin, AbstractBaseUser):
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

    objects = CustomPersonManager()

    USERNAME_FIELD = 'email'

    class Meta:
        verbose_name = _("Пользователь")
        verbose_name_plural = _("Пользователи")
        db_table = 'content"."person'
        ordering = ['last_name', 'first_name']

    def delete(self):
        self.is_active = False
        self.save()

    def delete_completely(self, using=None, keep_parents=False):
        return super().delete(using, keep_parents)

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


class Film(UUIDMixin):
    name = models.CharField(max_length=1024, verbose_name=_("Название"))


class Bookmark(TimeStampedMixin):
    timecode = models.IntegerField(_("Время"), blank=True, null=True)
    comment = models.TextField(_("Комментарий"), blank=True, null=True)
    person = models.ForeignKey(Person, related_name="bookmarks", on_delete=models.DO_NOTHING)
    film = models.ForeignKey(Film, related_name="bookmarks", on_delete=models.DO_NOTHING)

    def __str__(self):
        return f'{self.person} - {self.film} - {self.comment}'

    class Meta:
        db_table = 'content"."bookmark'
        verbose_name = _("Закладка")
        verbose_name_plural = _("Закладки")

        constraints = [models.UniqueConstraint(fields=["film", "timecode", "person"], name="film_timecode_person_idx")]


class Favorite(TimeStampedMixin):
    person = models.ForeignKey(Person, related_name='favorites', on_delete=models.DO_NOTHING)
    film = models.ForeignKey(Film, related_name="favorites", on_delete=models.DO_NOTHING)

    def __str__(self):
        return f'{self.person} - {self.film}'

    class Meta:
        db_table = 'content"."favorite'
        verbose_name = _("Любимый фильм")
        verbose_name_plural = _("Любимые фильмы")

        constraints = [models.UniqueConstraint(fields=["film", "person"], name="film_person_idx")]


class FilmReview(UUIDMixin, TimeStampedMixin):
    review_text = models.TextField(_("Текст"))
    score = models.IntegerField(_("Оценка"))
    person = models.ForeignKey(Person, related_name='film_reviews', on_delete=models.CASCADE)
    film = models.ForeignKey(Film, related_name="film_reviews", on_delete=models.DO_NOTHING)

    class Meta:
        db_table = 'content"."film_review'
        verbose_name = _("Рецензия")
        verbose_name_plural = _("Рецензии")

        constraints = [models.UniqueConstraint(fields=["film", "person"], name="films_persons_idx")]

