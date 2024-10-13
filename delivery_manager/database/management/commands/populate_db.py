# populate_db.py

from django.core.management.base import BaseCommand
from database.models import PlantInfo, EntityType, PlantEntity

class Command(BaseCommand):
    help = 'Populate database with plant, entity types, and plant entities'

    def handle(self, *args, **kwargs):
        # Sample data to populate
        plants_data = [
            {"plant_id": "amk.iserlon", "plant_name": "AMK", "plant_location": "Iserlon", "domain": "amk.wasteant.com"}
        ]

        entity_types_data = {
            "AMK": ["gate"],
        }

        plant_entities_data = {
            "gate": ["gate03", "gate04"],
        }

        # Step 1: Populate PlantInfo
        for plant_data in plants_data:
            if PlantInfo.objects.filter(plant_id=plant_data['plant_id']):
                plant = PlantInfo.objects.get(plant_id=plant_data["plant_id"])
                self.stdout.write(self.style.SUCCESS(f"Plant '{plant.plant_name}' already exists."))
            else:
                plant = PlantInfo(
                    plant_id=plant_data['plant_id'],
                    plant_name=plant_data["plant_name"],
                    plant_location=plant_data["plant_location"],
                    domain=plant_data["domain"],
                )

                plant.save()
                self.stdout.write(self.style.SUCCESS(f"Plant '{plant.plant_name}' created."))

            # Step 2: Populate EntityType for each plant
            if plant.plant_name in entity_types_data:
                for entity in entity_types_data[plant.plant_name]:
                    entity_type, created = EntityType.objects.get_or_create(
                        plant=plant,
                        entity_type=entity,
                    )
                    if created:
                        self.stdout.write(self.style.SUCCESS(f"EntityType '{entity}' created for plant '{plant.plant_name}'."))

                    # Step 3: Populate PlantEntity for each EntityType
                    if entity in plant_entities_data:
                        for entity_uid in plant_entities_data[entity]:
                            plant_entity, created = PlantEntity.objects.get_or_create(
                                entity_type=entity_type,
                                entity_uid=entity_uid,
                            )
                            if created:
                                self.stdout.write(self.style.SUCCESS(f"PlantEntity '{entity_uid}' created for EntityType '{entity}'."))

        self.stdout.write(self.style.SUCCESS('Database population complete.'))
