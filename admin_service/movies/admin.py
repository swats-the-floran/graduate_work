from django.contrib import admin

from .models import FilmWork, Genre, GenreFilmWork, Person, PersonFilmWork


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    search_fields = (
        "name",
        "description",
        "id",
    )


class GenreFilmWorkInline(admin.TabularInline):
    model = GenreFilmWork

    autocomplete_fields = ("genre",)


class PersonFilmWorkInline(admin.TabularInline):
    model = PersonFilmWork
    autocomplete_fields = ("person",)


@admin.register(FilmWork)
class FilmWorkAdmin(admin.ModelAdmin):
    inlines = (
        GenreFilmWorkInline,
        PersonFilmWorkInline,
    )

    list_display = ("title", "type", "creation_date", "rating", "get_genres")

    list_filter = (
        "type",
        "genres",
        "rating",
    )

    search_fields = (
        "title",
        "description",
        "id",
    )

    list_prefetch_related = ("genres",)

    def get_queryset(self, request):
        queryset = super().get_queryset(request).prefetch_related(*self.list_prefetch_related)
        return queryset

    def get_genres(self, obj):
        return ", ".join([genre.name for genre in obj.genres.all()])

    get_genres.short_description = "Жанры фильма"


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ("full_name",)

    search_fields = ("full_name", "film_works__title", "id")
