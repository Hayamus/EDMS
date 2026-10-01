from pydantic import BaseModel, Field, field_validator
from app.teams.models.team_member import UserRole

class TeamCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)

class AddMember(BaseModel):
    user_id: int

class ChangeRole(BaseModel):
    role: UserRole

class TeamOut(BaseModel):
    id: int
    name: str

    model_config = {'from_attributes': True}

class TeamMemberOut(BaseModel):
    id: int
    user_id: int
    team_id: int
    role: UserRole

    model_config = {'from_attributes': True}

class TeamMemberUserOut(BaseModel):
    id: int
    email: str
    first_name: str
    last_name: str

    model_config = {'from_attributes': True}

class TeamMemberWithUserOut(TeamMemberOut):
    user: TeamMemberUserOut