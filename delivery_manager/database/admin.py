from django.contrib import admin
from .models import PlantInfo, EntityType, PlantEntity, DeliveryEvent, DeliveryState
from .models import Metadata, MetadataColumn, MetadataLocalization, MetadataFlags

@admin.register(PlantInfo)
class PlantInfoAdmin(admin.ModelAdmin):
    """
    Admin interface for the PlantInfo model.
    """
    list_display = ('plant_id', 'plant_name', 'plant_location', 'created_at')  # Display these fields in the list view
    search_fields = ('plant_name', 'plant_location', 'description')  # Search by plant name, location, and description
    list_filter = ('plant_location', 'created_at')  # Add filters for plant location and creation date
    ordering = ('-created_at',)  # Order by creation date, newest first
    readonly_fields = ('created_at',)  # Make created_at field read-only

@admin.register(EntityType)
class EntityTypeAdmin(admin.ModelAdmin):
    """
    Admin interface for the EntityType model.
    """
    list_display = ('plant', 'entity_type', 'created_at')  # Display plant, entity type, and creation date
    search_fields = ('entity_type', 'plant__plant_name')  # Search by entity type and plant name
    list_filter = ('plant', 'created_at')  # Add filters for plant and creation date
    ordering = ('-created_at',)  # Order by creation date, newest first
    readonly_fields = ('created_at',)  # Make created_at field read-only

@admin.register(PlantEntity)
class PlantEntityAdmin(admin.ModelAdmin):
    """
    Admin interface for the PlantEntity model.
    """
    list_display = ('entity_type', 'entity_uid', 'description', 'created_At')  # Display fields in the list view
    search_fields = ('entity_uid', 'description', 'entity_type__entity_type')  # Search by UID, description, and entity type
    list_filter = ('entity_type', 'created_At')  # Add filters for entity type and creation date
    ordering = ('-created_At',)  # Order by creation date, newest first
    readonly_fields = ('created_At',)  # Make created_At field read-only

@admin.register(DeliveryEvent)
class DeliveryEventAdmin(admin.ModelAdmin):
    """
    Admin interface for the DeliveryEvent model.
    """
    list_display = ('event_id', 'event_name', 'event_location', 'event_timestamp', 'status')  # Display event fields
    search_fields = ('event_id', 'event_name', 'event_location__entity_uid', 'status')  # Search by event fields
    list_filter = ('event_location', 'event_timestamp', 'status')  # Add filters for event location, timestamp, and status
    ordering = ('-event_timestamp',)  # Order by event timestamp, newest first
    readonly_fields = ('created_at',)  # Make created_at field read-only

@admin.register(DeliveryState)
class DeliveryStateAdmin(admin.ModelAdmin):
    """
    Admin interface for the DeliveryState model.
    """
    list_display = ('entity', 'delivery_id', 'delivery_status', 'delivery_start', 'delivery_end', 'delivery_location')  # Display delivery state fields
    search_fields = ('delivery_id', 'delivery_location', 'entity__entity_uid')  # Search by delivery fields
    list_filter = ('delivery_status', 'delivery_location', 'created_at')  # Add filters for delivery status and location
    ordering = ('-delivery_start',)  # Order by delivery start date, newest first
    readonly_fields = ('created_at',)  # Make created_at field read-only

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
