from sqlalchemy import Column, Integer, String, Text
from .database import Base


class Component(Base):
    __tablename__ = "components"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    class_name = Column(String(100), nullable=False, index=True)
    family = Column(String(100), nullable=True, index=True)
    component = Column(String(100), nullable=True, index=True)
    component_name = Column(Text, nullable=True)  # Changed to Text to handle longer content
    element = Column(String(200), nullable=True)
    element_item = Column(Text, nullable=True)


# Base class for component family tables
class ComponentFamilyBase:
    """Base class for component family tables with common structure"""
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    class_field = Column("class", String(255), nullable=True, index=True)  # Use class_field to avoid Python keyword
    family = Column(String(255), nullable=True, index=True)
    component = Column(String(255), nullable=True, index=True)
    component_name = Column(Text, nullable=True)
    element = Column(String(255), nullable=True, index=True)
    element_item = Column(Text, nullable=True)


# Functional Requirements Tables (f-class tables)
class FauDb(ComponentFamilyBase, Base):
    """Security audit (FAU) family"""
    __tablename__ = "fau_db"


class FcoDb(ComponentFamilyBase, Base):
    """Communication (FCO) family"""
    __tablename__ = "fco_db"


class FcsDb(ComponentFamilyBase, Base):
    """Cryptographic support (FCS) family"""
    __tablename__ = "fcs_db"


class FdpDb(ComponentFamilyBase, Base):
    """User data protection (FDP) family"""
    __tablename__ = "fdp_db"


class FiaDb(ComponentFamilyBase, Base):
    """Identification and authentication (FIA) family"""
    __tablename__ = "fia_db"


class FmtDb(ComponentFamilyBase, Base):
    """Security management (FMT) family"""
    __tablename__ = "fmt_db"


class FprDb(ComponentFamilyBase, Base):
    """Privacy (FPR) family"""
    __tablename__ = "fpr_db"


class FptDb(ComponentFamilyBase, Base):
    """Protection of the TSF (FPT) family"""
    __tablename__ = "fpt_db"


class FruDb(ComponentFamilyBase, Base):
    """Resource utilisation (FRU) family"""
    __tablename__ = "fru_db"


class FtaDb(ComponentFamilyBase, Base):
    """TOE access (FTA) family"""
    __tablename__ = "fta_db"


class FtpDb(ComponentFamilyBase, Base):
    """Trusted path/channels (FTP) family"""
    __tablename__ = "ftp_db"


# Assurance Requirements Tables (a-class tables)
class AcoDb(ComponentFamilyBase, Base):
    """Composition (ACO) family"""
    __tablename__ = "aco_db"


class AdvDb(ComponentFamilyBase, Base):
    """Development (ADV) family"""
    __tablename__ = "adv_db"


class AgdDb(ComponentFamilyBase, Base):
    """Guidance documents (AGD) family"""
    __tablename__ = "agd_db"


class AlcDb(ComponentFamilyBase, Base):
    """Life-cycle support (ALC) family"""
    __tablename__ = "alc_db"


class ApeDb(ComponentFamilyBase, Base):
    """Protection Profile evaluation (APE) family"""
    __tablename__ = "ape_db"


class AseDb(ComponentFamilyBase, Base):
    """Security Target evaluation (ASE) family"""
    __tablename__ = "ase_db"


class AteDb(ComponentFamilyBase, Base):
    """Tests (ATE) family"""
    __tablename__ = "ate_db"


class AvaDb(ComponentFamilyBase, Base):
    """Vulnerability assessment (AVA) family"""
    __tablename__ = "ava_db"


# Special table for element lists with colors
class ElementListDb(Base):
    """Element list database for special handling of colored XML elements"""
    __tablename__ = "element_list_db"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    element = Column(String(255), nullable=True, index=True)
    element_index = Column(String(255), nullable=True, index=True, unique=True)
    item_list = Column(Text, nullable=True)
    color = Column(String(50), nullable=True)  # For handling colored elements
