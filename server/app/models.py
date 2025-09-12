from sqlalchemy import Column, Integer, String, Text
from .database import Base


class Component(Base):
    __tablename__ = "components"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    class_name = Column(String(100), nullable=False, index=True)
    family = Column(String(100), nullable=True, index=True)
    component = Column(String(100), nullable=True, index=True)
    component_name = Column(String(200), nullable=True)
    element = Column(String(200), nullable=True)
    element_item = Column(Text, nullable=True)  # Changed from String(200) to Text for longer content
