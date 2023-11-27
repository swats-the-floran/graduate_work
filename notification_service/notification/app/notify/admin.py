from typing import Any, Dict

from django.contrib import admin, messages
from django.shortcuts import redirect
from django.urls import path, reverse
from django.utils.safestring import mark_safe
from notify.models import Assignment, NotificationLog
from notify.tasks import task_send_assignment


admin.site.register(NotificationLog)


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('guid', 'subject', 'title', 'from_age', 'to_age', 'sex', 'custom_actions', 'sent', 'error',)
    list_display_links = ('guid',)
    readonly_fields = 'created_at', 'updated_at', 'sent', 'error'

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('send_notify/<str:guid>/',
                 self.admin_site.admin_view(self.send_notify),
                 name='send_notify'
                 ),
        ]
        return my_urls + urls

    def custom_actions(self, obj: Assignment):
        default_disable_dict = {
            'disabled': 'disabled',
            'title': 'Сообщение отправлено.',
            'onclick': '"alert(\'Сообщение уже отправлено.\'); return false;"'
        }
        default_disable_str = ' '.join(f'{k}={v}' for k, v in default_disable_dict.items())
        send_notify_str: Any[str, Dict[str, str]] = {}

        url_send_notify = reverse("admin:send_notify", args=[obj.guid])

        if obj.sent:
            send_notify_str = default_disable_str
            return mark_safe(  # noqa
                f'<p><a class="button" {send_notify_str} href="{url_send_notify}">'
                f'Сообщение отправлено.</a></p>'
            )

        return mark_safe(  # noqa
            f'<p><a class="button" {send_notify_str} href="{url_send_notify}">'
            f'Отправить сообщение.</a></p>'
        )

    custom_actions.short_description = 'Действия'
    custom_actions.allow_tags = True

    def send_notify(self, request, guid, *args, **kwargs):
        response = redirect(reverse('admin:notify_assignment_changelist'))
        assignment = Assignment.get_object(guid)

        if not assignment:
            messages.warning(request, 'Поручение не найдено.')

        elif assignment.sent:
            messages.warning(request, 'Сообщение было отправлено, для повторной отправки создайте новое поручение.')
        else:
            task_send_assignment.delay(guid=assignment.guid)
            messages.info(request, 'Задача на отправку сообщений поставлена!')
        return response
