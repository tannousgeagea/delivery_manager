from django.contrib import admin
from .models import (
    Metadata,
    MetadataColumn,
    MetadataFlags,
    MetadataLocalization
)

# Register your models here.
@admin.register(Metadata)
class MetadataAdmin(admin.ModelAdmin):
    list_display = ('id', 'primary_key')
    search_fields = ('primary_key',)
    list_filter = ('primary_key',)
    ordering = ('id',)

    class MetadataColumnInline(admin.TabularInline):
        model = MetadataColumn
        extra = 1

    class MetadataFlagsInline(admin.TabularInline):
        model = MetadataFlags
        extra = 1

    inlines = [MetadataColumnInline, MetadataFlagsInline]

@admin.register(MetadataColumn)
class MetadataColumnAdmin(admin.ModelAdmin):
    list_display = ('id', 'metadata', 'column_name', 'type')
    search_fields = ('column_name', 'type')
    list_filter = ('metadata', 'type')
    ordering = ('metadata', 'column_name')

@admin.register(MetadataLocalization)
class MetadataLocalizationAdmin(admin.ModelAdmin):
    list_display = ('id', 'metadata_column', 'language', 'title')
    search_fields = ('language', 'title', 'description')
    list_filter = ('language', 'metadata_column')
    ordering = ('metadata_column', 'language')

@admin.register(MetadataFlags)
class MetadataFlagsAdmin(admin.ModelAdmin):
    list_display = ('id', 'metadata', 'column_name')
    search_fields = ('column_name',)
    list_filter = ('metadata',)
    ordering = ('metadata', 'column_name')