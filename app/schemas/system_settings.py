from datetime import time

from pydantic import BaseModel, ConfigDict


class SystemSettingsBase(BaseModel):
    cutoff_time: time
    day_rollover_time: time


class SystemSettingsRead(SystemSettingsBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
