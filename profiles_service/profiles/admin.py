from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html

from .models import Bookmark, Favorite, FilmReview, Person


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'email',
        'short_full_name',
        'age',
        'gender_display',
        'date_of_birth',
        'profile_image_tag',
        'is_active'
    )
    list_filter = ('gender', 'date_of_birth')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('last_name', 'first_name')
    readonly_fields = ('age', 'gender_display', 'profile_image_tag')
    exclude = ('password',)

    def profile_image_tag(self, obj):
        if obj.profile_image:
            return format_html('<img src="{}" style="width: 45px; height:45px;" />', obj.profile_image.url)
        return _("Нет фото.")

    profile_image_tag.short_description = _('Фото профиля')


@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    pass


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('id', 'movie_id', 'movie_name', 'person')


@admin.register(FilmReview)
class FilmReviewAdmin(admin.ModelAdmin):
    pass

