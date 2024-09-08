from datetime import datetime

from odmantic import Model
from enum import Enum, auto


class QueueStatus(str, Enum):
    UPLOAD_REQUESTED = "UPLOAD_REQUESTED"
    UPLOADED = "UPLOADED"


class WorkQueueModel(Model):
    patchSn: str
    status: QueueStatus
    createdAt: datetime = datetime.now()
    updatedAt: datetime = datetime.now()
    model_config = {"collection": "work_queue", "arbitrary_types_allowed": True}
