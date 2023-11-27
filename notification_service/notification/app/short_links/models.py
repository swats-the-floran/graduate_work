import datetime
from random import choice
from string import ascii_letters, digits

from django.conf import settings
from django.db import models
from django.utils import timezone


SHORT_LINK_SIZE = getattr(settings, 'SHORT_LINK_SIZE', 7)


class Link(models.Model):
    short_link = models.CharField(max_length=10, unique=True, blank=True)
    valid_to = models.DateTimeField(editable=False)
    redirect_url = models.URLField(default=getattr(settings, 'REDIRECT_AFTER_ACTIVATION', 'http://example.com'))
    user_id = models.CharField(max_length=50, blank=True)
    used = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.short_link} valid to {self.valid_to}'

    def save(self, *args, **kwargs):
        """
        Overwritten method adds short_link and valid_to
        """
        if not self.valid_to:
            self.valid_to = timezone.now() + datetime.timedelta(days=1)
        if not self.short_link:
            self.short_link = self._generate_short_link()
        super().save(*args, **kwargs)

    def _generate_short_link(self):
        """
        Generates unique short link
        """
        model_class = self.__class__

        code = self._create_random_code()

        if model_class.objects.filter(short_link=code).exists():
            return self._generate_short_link()
        return code

    @staticmethod
    def _create_random_code(size=SHORT_LINK_SIZE):
        """
        Creates a random string
        """
        available_chars = ascii_letters + digits
        return "".join(
            [choice(available_chars) for _ in range(size)] # noqa
        )

    @classmethod
    def create_new(cls, user_id):
        link = cls.objects.create(user_id=user_id)
        return link.short_link
