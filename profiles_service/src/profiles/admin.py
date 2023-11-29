from django.contrib import admin
from .models import Person
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ('email', 'short_full_name', 'age', 'gender_display', 'date_of_birth', 'profile_image_tag')
    list_filter = ('gender', 'date_of_birth')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('last_name', 'first_name')
    readonly_fields = ('age', 'gender_display', 'profile_image_tag')

    def profile_image_tag(self, obj):
        if obj.profile_image:
            return format_html('<img src="{}" style="width: 45px; height:45px;" />', obj.profile_image.url)
        return _("Нет фото.")

    profile_image_tag.short_description = _('Фото профиля')
