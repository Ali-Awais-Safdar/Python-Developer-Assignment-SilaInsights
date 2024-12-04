from pydantic import BaseModel
from typing import List
from typing import Optional

class StudentBase(BaseModel):
    name: str
    email: str
    subject_ids: List[int] = []

class TeacherBase(BaseModel):
    name: str
    email: str
    subject_ids: List[int] = []

class SubjectBase(BaseModel):
    name: str

class TeacherPatchSchema(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    subject_ids: Optional[List[int]] = None

class StudentPatchSchema(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    subject_ids: Optional[List[int]] = None