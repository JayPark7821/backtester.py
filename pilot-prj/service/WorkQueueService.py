import os
import aiofiles
from fastapi import UploadFile
from pathlib import Path
from app.models import mongodb
from app.models.WorkQueue import WorkQueueModel, QueueStatus


class WorkQueueService:
    BASE_DIR = Path(__file__).resolve().parent.parent.parent
    ECG_FILE_DIR = BASE_DIR / "files"

    if not os.path.exists(ECG_FILE_DIR):
        os.makedirs(ECG_FILE_DIR)

    async def append_patient_to_queue(self, file: UploadFile):
        work_queue_model = WorkQueueModel(patchSn=file.filename, status=QueueStatus.UPLOAD_REQUESTED)
        async with aiofiles.open(self.ECG_FILE_DIR / file.filename, 'wb') as out_file:
            content = await file.read()
            await out_file.write(content)

        await mongodb.engine.save(work_queue_model)
