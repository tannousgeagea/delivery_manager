import json
import time
import uuid
from typing import Callable
from typing import Annotated
from pathlib import Path
from datetime import datetime
from datetime import datetime, timedelta
from typing import Union
from typing import Any
from typing import Dict
from typing import AnyStr
from celery.result import AsyncResult
from typing import Optional
from typing import  List
from fastapi import Request
from fastapi import BackgroundTasks
from fastapi.routing import APIRoute
from pydantic import BaseModel, Field
from fastapi import FastAPI, Depends, APIRouter, Request, Header, Response
from events_api.tasks.delivery import log_delivery

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


class ApiResponse(BaseModel):
    status: str
    task_id: str
    data: Optional[Dict[AnyStr, Any]] = None


class ApiRequest(BaseModel):
    request: Optional[Dict[AnyStr, Any]] = None


class DeliveryEventRequest(BaseModel):
    """
    Pydantic model to validate delivery event requests coming from the state machine.
    """
    event_uid: str = Field(..., max_length=250)
    event_name: str = Field(..., max_length=255)
    location: str = Field(..., description="ID of the PlantEntity where the event occurred.")
    timestamp: datetime = Field(..., description="The timestamp when the event occurred.")
    status: str = Field(..., max_length=255)
    description: Optional[str] = Field(None, max_length=250)
    meta_info: Optional[Dict] = Field(None, description="Additional information in JSON format.")


router = APIRouter(
    prefix="/api/v1",
    tags=["DeliveryAPI"],
    route_class=TimedRoute,
    responses={404: {"description": "Not found"}},
)


@router.api_route(
    "/delivery/event", methods=["POST"], tags=["DeliveryAPI"]
)
async def create_delivery(
    response: Response,
    event: DeliveryEventRequest = Depends(),
    x_request_id: Annotated[str | None, Header()] = None,
) -> dict:
    
    task = log_delivery.create_delivery.apply_async(args=(event,), task_id=x_request_id)
    result = {"status": "received", "task_id": task.id, "data": {}}

    return result

@router.api_route(
    "/delivery/task/status/{task_id}", methods=["GET"], tags=["DeliveryAPI"]
    )
async def get_task_status(task_id: str):
    """
    Endpoint to check the status of a Celery task.
    """
    task_result = AsyncResult(task_id)
    if task_result.state == 'FAILURE':
        return {"status": task_result.state, "error": str(task_result.result)}
    
    return {"status": task_result.state, "result": task_result.result}