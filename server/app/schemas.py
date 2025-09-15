from typing import Optional, List, Dict, Any
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


# Schema for family-specific component tables
class ComponentFamilyBase(BaseModel):
    class_field: Optional[str] = Field(None, alias="class")
    family: Optional[str] = None
    component: Optional[str] = None
    component_name: Optional[str] = None
    element: Optional[str] = None
    element_item: Optional[str] = None

    class Config:
        populate_by_name = True
        from_attributes = True


class ComponentFamilyCreate(ComponentFamilyBase):
    pass


class ComponentFamilyUpdate(BaseModel):
    class_field: Optional[str] = Field(None, alias="class")
    family: Optional[str] = None
    component: Optional[str] = None
    component_name: Optional[str] = None
    element: Optional[str] = None
    element_item: Optional[str] = None

    class Config:
        populate_by_name = True
        from_attributes = True


class ComponentFamilyOut(ComponentFamilyBase):
    id: int


# Schema for element list table
class ElementListBase(BaseModel):
    element: Optional[str] = None
    element_index: Optional[str] = None
    item_list: Optional[str] = None
    color: Optional[str] = None

    class Config:
        from_attributes = True


class ElementListCreate(ElementListBase):
    pass


class ElementListUpdate(BaseModel):
    element: Optional[str] = None
    element_index: Optional[str] = None
    item_list: Optional[str] = None
    color: Optional[str] = None

    class Config:
        from_attributes = True


class ElementListOut(ElementListBase):
    id: int


# XML Parser Schemas
class XmlParseResponse(BaseModel):
    success: bool
    message: Optional[str] = None
    data: Optional[Dict[str, Any]] = None
    components: Optional[List[Dict[str, str]]] = None


class XmlImportResponse(BaseModel):
    success: bool
    message: str
    components_imported: int
    components_failed: int
    element_lists_imported: Optional[int] = 0
    errors: Optional[List[str]] = None
    tables_used: Optional[List[str]] = None  # Track which tables were used
