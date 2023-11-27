import uuid

from django.core.exceptions import ValidationError
from django.core.serializers.json import DjangoJSONEncoder
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import JSONField


class NotificationStages(models.TextChoices):
    new = ('new', 'new')
    failed = ('failed', 'failed')
    success = ('success', 'success')


class NotificationTypes(models.TextChoices):
    assignment = ('assignment', 'assignment')
    delayed = ('delayed', 'delayed')
    birthday = ('birthday', 'birthday')
    like = ('like', 'like')
    mass_mail = ('mass_mail', 'mass_mail')
    welcome = ('welcome', 'welcome')
    new_movie = ('new_movie', 'new_movie')


class SexOptions(models.TextChoices):
    MALE = ('M', ' Мужчины')
    FEMALE = ('F', 'Женщины')
    BOTH = ('FM', 'Всем')


class TransportTypes(models.TextChoices):
    email = ('email', 'email')
    sms = ('sms', 'sms')


class NotificationLogNewManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(stage=NotificationStages.new).exclude(locked=True)


class NotificationLog(models.Model):
    """
    Класс логов уведомления
    """

    notification_data = JSONField(encoder=DjangoJSONEncoder, blank=True, default=dict)
    guid = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    locked = models.BooleanField(default=False, null=True, blank=True)
    stage = models.CharField('Stage',
                             max_length=20,
                             choices=NotificationStages.choices,
                             default=NotificationStages.new, blank=True)
    stages_data = JSONField(encoder=DjangoJSONEncoder, blank=True, default=dict)
    notification_type = models.CharField('notification_type',
                                         max_length=20,
                                         choices=NotificationTypes.choices,
                                         default='', blank=True)
    send_tries = models.IntegerField(default=0)

    transport = models.CharField('transport', max_length=20, choices=TransportTypes.choices,
                                 default=TransportTypes.email, blank=True)

    # managers
    objects = models.Manager()
    new = NotificationLogNewManager()

    def __str__(self):
        return f'{self.guid}: {self.notification_type}'

    @classmethod
    def get_object(cls, guid):
        try:
            return cls.objects.get(guid=guid)
        except cls.DoesNotExist:
            return None

    def unlock(self):
        self.locked = False
        self.save(update_fields=['locked'])

    @classmethod
    def create_by_type(cls, nl_type, data):
        values = dict(notification_type=nl_type, notification_data=data)
        return cls.objects.create(**values)

    def change_stage(self, new_stage, save=True):
        self.stage = new_stage
        if save:
            self.save(update_fields=['stage'])

    def log_error(self, error):
        if not self.stages_data.get('error'):
            self.stages_data['error'] = []
            self.stages_data['error'].append(str(error))
        self.save()

    def log_success(self, message, save=True):
        if not self.stages_data.get('success'):
            self.stages_data['success'] = []
            self.stages_data['success'].append(str(message))
        if save:
            self.save()


class Assignment(models.Model):
    """Модель для создания и последующей отправки сообщений из панели администрирования."""
    guid = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    from_age = models.SmallIntegerField(
        verbose_name='Минимальный возраст.',
        help_text='Укажите минимальный возраст получателей.'
                  '<br> Примечание:'
                  '<br> &emsp; - Возраст может быть не меньше 6 лет.'
                  '<br> &emsp; - Поле может быть пустым.'
                  '<br> &emsp; - По умолчанию 6 лет.',
        default=6,
        blank=True,
        validators=[MinValueValidator(6)]
    )
    to_age = models.SmallIntegerField(
        verbose_name='Максимальный возраст.',
        help_text='Укажите максимальный возраст получателей.'
                  '<br> Примечание:'
                  '<br> &emsp; -  Поле может быть пустым.'
                  '<br> &emsp; -  По умолчанию 125 лет.',
        default=125,
        blank=True,
        validators=[MinValueValidator(7)]
    )
    sex = models.CharField(
        verbose_name='Пол получателей.',
        help_text='Выбрать пол получателей, по умолчанию отправка будет производится всем.',
        max_length=2,
        choices=SexOptions.choices,
        default=SexOptions.BOTH,
        blank=True
    )
    subject = models.CharField(
        verbose_name='Тема письма.',
        help_text='Максимальная длина - 125 символов.',
        max_length=125
    )
    title = models.CharField(
        verbose_name='Заглавие.',
        help_text='Максимальная длина - 125 символов.',
        max_length=125
    )
    message = models.TextField(
        verbose_name='Текст сообщения.'
    )
    sent = models.BooleanField(
        verbose_name='Отправлено.',
        default=False
    )
    error = models.CharField(
        verbose_name='Ошибка',
        max_length=255,
        blank=True
    )
    created_at = models.DateTimeField(
        verbose_name='Дата создания.',
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        verbose_name='Дата последнего обновления.',
        auto_now=True
    )

    class Meta:
        verbose_name = 'Поручение'
        verbose_name_plural = 'Поручения'
        ordering = ['-created_at']

    def clean(self) -> None:
        if self.from_age > self.to_age:
            raise ValidationError(
                'Минимальный возраст не может быть меньше максимально!'
            )
        super(Assignment, self).clean()

    @classmethod
    def get_object(cls, guid):
        try:
            return cls.objects.get(guid=guid)
        except cls.DoesNotExist:
            return None

    def __str__(self) -> str:
        return f'{self.guid} - {self.subject}'
