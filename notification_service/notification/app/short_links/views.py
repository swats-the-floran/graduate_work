from django.conf import settings
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views import View

from .models import Link
from .utils import activate_user_in_auth_service


class ActivateUserView(View):

    def get(self, request, short_link):
        link = get_object_or_404(Link, short_link=short_link, valid_to__gte=timezone.now())

        activate_user_in_auth_service(link.user_id)
        link.used = True
        link.save(update_fields=['used'])

        redirect_to = getattr(settings, 'REDIRECT_AFTER_ACTIVATION')
        return HttpResponseRedirect(redirect_to)
