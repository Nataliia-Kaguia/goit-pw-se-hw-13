from django.contrib import admin
from .models import Author, Quote, Tag

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('name', 'born_date', 'born_location')

@admin.register(Quote)
class QuoteAdmin(admin.ModelAdmin):
    list_display = ('short_text','author','created_by','created_at')
    list_filter = ('author','tags')
    search_fields = ('text',)

    def short_text(self, obj):
        return obj.text[:80]

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)
