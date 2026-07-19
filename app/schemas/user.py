from pydantic import BaseModel, ConfigDict, EmailStr


class UserBase(BaseModel):
    slack_user_id: str
    team_id: str
    name: str
    email: EmailStr


class UserCreate(UserBase):
    pass


class UserUpdate(BaseModel):
    name: str | None = None
    email: EmailStr | None = None


class UserRead(UserBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
