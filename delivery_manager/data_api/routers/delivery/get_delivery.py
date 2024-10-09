import os
import math
import time
import django
django.setup()
from django.db import connection
from datetime import datetime, timedelta
from datetime import date, timezone
from typing import Callable
from fastapi import Request
from fastapi import Response
from fastapi import APIRouter
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute
from fastapi import status
from pydantic import BaseModel
from typing import Dict, List, Optional
from metadata.models import MetadataColumn, Metadata
from database.models import PlantEntity, DeliveryState

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"

red_square = '🟥'
yellow_square = '🟨'
green_square = '🟩'
orange_square = '🟧'

mapping_flag = {
    0: green_square,
    1: yellow_square,
    2: orange_square,
    3: red_square,
}

class TimedRoute(APIRoute):
    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()
        async def custom_route_handler(request: Request) -> Response:
            before = time.time()
            response: Response = await original_route_handler(request)
            duration = time.time() - before
            response.headers["X-Response-Time"] = str(duration)
            print(f"route duration: {duration}")
            print(f"route response: {response}")
            print(f"route response headers: {response.headers}")
            return response

        return custom_route_handler


router = APIRouter(
    prefix="/api/v1",
    tags=["Delivery"],
    route_class=TimedRoute,
    responses={404: {"description": "Not found"}},
)


summary="Retrieve Delivery Metadata",
description="""
Retrieves the metadata for delivery information in the specified language.

The metadata includes the column titles, types, and descriptions based on the specified language code (e.g., "en" for English, "de" for German). 
The `metadata_id` is used to specify which set of metadata to retrieve.

### Path Parameters
- **language**: A string representing the language code (e.g., "en" for English, "de" for German). Default is "de".

### Query Parameters
- **metadata_id**: An integer representing the ID of the metadata to retrieve. Default is 1.

### Responses
- **200 OK**: Returns the metadata details.
- **404 Not Found**: Returns an error if the specified metadata ID or language is not found.
- **500 Internal Server Error**: Returns an error if an unexpected error occurs.
"""


@router.api_route(
    "/delivery/metadata/{language}", methods=["GET"], tags=["Delivery"], summary=summary, description=description,
)
def get_delivery_metadata(response: Response, language:str="de", metadata_id:int=1):
    metadata = {}
    try:
        if not MetadataColumn.objects.filter(metadata_id=metadata_id).exists():
            metadata = {
                "error": {
                    "status_code": "not found",
                    "status_description": f"Metadata ID {metadata_id} not found",
                    "deatil": f"Metadata ID {metadata_id} not found",
                }
            }
            
            response.status_code = status.HTTP_404_NOT_FOUND
            return metadata
        
        columns = MetadataColumn.objects.filter(metadata_id=metadata_id).select_related('metadata').prefetch_related('localizations')

        col = []
        for column in columns:
            localization = column.localizations.filter(language=language).first()
            if not localization:
                metadata = {
                    "error": {
                        "status_code": "not found",
                        "status_description": f"language {language} not found",
                        "deatil": f"language {language} not found",
                    }
                }
                
                response.status_code = status.HTTP_404_NOT_FOUND
                return metadata
            
            col.append(
                {
                    column.column_name: {
                        "title": localization.title,
                        "type": column.type,
                        "description": localization.description                        
                    }

                }
            )
            
        metadata = {
            "columns": col,
            "primary_key": Metadata.objects.get(id=metadata_id).primary_key
        }
        return metadata

    except Exception as e:
        metadata = {
            "error": {
                "status_code": "internal server error",
                "status_description": f"Error {e}",
                "deatil": f"Error: {e}",
            }
        }
        
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return metadata


class DeliveryItemResponse(BaseModel):
    """Schema for an individual delivery record."""
    delivery_id: str
    date: str
    start: str
    end: str
    location: str
    problematic_objetcs: str
    long_objects: str
    dust: str
    hotspot: str

class FlagInterpretationResponse(BaseModel):
    """Schema for flag interpretation in the response."""
    description: str
    color: str
    hex: str

class DeliveryResponse(BaseModel):
    """Schema for the overall delivery response."""
    type: str
    total_record: int
    pages: int
    items: List[DeliveryItemResponse]
    flag_interpretation: Dict[str, FlagInterpretationResponse]

summary="Retrieve Delivery Data",
description="""
Retrieves a list of deliveries for a specified gate and date range.

The delivery data includes the delivery ID, date, start and end times, location, and various flags for problematic objects, long objects, dust, and hotspots.

### Query Parameters
- **gate_id** (optional): A string representing the unique identifier for a gate.
- **from_date** (optional): A datetime object representing the start date to filter deliveries. Defaults to today's date if not provided.
- **to_date** (optional): A datetime object representing the end date to filter deliveries. Defaults to the day after `from_date` if not provided.
- **items_per_page** (optional): An integer specifying the number of delivery records to return per page. Default is 15.
- **page** (optional): An integer specifying which page of results to return. Default is 1.
- **metadata_id** (optional): An integer representing the metadata ID to use. Default is 1.

### Responses
- **200 OK**: Returns the delivery data.
- **400 Bad Request**: Returns an error if the input parameters are invalid.
- **404 Not Found**: Returns an error if the specified gate ID is not found.
- **500 Internal Server Error**: Returns an error if an unexpected error occurs.
"""


@router.api_route(
    "/delivery", methods=["GET"], tags=["Delivery"], summary=summary, description=description,
)
def get_delivery(
    response: Response, 
    gate_id:str=None, 
    from_date:datetime=None, 
    to_date:datetime=None, 
    items_per_page:int=15, 
    page:int=1, 
    metadata_id:int=1
    ) -> DeliveryResponse:
    results = {}
    try:
        
        
        today = datetime.today()
        if from_date is None:
            from_date = datetime(today.year, today.month, today.day)
        
        if to_date is None:
            to_date = from_date + timedelta(days=1)
            
        from_date = from_date.replace(tzinfo=timezone.utc)
        to_date = to_date.replace(tzinfo=timezone.utc) + timedelta(days=1)
        
        if page < 1:
            page = 1
        
        if items_per_page==0:
            results['error'] = {
                'status_code': 'bad request',
                'status_description': f'Bad Request, items_per_pages should not be 0',
                'detail': "division by zero."
            }

            response.status_code = status.HTTP_400_BAD_REQUEST
            return results
        
        if gate_id is not None:
            if not PlantEntity.objects.filter(entity_uid=gate_id).exists():
                results = {
                    "error": {
                        "status_code": "not found",
                        "status_description": f"Gate ID {gate_id} not found",
                        "deatil": f"Gate ID {gate_id} not found",
                    }
                }
                
                response.status_code = status.HTTP_404_NOT_FOUND
                return results
            
            plant_entity = PlantEntity.objects.get(entity_uid=gate_id)
            delivery_state = DeliveryState.objects.filter(entity=plant_entity, created_at__range=(from_date, to_date )).order_by('-created_at')
        else:
            delivery_state = DeliveryState.objects.filter(created_at__range=(from_date, to_date)).order_by('-created_at')
        
        rows = []
        total_record = len(delivery_state)
        for delivery in delivery_state[(page - 1) * items_per_page:page * items_per_page]:
            
            beginn = delivery.delivery_start
            ende = delivery.delivery_end
            
            if delivery.delivery_status == "on-going":
                ende = datetime.now(tz=timezone.utc)

            delivery_id = str(delivery.id).zfill(6)
            severity_level = 0 # query_impurity_severity_level(url=f"{os.environ.get('FLAG_API_URL')}/api/v1/impurity/delivery/{delivery_id}")
            
            if not delivery.meta_info:
                delivery.meta_info = {}
            
            long_object_severity_level = 0
            
            impurity_flag = mapping_flag[severity_level]
            long_object_flag = mapping_flag[long_object_severity_level]
              
            row = DeliveryItemResponse(
                delivery_id=delivery_id,
                date=(beginn + timedelta(hours=2)).strftime('%Y-%m-%d'),
                start=(beginn + timedelta(hours=2)).strftime('%H:%M:%S'),
                end=(ende + timedelta(hours=2)).strftime('%H:%M:%S'),
                location=delivery.delivery_location,
                problematic_objetcs=impurity_flag,
                long_objects=long_object_flag,
                dust=green_square,  # Placeholder
                hotspot=green_square,  # Placeholder
            )
            
            rows.append(row.dict())
            
        connection.close()
        
        return DeliveryResponse(
            type='collection',
            total_record=total_record,
            pages=math.ceil(total_record / items_per_page),
            items=rows,
            flag_interpretation={
                'niedrig': {
                    'description': "Auffälligkeitgrad ist niedrig",
                    'color': 'yellow',
                    'hex': '#FFFF00',
                },
                'mittel': {
                    'description': "Auffälligkeitgrad ist mittel",
                    'color': 'orange',
                    "hex": "#FFA500",
                },    
                'hoch': {
                    'description': "Auffälligkeitgrad ist hoch",
                    'color': 'red',
                    "hex": "#FF0000",
                },
                'normal': {
                    'description': "Keine Auffälligkeit",
                    'color': 'green',
                    "hex": "#008000",
                },
            }
        )

    except PlantEntity.DoesNotExist as e:
        results['error'] = {
            'status_code': 404,
            'status_description': f'Matching query for gate_id {gate_id} was not found',
            'detail': "PlantEntity matching query does not exist."
        }

        response.status_code = status.HTTP_404_NOT_FOUND
        
        return results
    
    except HTTPException as e:
        results['error'] = {
            "status_code": 404,
        }
        
        response.status_code = status.HTTP_404_NOT_FOUND
        return results
    
    except Exception as e:
        results['error'] = {
            'status_code': 500,
            "status_description": "Internal Server Error",
            "detail": str(e),
        }
        
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return results
    





description = """

This API endpoint is designed to retrieve detailed information related to a delivery identified by delivery_id. Here's a breakdown of its functionality:
Endpoint Definition

python

@router.api_route(
    "/delivery/assets/{delivery_id}", methods=["GET"], tags=["Delivery"]
)

    Route: /delivery/assets/{delivery_id}
    Methods: GET
    Tags: ["Delivery"]
    Parameters:
        delivery_id: Path parameter representing the unique identifier of the delivery.

Functionality

    Input Validation:
        Checks if delivery_id is 'null'. If true, returns a 400 Bad Request response indicating that delivery_id cannot be null.
        Checks if delivery_id is not a digit. If true, returns a 400 Bad Request response indicating that delivery_id should be a number.

    Existence Check:
        Queries the database (DeliveryState model) to verify if a delivery with the specified delivery_id exists. If not found, returns a 404 Not Found response indicating that the delivery was not found.

    Successful Response:
        If the delivery_id is valid and exists, constructs a detailed response containing:
            Information about the delivery ('delivery' section).
            Analytics related to the delivery ('analytics' section), including querying external APIs (query_impurity_by_delivery, query_staub_by_delivery, query_hotspot_by_delivery).
            Additional information ('information' section) related to the delivery, such as comments and additional data.

    Error Handling:
        Catches exceptions:
            HTTPException: Specifically catches and handles HTTP exceptions, setting a 404 Not Found status code.
            General Exception: Catches any other unexpected errors, setting a 500 Internal Server Error status code and providing details of the error in the response.

Response Structure

    Success Response (200 OK):
        Detailed JSON structure containing sections for delivery details, analytics, and additional information.

    Error Responses:
        400 Bad Request: When delivery_id is 'null' or not a digit.
        404 Not Found: When the specified delivery_id does not exist in the database or when caught HTTPException.
        500 Internal Server Error: For any other unexpected errors, providing details of the error in the response.

Usage

This API is used to fetch comprehensive information and analytics related to a specific delivery identified by delivery_id, integrating with external analytics APIs to provide enriched data about the delivery process.

"""


@router.api_route(
    "/delivery/assets/{delivery_id}", methods=["GET"], tags=["Delivery"], description=description,
)
def get_delivery_assets(response: Response, delivery_id:str):
    results = {}
    
    try:
        
        
        if delivery_id == 'null':
            results['error'] = {
                'status_code': "bad-request",
                'status_description': "delivery_id is not supposed to be null",
                'detail': 'delivery_id is null, please provide a valid delivery_id'
            }
            response.status_code = status.HTTP_400_BAD_REQUEST
            return results
        
        if not delivery_id.isdigit():
            results['error'] = {
                'status_code': "bad-request",
                'status_description': f"delivery_id is expected a number but got {delivery_id}",
                'detail': 'delivery_id is null, please provide a valid delivery_id'
            }
            response.status_code = status.HTTP_400_BAD_REQUEST
            return results
    
        if not DeliveryState.objects.filter(id=delivery_id).exists():
            results['error'] = {
                'status_code': "Not-Found",
                'status_description': f"delivery_id {delivery_id} is not found",
                'detail': 'please provide a valid delivery_id'
            }
            response.status_code = status.HTTP_404_NOT_FOUND
            return results
            
            
            
        delivery = DeliveryState.objects.get(id=delivery_id)
        meta_info = delivery.meta_info if delivery.meta_info is not None else {}
        snapshots_dir = meta_info.get('snapshots', "do-not-exist")
        snapshots_dir = "/media/alarms/delivery" +  snapshots_dir.split('delivery')[1]
        snapshots = sorted(glob(snapshots_dir + "/*.jpg"))
        
        videos_dir = meta_info.get('videos', "do-not-exist")
        videos_dir = "/media/alarms/delivery" +  videos_dir.split('delivery')[1]
        videos = glob(videos_dir + "/*.avi") + glob(videos_dir + "/*.mp4")
        videos_with_bbx = glob(videos_dir + "/" "stoerstoff" + "/*.avi") + glob(videos_dir + "/" + "stoerstoff" + "/*.mp4")
        
        substitue_data = {
            "url": "/alarms/delivery/documentation-in-progress.jpg",
            "name": "Dokumentation in der Erstellung",
            "time": (datetime.now() + timedelta(hours=2)).strftime("%Y-%m-%d %H:%M:%S"),
        }
        
        results['delivery'] = {
            'title': "Nachschau",
            'items': {
                'snapshots': {
                    'title': 'Aktivität',
                    'type': 'image',
                    'snapshots_dir': snapshots_dir,
                    'data': [
                        {
                            'url': snapshot.split('media')[1],
                            'name': (datetime.strptime(f"{snapshot.split('/')[-1].split('.')[0].split('_')[0]} {snapshot.split('/')[-1].split('.')[0].split('_')[1].replace('-', ':')}", DATETIME_FORMAT) + timedelta(hours=2)).strftime(DATETIME_FORMAT),
                            'time': (datetime.strptime(f"{snapshot.split('/')[-1].split('.')[0].split('_')[0]} {snapshot.split('/')[-1].split('.')[0].split('_')[1].replace('-', ':')}", DATETIME_FORMAT) + timedelta(hours=2)).strftime(DATETIME_FORMAT),
                        } for snapshot in snapshots] if len(snapshots) else [substitue_data],
                }
            }
        }
        
        if len(videos):
            results['delivery']['items']['videos'] = {
                'title': 'Zeitrafferaufnahme',
                'type': 'video',
                'data': [
                    {
                        'url': video.split('media')[1],
                        'name': video.split('/')[-1].split('.')[0],
                        'time': video.split('/')[-1].split('.')[0], 
                    } for video in videos]
            }
            
        if len(videos_with_bbx):
            results['delivery']['items']['videos_with_bbx'] = {
                'title': "Störstoffdetektion",
                'type': 'video',
                'data': [
                    {
                        'url': video.split('media')[1],
                        'name': video.split('/')[-1].split('.')[0],
                        'time': video.split('/')[-1].split('.')[0], 
                    } for video in videos_with_bbx]
            }
        
        
        results['analytics'] = query_flag_assets(delivery_id=delivery_id, snapshots_dir=snapshots_dir, videos_dir=videos_dir, long_object_severity_level=delivery.meta_info.get('long_object_severity_level', 0))
        
        
        connection.close()
        return results    
    
    except HTTPException as e:
        results['error'] = {
            "status_code": 404,
        }
        
        response.status_code = status.HTTP_404_NOT_FOUND
        return results
    
    except Exception as e:
        results['error'] = {
            'status_code': 500,
            "status_description": "Internal Server Error",
            "detail": str(e),
        }
        
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return results

@router.api_route(
    "/gate/{gate_id}", methods=["GET"], tags=["Delivery"], description=description,
)
def get_gate_status(response: Response, gate_id:str, timestamp:datetime, diff:float=60):
    results = {}
    
    try:
        
        if gate_id == 'null':
            results['error'] = {
                'status_code': "bad-request",
                'status_description': "delivery_id is not supposed to be null",
                'detail': 'delivery_id is null, please provide a valid delivery_id'
            }
            response.status_code = status.HTTP_400_BAD_REQUEST
            return results
    
        if not PlantEntity.objects.filter(entity_uid=gate_id).exists():
            results['error'] = {
                'status_code': "Not-Found",
                'status_description': f"entity_id {gate_id} is not found",
                'detail': 'please provide a valid gate_id'
            }
            response.status_code = status.HTTP_404_NOT_FOUND
            return results
        
        plant_entity = PlantEntity.objects.get(entity_uid=gate_id)
        if not DeliveryState.objects.filter(entity=plant_entity).exists():
            results['error'] = {
                'status_code': "Not-Found",
                'status_description': f"delivery_id for {gate_id} is not found",
                'detail': f'No delivery has been registered for {gate_id} yet'
            }
            response.status_code = status.HTTP_404_NOT_FOUND
            return results
            
            
        delivery = DeliveryState.objects.filter(entity=plant_entity).last()
        delivery_end = datetime.now(tz=timezone.utc)
        if delivery.delivery_status == 'on-going':
            results = {
                'delivery_id': delivery.id,
                'delivery_uid': delivery.delivery_id,
                'delivery_location': gate_id,
                'delivery_start': delivery.delivery_start.strftime(DATETIME_FORMAT),
                'delivery_end': delivery_end.strftime(DATETIME_FORMAT),
                'delivery_status': delivery.delivery_status, 
                'gate_status': 'Anlieferung im Bearbeitung' if  delivery.delivery_status != 'done' else 'Keine Anlieferung',
                'videos_dir': delivery.meta_info.get('videos', '') if delivery.meta_info is not None else '',
                'snapshots_dir': delivery.meta_info.get('snapshots', '') if delivery.meta_info is not None else '',
            } 
            
            return results


        if (timestamp.replace(tzinfo=timezone.utc) - delivery.delivery_end).seconds > diff:
            results = {
                "delivery_id": None,
                "delivery_end": delivery.delivery_end.strftime(DATETIME_FORMAT),
                "timestamp": timestamp.strftime(DATETIME_FORMAT),
                "diff": (timestamp.replace(tzinfo=timezone.utc) - delivery.delivery_end).seconds
            }
            
            return results
        
        results = {
            'delivery_id': delivery.id,
            'delivery_uid': delivery.delivery_id,
            'delivery_location': gate_id,
            'delivery_start': delivery.delivery_start.strftime(DATETIME_FORMAT),
            'delivery_end': delivery_end.strftime(DATETIME_FORMAT),
            'delivery_status': delivery.delivery_status, 
            'gate_status': 'Anlieferung im Bearbeitung' if  delivery.delivery_status != 'done' else 'Keine Anlieferung',
            'videos_dir': delivery.meta_info.get('videos', '') if delivery.meta_info is not None else '',
            'snapshots_dir': delivery.meta_info.get('snapshots', '') if delivery.meta_info is not None else '',
        } 
        
        connection.close()
        return results    
    
    except HTTPException as e:
        results['error'] = {
            "status_code": 404,
        }
        
        response.status_code = status.HTTP_404_NOT_FOUND
        return results
    
    except Exception as e:
        results['error'] = {
            'status_code': 500,
            "status_description": "Internal Server Error",
            "detail": str(e),
        }
        
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        return results