import logging
from fastapi import APIRouter, UploadFile, Depends

from app.service.WorkQueueService import WorkQueueService

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/v1/patient")
async def append_patient_to_queue(
        file: UploadFile,
        work_queue_service: WorkQueueService = Depends()
):
    await work_queue_service.append_patient_to_queue(file)
