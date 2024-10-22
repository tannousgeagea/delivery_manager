import os
import uuid
import time
import celery
import django
from celery import shared_task
from datetime import datetime, timezone
django.setup()
from utils.state import StateMachine
from utils.time.time_tracker import KeepTrackOfTime
from utils.media import request_video, request_image
from utils.api.base import BaseAPI
from database.models import PlantInfo, PlantEntity, DeliveryEvent, DeliveryState

fsm = StateMachine()
DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'
topics = os.getenv('topics', "/top/rgb_left")
MediaManager_API = os.getenv('MEDIA_MANAGER_API', "MediaManager_core")

base_api = BaseAPI()
keep_track_of_time = KeepTrackOfTime()

@shared_task(bind=True, autoretry_for=(Exception,), retry_backoff=True, retry_kwargs={"max_retries": 5},
             name='delivery:create_delivery')
def create_delivery(self, event, **kwargs):
    data: dict = {}
    
    try:
        if not PlantEntity.objects.filter(entity_uid=event.location).exists():
            self.request.state = "FAILURE"
            data.update(
                {
                    "action": "failed",
                    "task_id": self.request.id,
                    "time": datetime.now().strftime(DATETIME_FORMAT),
                    "result": f"Invalid event location ID {event.location} provided. Delivery event could not be saved.",
                }
            )
            
            return data
        
        plant_entity = PlantEntity.objects.get(entity_uid=event.location)
        last_delivery = DeliveryState.objects.filter(entity=plant_entity).order_by('-created_at').first()
        
        fsm.on_event(event=event.status)
        dt = datetime.now().strftime(DATETIME_FORMAT)
        
        delivery_status = last_delivery.delivery_status if last_delivery else 'done'
        delivery_id = last_delivery.delivery_id if last_delivery else event.event_uid
        
        msg = f'{dt}: No delivery at the moment'
        if delivery_status == 'on-going':
            msg = f'{dt}: delivery on going'
        
        params = {
            'gate_id': event.location,
            'event_id': event.event_uid,
            'event_name': event.event_name,
            'event_type': 'start',
            'timestamp': dt,
            'topics': topics,
        }
        
        if str(fsm) == 'truck' and delivery_status == 'done':
            delivery_start = datetime.now(tz=timezone.utc)
            delivery_state = DeliveryState()
            delivery_state.delivery_start = delivery_start
            delivery_state.delivery_id = event.event_uid
            delivery_state.entity = plant_entity
            delivery_state.delivery_status = 'on-going'
            delivery_state.delivery_location = event.location
            delivery_state.meta_info = event.meta_info
            delivery_state.save()
            msg = f"delivery start at {delivery_start}"
            
            params.update(
                {
                    "event_type": "start",
                    "event_description": msg,
                    "event_id": delivery_state.delivery_id,
                }
            )

            
            request_video.send_request(
                url=f"http://{MediaManager_API}:18042/api/v1/event/rt_video/start",
                params=params,
            )      
                
        if str(fsm)=='no-truck':
            delivery_end = datetime.now(tz=timezone.utc)
            delivery_state = last_delivery
            
            if delivery_status == 'on-going':
                delivery_state.delivery_end = delivery_end
                delivery_state.delivery_status = 'done'                
                delivery_state.save()
                msg = f"delivery end at {delivery_end}"
                
                params.update(
                    {
                        "event_type": "stop",
                        "event_description": msg,
                        "event_id": delivery_state.delivery_id,
                    }
                )
                
                request_video.send_request(
                    url=f"http://{MediaManager_API}:18042/api/v1/event/rt_video/stop",
                    params=params,
                ) 
        
                base_api.post(
                    url=f"http://{os.getenv('EDGE_CLOUD_SYNC_HOST', '0.0.0.0')}:{os.getenv('EDGE_CLOUD_SYNC_PORT', '27092')}/api/v1/data",
                    payload={
                        'event_id': delivery_state.delivery_id,
                        "source_id": "delivery_manager",
                        "target": "delivery",
                        "data": {
                            "tenant_domain": "amk.wasteant.com",
                            "delivery_id": delivery_state.delivery_id,
                            "location": delivery_state.delivery_location,
                            "delivery_start": delivery_state.delivery_start.strftime(DATETIME_FORMAT),
                            "delivery_end": delivery_state.delivery_end.strftime(DATETIME_FORMAT),
                        }
                    }
                )
        
        
        print('Time Diff: ',keep_track_of_time.check_if_time_more_than_diff(
            start=keep_track_of_time.what_is_the_time, 
            end=time.time(), 
            diff=int(os.getenv('IMAGE_RATE', 10))
            ) and delivery_status == 'on-going')
        
        
        if delivery_status == 'on-going' and keep_track_of_time.check_if_time_more_than_diff(
            start=keep_track_of_time.what_is_the_time, 
            end=time.time(), 
            diff=int(os.getenv('IMAGE_RATE', 10))
            ):
            params = {
                'gate_id': event.location,
                'event_name': event.event_name,
                'timestamp': dt,
                "event_type": "delivery on-going",
                "event_description": msg,
                "event_id": delivery_id,
                "topic": topics.split(',')[0]
                }
            
            request_image.send_request(
                url=f"http://{MediaManager_API}:18042/api/v1/event/image",
                params=params
            )
            
            keep_track_of_time.update_time()
        
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



        
    
    
    
    