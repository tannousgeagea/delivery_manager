from django.contrib import admin
from unfold.admin import ModelAdmin
from .models import PlantInfo, EntityType, PlantEntity, DeliveryEvent, DeliveryState, Camera

admin.site.site_header = "Delivery Manager"
admin.site.site_title = "Delivery Manager"
admin.site.index_title = "Welcome to Delivery Manager Dashboard Portal"


@admin.register(PlantInfo)
class PlantInfoAdmin(ModelAdmin):
    """
    Admin interface for the PlantInfo model.
    """
    list_display = ('plant_id', 'plant_name', 'plant_location', 'created_at')  # Display these fields in the list view
    search_fields = ('plant_name', 'plant_location', 'description')  # Search by plant name, location, and description
    list_filter = ('plant_location', 'created_at')  # Add filters for plant location and creation date
    ordering = ('-created_at',)  # Order by creation date, newest first
    readonly_fields = ('created_at',)  # Make created_at field read-only

@admin.register(EntityType)
class EntityTypeAdmin(ModelAdmin):
    """
    Admin interface for the EntityType model.
    """
    list_display = ('plant', 'entity_type', 'created_at')  # Display plant, entity type, and creation date
    search_fields = ('entity_type', 'plant__plant_name')  # Search by entity type and plant name
    list_filter = ('plant', 'created_at')  # Add filters for plant and creation date
    ordering = ('-created_at',)  # Order by creation date, newest first
    readonly_fields = ('created_at',)  # Make created_at field read-only

@admin.register(PlantEntity)
class PlantEntityAdmin(ModelAdmin):
    """
    Admin interface for the PlantEntity model.
    """
    list_display = ('entity_type', 'entity_uid', 'description', 'created_At')  # Display fields in the list view
    search_fields = ('entity_uid', 'description', 'entity_type__entity_type')  # Search by UID, description, and entity type
    list_filter = ('entity_type', 'created_At')  # Add filters for entity type and creation date
    ordering = ('-created_At',)  # Order by creation date, newest first
    readonly_fields = ('created_At',)  # Make created_At field read-only

@admin.register(Camera)
class CameraAdmin(ModelAdmin):
    list_display = ('camera_id', 'plant_entity', 'stream_topic', 'location')
    search_fields = ('camera_id', 'plant_entity__plant_name', 'stream_topic', 'location')
    list_filter = ('plant_entity',)

@admin.register(DeliveryEvent)
class DeliveryEventAdmin(ModelAdmin):
    """
    Admin interface for the DeliveryEvent model.
    """
    list_display = ('event_id', 'event_name', 'event_location', 'event_timestamp', 'status')  # Display event fields
    search_fields = ('event_id', 'event_name', 'event_location__entity_uid', 'status')  # Search by event fields
    list_filter = ('event_location', 'event_timestamp', 'status')  # Add filters for event location, timestamp, and status
    ordering = ('-event_timestamp',)  # Order by event timestamp, newest first
    readonly_fields = ('created_at',)  # Make created_at field read-only

@admin.register(DeliveryState)
class DeliveryStateAdmin(ModelAdmin):
    """
    Admin interface for the DeliveryState model.
    """
    list_display = ('entity', 'delivery_id', 'delivery_status', 'delivery_start', 'delivery_end', 'delivery_location')  # Display delivery state fields
    search_fields = ('delivery_id', 'delivery_location', 'entity__entity_uid')  # Search by delivery fields
    list_filter = ('delivery_status', 'delivery_location', 'created_at')  # Add filters for delivery status and location
    ordering = ('-delivery_start',)  # Order by delivery start date, newest first
    readonly_fields = ('created_at',)  # Make created_at field read-only
