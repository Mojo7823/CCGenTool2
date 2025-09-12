from typing import Optional
from pydantic import BaseModel, Field


class ComponentBase(BaseModel):
    class_name: str = Field(..., alias="class")
    family: Optional[str] = None
    component: Optional[str] = None
    component_name: Optional[str] = None
    element: Optional[str] = None
    element_item: Optional[str] = None

    class Config:
        populate_by_name = True
        from_attributes = True


class ComponentCreate(ComponentBase):
    pass


class ComponentUpdate(BaseModel):
    class_name: Optional[str] = Field(None, alias="class")
    family: Optional[str] = None
    component: Optional[str] = None
    component_name: Optional[str] = None
    element: Optional[str] = None
    element_item: Optional[str] = None

    class Config:
        populate_by_name = True
        from_attributes = True


class ComponentOut(ComponentBase):
    id: int
