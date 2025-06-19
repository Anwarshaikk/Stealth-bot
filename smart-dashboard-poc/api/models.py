from pydantic import BaseModel
from typing import List, Optional
from enum import Enum
from uuid import UUID

class CandidateStatus(str, Enum):
    PENDING = "Pending"
    REVIEWING = "Reviewing"
    APPROVED = "Approved"
    REJECTED = "Rejected"

class ApplicationStatus(str, Enum):
    APPLIED = "Applied"
    INTERVIEW = "Interview"
    OFFER = "Offer"
    REJECTED = "Rejected"

class Candidate(BaseModel):
    candidate_id: str
    name: Optional[str] = None
    email: Optional[str] = None
    mobile_number: Optional[str] = None
    skills: List[str] = []
    college_name: Optional[List[str]] = None
    degree: Optional[List[str]] = None
    designation: Optional[List[str]] = None
    company_names: Optional[List[str]] = None
    total_experience: Optional[float] = None
    status: CandidateStatus = CandidateStatus.PENDING
    resume_file_path: Optional[str] = None

class Job(BaseModel):
    title: str
    company: str
    location: str
    url: str
    description: Optional[str] = None
    salary: Optional[str] = None
    posted_date: Optional[str] = None
    score: Optional[float] = None

class ApplyRequest(BaseModel):
    candidate_id: str
    jobs: List[Job]

class Application(BaseModel):
    application_id: UUID
    candidate_id: str
    job_title: str
    company: str
    job_url: str
    status: ApplicationStatus = ApplicationStatus.APPLIED
    created_at: str
    updated_at: str

class ApplicationStatusUpdate(BaseModel):
    status: ApplicationStatus 