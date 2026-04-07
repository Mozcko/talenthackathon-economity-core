from datetime import datetime, date
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict

class AchievementBase(BaseModel):
    code: str
    name: str
    description: str
    xp_reward: int

class AchievementResponse(AchievementBase):
    model_config = ConfigDict(from_attributes=True)

class UserAchievementResponse(BaseModel):
    achievement_code: str
    unlocked_at: datetime
    definition: AchievementResponse

    model_config = ConfigDict(from_attributes=True)

class UserGamificationProfileResponse(BaseModel):
    user_id: str
    total_xp: int
    current_tier: str
    current_streak: int
    max_streak: int
    last_activity_date: Optional[date]
    
    # Campos calculados para el frontend
    next_tier: Optional[str] = None
    xp_to_next_tier: Optional[int] = None
    progress_percentage: float = 0.0

    model_config = ConfigDict(from_attributes=True)

class MilestoneResponse(BaseModel):
    message: str
    target_xp: Optional[int] = None
    progress: float
    is_completed: bool
