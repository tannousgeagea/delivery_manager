from django.db import models

# Create your models here.
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