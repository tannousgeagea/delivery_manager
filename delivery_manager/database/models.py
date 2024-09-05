from django.db import models

class PlantInfo(models.Model):
    """
    Represent information about the plant
    
    Attributes:
        - plant_id (CharField): a string field to store the id of the plant
        - plant_name (CharField): a string field to store the name of the plant
        - plant_location (CharField): a string field to the location of the plant
        - description (CharField): a string field to provide description on the plant
        - meta_info (JSONField): a json field for additional info
    """
    plant_id = models.CharField(max_length=255)
    plant_name = models.CharField(max_length=255)
    plant_location = models.CharField(max_length=255)
    description = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    meta_info = models.JSONField(null=True, blank=True)
    
    class Meta:
        db_table = "plant_info"
        verbose_name_plural = 'Plant Info'
        indexes = [
            models.Index(fields=['plant_name', 'plant_location']),
        ]
        unique_together = ('plant_name', 'plant_location')

    def __str__(self,):
        return f"{self.plant_name} in {self.plant_location}"

# Create your models here.
class EntityType(models.Model):
    """
    Represents a type of entity within the application. This model is used to store distinct entity types, characterized by their 'entity_type' field.

    Attributes:
    - entity_type (CharField): A string field to store the type of the entity. Max length is set to 250 characters.
    - entry_timestamp (DateTimeField): A timestamp indicating when the entity type was created or registered in the system. It defaults to the current time when the entity type instance is created.

    The Meta class defines the database table name 'entity_type' and sets a verbose name in plural form 'Entity Types'.
    The __str__ method returns the string representation of the entity type, making it more readable and identifiable in admin interfaces or when queried.
    """
    plant = models.ForeignKey(PlantInfo, on_delete=models.CASCADE)
    entity_type = models.CharField(max_length=250)
    created_at = models.DateTimeField(auto_now_add=True)
    meta_info = models.JSONField(null=True, blank=True)


    class Meta:
        db_table = "entity_type"
        verbose_name_plural = "Entity Types"

    def __str__(self):
        return self.entity_type
    
class PlantEntity(models.Model):

    """
    Represents a plant entity within the application, associated with a specific type of entity defined in EntityType. This model is used to store and manage plant entities, keeping track of their types, unique identifiers, and descriptions.

    Attributes:
    - entity_type (ForeignKey): A foreign key linking to the EntityType model, defining the type of the plant entity.
    - entity_uid (CharField): A unique identifier for the plant entity. Max length is set to 250 characters.
    - description (CharField): A brief description of the plant entity. Max length is set to 250 characters.
    - entry_timestamp (DateTimeField): A timestamp indicating when the plant entity was created or registered in the system. It defaults to the current time when the plant entity instance is created.

    The Meta class defines the database table name 'plant_entity' and sets a verbose name in plural form ' Plant Entities'.
    The __str__ method returns a string representation of the plant entity, combining the entity type and the unique identifier, making it easily identifiable and readable, especially in admin interfaces or when queried.
    """

    entity_type = models.ForeignKey(EntityType, on_delete=models.CASCADE)
    entity_uid = models.CharField(max_length=250)
    description = models.CharField(max_length=250)
    created_At = models.DateTimeField(auto_now_add=True)
    meta_info = models.JSONField(null=True, blank=True)

    class Meta:
        db_table = "plant_entity"
        verbose_name_plural = "Plant Entities"

    def __str__(self):
        return f'{self.entity_type}, {self.entity_uid}'
    
class DeliveryEvent(models.Model):

    """
    Represents an event within the application. This model is used to log and manage events, providing insights into the source, cause, and detailed description of each event.

    Attributes:
    - event_id (CharField): A unique identifier for the event. Max length is set to 250 characters.
    - entry_timestamp (DateTimeField): A timestamp indicating when the event was logged or occurred. Defaults to the current time when the instance is created.
    - event_source (CharField): The source of the event, indicating what or who triggered the event. Max length is set to 250 characters.
    - event_cause (CharField): The cause of the event, providing a brief explanation or reason. Max length is set to 250 characters.
    - description (CharField): A detailed description of the event. Max length is set to 250 characters.

    The Meta class defines the database table name 'events' and sets a verbose name in plural form 'Events'.
    The __str__ method returns a string representation of the event, combining the event ID, event source, event cause, and the description, providing a comprehensive overview and making it easily identifiable and readable, especially useful in admin interfaces or when queried.
    """

    event_id = models.CharField(max_length=250)
    event_name = models.CharField(max_length=255)
    event_location = models.ForeignKey(PlantEntity, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    event_timestamp = models.DateTimeField()
    status = models.CharField(max_length=255)
    description = models.CharField(max_length=250, null=True, blank=True)
    meta_info = models.JSONField(null=True, blank=True)


    class Meta:
        db_table = "delivery_event"
        verbose_name_plural = "Delivery Events"
        indexes = [
            models.Index(
                fields=["event_location", "event_timestamp"]),
            models.Index(
                fields=["status", "event_timestamp", "event_location"],
            )
        ]

    def __str__(self):
        return f"{self.event_name} at {self.event_location} at {self.event_timestamp}"
    
    
class DeliveryState(models.Model):
    entity = models.ForeignKey(PlantEntity, on_delete=models.CASCADE)
    delivery_id = models.CharField(max_length=255)
    delivery_start = models.DateTimeField()
    delivery_end = models.DateTimeField(null=True)
    delivery_status = models.CharField(max_length=255, default='pending')
    delivery_location = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    meta_info = models.JSONField(null=True, blank=True)
    
    class Meta:
        db_table = 'delivery_state'
        verbose_name_plural = 'Delivery State'
    
    def __str__(self):
        return f'Delivery at {self.delivery_location} at {self.created_at}'
    
class Metadata(models.Model):
    """
    Represents general metadata information.
    
    Attributes:
        - primary_key (CharField): The primary key column name.
    """
    primary_key = models.CharField(max_length=255)

    class Meta:
        db_table = 'metadata'
        verbose_name_plural = 'Metadata'

    def __str__(self):
        return f"Metadata with primary key: {self.primary_key}"
    
class MetadataColumn(models.Model):
    """
    Represents a metadata column.
    
    Attributes:
        - metadata (ForeignKey): A reference to the Metadata object.
        - column_name (CharField): The internal name of the column.
        - type (CharField): The data type of the column (e.g., "string").
    """
    metadata = models.ForeignKey(Metadata, on_delete=models.CASCADE, related_name='columns')
    column_name = models.CharField(max_length=255)
    type = models.CharField(max_length=50)

    class Meta:
        db_table = 'metadata_column'
        verbose_name_plural = 'Metadata Columns'
        unique_together = ('metadata', 'column_name')  # Ensure unique columns per metadata entry
        indexes = [
            models.Index(fields=['metadata', 'column_name']),
        ]

    def __str__(self):
        return f"Column: {self.column_name} (Type: {self.type})"

class MetadataLocalization(models.Model):
    """
    Represents localized metadata for columns.
    
    Attributes:
        - metadata_column (ForeignKey): A reference to the MetadataColumn object.
        - language (CharField): The language code (e.g., "en", "de").
        - title (CharField): Localized title of the column.
        - description (TextField): Localized description of the column.
    """
    metadata_column = models.ForeignKey(MetadataColumn, on_delete=models.CASCADE, related_name='localizations')
    language = models.CharField(max_length=10)  # ISO 639-1 codes, e.g., "en", "de"
    title = models.CharField(max_length=255)
    description = models.TextField()

    class Meta:
        db_table = 'metadata_localization'
        verbose_name_plural = 'Metadata Localizations'
        unique_together = ('metadata_column', 'language')  # Ensure unique localization per column-language pair
        indexes = [
            models.Index(fields=['metadata_column', 'language']),
        ]

    def __str__(self):
        return f"Localization for '{self.metadata_column.column_name}' in {self.language}"

class MetadataFlags(models.Model):
    """
    Represents flags associated with metadata columns.
    
    Attributes:
        - metadata (ForeignKey): A reference to the Metadata object.
        - column_name (CharField): The name of the column to be flagged.
    """
    metadata = models.ForeignKey(Metadata, on_delete=models.CASCADE, related_name='flags')
    column_name = models.CharField(max_length=255)
    description = models.TextField(null=True)

    class Meta:
        db_table = 'metadata_flags'
        verbose_name_plural = 'Metadata Flags'
        unique_together = ('metadata', 'column_name')  # Ensure unique flags per metadata entry
        indexes = [
            models.Index(fields=['metadata', 'column_name']),
        ]

    def __str__(self):
        return f"Flag for column: {self.column_name} in Metadata ID {self.metadata.id}"
