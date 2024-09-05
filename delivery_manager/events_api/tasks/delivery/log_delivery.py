import os
import uuid
import celery
import django
from celery import shared_task
from datetime import datetime, timezone
django.setup()
from utils.state import StateMachine
from database.models import PlantInfo, PlantEntity, DeliveryEvent, DeliveryState

fsm = StateMachine()
DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'

@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 5},
             name='delivery:create_delivery')
def create_delivery(self, **kwargs):
    data: dict = {}
    event = kwargs
    
    try:
        if not PlantEntity.objects.filter(entity_uid=event['location']).exists():
            self.request.state = "FAILURE"
            data.update(
                {
                    "action": "failed",
                    "task_id": self.request.id,
                    "time": datetime.now().strftime(DATETIME_FORMAT),
                    "result": f"Invalid event location ID {event['location']} provided. Delivery event could not be saved.",
                }
            )
            
            return data
        
        plant_entity = PlantEntity.objects.get(entity_uid=event['location'])
        last_delivery = DeliveryState.objects.filter(entity=plant_entity).order_by('-created_at').first()
        
        fsm.on_event(event=event['status'])
        dt = datetime.now().strftime(DATETIME_FORMAT)
        
        delivery_status = last_delivery.delivery_status if last_delivery else 'done'
        
        msg = f'{dt}: No delivery at the moment'
        if delivery_status == 'on-going':
            msg = f'{dt}: delivery on going'
        
        if str(fsm) == 'truck' and delivery_status == 'done':
            delivery_start = datetime.now(tz=timezone.utc)
            delivery_state = DeliveryState()
            delivery_state.delivery_start = delivery_start
            delivery_state.delivery_id = event['event_uid']
            delivery_state.entity = plant_entity
            delivery_state.delivery_status = 'on-going'
            delivery_state.delivery_location = event['location']
            delivery_state.meta_info = event.get('meta_info')
            delivery_state.save()
            msg = f"delivery start at {delivery_start}"
            
        if str(fsm)=='no-truck':
            delivery_end = datetime.now(tz=timezone.utc)
            delivery_state = last_delivery
            
            if delivery_status == 'on-going':
                delivery_state.delivery_end = delivery_end
                delivery_state.delivery_status = 'done'                
                delivery_state.save()
                msg = f"delivery end at {delivery_end}"
        
        data.update(
            {
                "action": "done",
                "task_id": self.request.id,
                "time": datetime.now().strftime("%Y-%m-%d %H-%M-%S"),
                "result": msg
            }
        )

    except Exception as err:
        raise ValueError(f"Error occured while creating delivery: {err}")

    return data



        
    
    
    
    