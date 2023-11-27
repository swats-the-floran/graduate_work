from django.contrib import admin

from .models import Link


@admin.register(Link)
class LinkAdmin(admin.ModelAdmin):
    readonly_fields = ['short_link', 'user_id', 'used']
