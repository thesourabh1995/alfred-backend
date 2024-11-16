from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any

@dataclass
class AvatarUrls:
    _48x48: str
    _24x24: str
    _16x16: str
    _32x32: str

@dataclass
class User:
    self: str
    accountId: str
    emailAddress: str
    avatarUrls: AvatarUrls
    displayName: str
    active: bool
    timeZone: str
    accountType: str

@dataclass
class Project:
    self: str
    id: str
    key: str
    name: str
    projectTypeKey: str
    simplified: bool
    avatarUrls: Dict[str, str]

@dataclass
class IssueType:
    self: str
    id: str
    description: str
    iconUrl: str
    name: str
    subtask: bool
    avatarId: int
    entityId: str
    hierarchyLevel: int

@dataclass
class Priority:
    self: str
    iconUrl: str
    name: str
    id: str

@dataclass
class StatusCategory:
    self: str
    id: int
    key: str
    colorName: str
    name: str

@dataclass
class Status:
    self: str
    description: str
    iconUrl: str
    name: str
    id: str
    statusCategory: StatusCategory

@dataclass
class DescriptionContent:
    type: str
    version: int
    content: List[Dict[str, Any]]

@dataclass
class IssueFields:
    statuscategorychangedate: str
    issuetype: IssueType
    timespent: Optional[Any]
    project: Project
    fixVersions: List[Any]
    resolution: Optional[Any]
    priority: Priority
    labels: List[str]
    created: str
    updated: str
    description: DescriptionContent
    summary: str
    creator: User
    assignee: Optional[User]
    status: Status

@dataclass
class Issue:
    expand: str
    id: str
    self: str
    key: str
    fields: IssueFields

@dataclass
class Issues:
    issues: List[Issue]