import os
import os
import re
import shutil
import tempfile
import time
import uuid
from dataclasses import dataclass
from datetime import datetime
from contextlib import asynccontextmanager
from pathlib import Path
from typing import List, Optional

from fastapi import FastAPI, Depends, HTTPException, Query, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from sqlalchemy import text

from docx import Document
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
from docx.shared import Mm, Pt, RGBColor
from lxml import etree, html as lxml_html

from .database import Base, engine, get_db
from .models import (
    Component, FauDb, FcoDb, FcsDb, FdpDb, FiaDb, FmtDb, FprDb, FptDb, FruDb, FtaDb, FtpDb,
    AcoDb, AdvDb, AgdDb, AlcDb, ApeDb, AseDb, AteDb, AvaDb, ElementListDb
)
from .schemas import (
    ComponentCreate, ComponentOut, ComponentUpdate, XmlParseResponse, XmlImportResponse,
    ComponentFamilyOut, ElementListOut
)
from .xml_parser_service import XmlParserService
from pydantic import BaseModel, Field, ConfigDict


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    Base.metadata.create_all(bind=engine)
    yield
    # Shutdown (if needed)


app = FastAPI(title="CCGenTool2 API", lifespan=lifespan)

COVER_UPLOAD_ROOT = Path(os.getenv("COVER_UPLOAD_DIR", Path(tempfile.gettempdir()) / "ccgentool2_cover_uploads"))
COVER_UPLOAD_ROOT.mkdir(parents=True, exist_ok=True)
COVER_DOCX_ROOT = Path(os.getenv("COVER_DOCX_DIR", Path(tempfile.gettempdir()) / "ccgentool2_cover_docx"))
COVER_DOCX_ROOT.mkdir(parents=True, exist_ok=True)

SECURITY_DOCX_ROOT = Path(
    os.getenv("SECURITY_DOCX_DIR", Path(tempfile.gettempdir()) / "ccgentool2_security_docx")
)
SECURITY_DOCX_ROOT.mkdir(parents=True, exist_ok=True)
SECURITY_SECTIONS = {"sfr", "sar"}

USER_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]{1,64}$")


def get_user_upload_dir(user_id: str, *, create: bool = False) -> Path:
    if not USER_ID_PATTERN.match(user_id):
        raise HTTPException(status_code=400, detail="Invalid user identifier")

    user_dir = COVER_UPLOAD_ROOT / user_id
    if create:
        user_dir.mkdir(parents=True, exist_ok=True)
    return user_dir


def get_user_docx_dir(user_id: str, *, create: bool = False) -> Path:
    if not USER_ID_PATTERN.match(user_id):
        raise HTTPException(status_code=400, detail="Invalid user identifier")

    user_dir = COVER_DOCX_ROOT / user_id
    if create:
        user_dir.mkdir(parents=True, exist_ok=True)
    return user_dir


def get_security_docx_dir(user_id: str, section: str, *, create: bool = False) -> Path:
    if not USER_ID_PATTERN.match(user_id):
        raise HTTPException(status_code=400, detail="Invalid user identifier")

    if section not in SECURITY_SECTIONS:
        raise HTTPException(status_code=400, detail="Invalid preview section")

    section_dir = SECURITY_DOCX_ROOT / section
    user_dir = section_dir / user_id
    if create:
        user_dir.mkdir(parents=True, exist_ok=True)
    return user_dir


class CoverPreviewRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    user_id: str = Field(..., alias="user_id")
    title: Optional[str] = None
    version: Optional[str] = None
    revision: Optional[str] = None
    description: Optional[str] = None
    manufacturer: Optional[str] = None
    date: Optional[str] = None
    image_path: Optional[str] = Field(None, alias="image_path")


def _resolve_uploaded_image_path(image_path: Optional[str], user_id: str) -> Optional[Path]:
    if not image_path:
        return None

    expected_prefix = f"/cover/uploads/{user_id}/"
    if not image_path.startswith(expected_prefix):
        raise HTTPException(status_code=400, detail="Invalid image reference for preview generation")

    filename = Path(image_path).name
    upload_dir = get_user_upload_dir(user_id, create=False)
    image_file = upload_dir / filename
    if not image_file.exists():
        raise HTTPException(status_code=400, detail="Referenced cover image could not be found")
    return image_file


def _format_cover_date(date_value: Optional[str]) -> str:
    if not date_value:
        return "—"

    try:
        parsed = datetime.fromisoformat(date_value)
        return parsed.strftime("%d %B %Y")
    except ValueError:
        return date_value


def _build_cover_document(payload: CoverPreviewRequest) -> Path:
    image_file = _resolve_uploaded_image_path(payload.image_path, payload.user_id)
    docx_dir = get_user_docx_dir(payload.user_id, create=True)

    # Clear previous previews for the user to avoid stale documents piling up
    for existing in docx_dir.glob("*.docx"):
        existing.unlink(missing_ok=True)

    document = Document()
    section = document.sections[0]
    section.page_height = Mm(297)
    section.page_width = Mm(210)
    section.top_margin = Mm(20)
    section.bottom_margin = Mm(20)
    section.left_margin = Mm(25)
    section.right_margin = Mm(25)

    if image_file:
        image_paragraph = document.add_paragraph()
        image_paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
        run = image_paragraph.add_run()
        run.add_picture(str(image_file), width=Mm(120))
        image_paragraph.space_after = Pt(12)

    title_text = payload.title.strip() if payload.title else "Security Target Title"
    title_paragraph = document.add_paragraph()
    title_paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
    title_run = title_paragraph.add_run(title_text)
    title_run.font.size = Pt(24)
    title_run.font.bold = True
    title_paragraph.space_after = Pt(12)

    if payload.description:
        description_paragraph = document.add_paragraph(payload.description.strip())
        description_paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
        description_paragraph.space_after = Pt(18)

    info_items = [
        ("Version", payload.version.strip() if payload.version else "—"),
        ("Revision", payload.revision.strip() if payload.revision else "—"),
        ("Manufacturer/Laboratory", payload.manufacturer.strip() if payload.manufacturer else "—"),
        ("Date", _format_cover_date(payload.date)),
    ]

    for label, value in info_items:
        paragraph = document.add_paragraph()
        paragraph.space_after = Pt(6)
        run_label = paragraph.add_run(f"{label}: ")
        run_label.font.bold = True
        paragraph.add_run(value)

    filename = f"{uuid.uuid4().hex}.docx"
    output_path = docx_dir / filename
    document.save(str(output_path))
    return output_path


@dataclass
class RunFormatting:
    bold: bool = False
    italic: bool = False
    underline: bool = False
    strike: bool = False
    color: Optional[str] = None


class HtmlPreviewRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    user_id: str = Field(..., alias="user_id")
    html_content: str = Field(..., alias="html_content")


def _parse_css_color(style: str) -> Optional[str]:
    match = re.search(r"color\s*:\s*(#[0-9A-Fa-f]{6})", style)
    if match:
        return match.group(1)
    return None


def _extract_margin_left_points(style: str) -> Optional[float]:
    match = re.search(r"margin-left\s*:\s*([0-9.]+)px", style)
    if not match:
        return None
    try:
        return float(match.group(1)) * 0.75
    except ValueError:
        return None


def _apply_run_formatting(run, formatting: RunFormatting) -> None:
    run.font.bold = formatting.bold
    run.font.italic = formatting.italic
    run.font.underline = formatting.underline
    run.font.strike = formatting.strike
    if formatting.color:
        try:
            rgb = formatting.color.lstrip("#")
            if len(rgb) == 6:
                run.font.color.rgb = RGBColor(int(rgb[0:2], 16), int(rgb[2:4], 16), int(rgb[4:6], 16))
        except ValueError:
            pass


def _derive_child_formatting(element, base: RunFormatting) -> RunFormatting:
    formatting = RunFormatting(**base.__dict__)
    tag = element.tag.lower()

    if tag in {"strong", "b"}:
        formatting.bold = True
    if tag in {"em", "i"}:
        formatting.italic = True
    if tag in {"u"}:
        formatting.underline = True
    if tag in {"s", "strike"}:
        formatting.strike = True

    style = element.attrib.get("style", "")
    if style:
        color = _parse_css_color(style)
        if color:
            formatting.color = color
        if "underline" in style:
            formatting.underline = True
        if "line-through" in style:
            formatting.strike = True

    return formatting


BLOCK_TAGS = {"p", "div", "section", "article", "h1", "h2", "h3", "h4", "h5", "h6", "ul", "ol", "table"}


def _append_runs_from_node(paragraph, node, formatting: RunFormatting) -> None:
    if node.text and node.text.strip():
        run = paragraph.add_run(node.text.replace("\xa0", " "))
        _apply_run_formatting(run, formatting)

    for child in node:
        child_tag = child.tag.lower()
        if child_tag in BLOCK_TAGS:
            continue
        if child.tag.lower() == "br":
            paragraph.add_run().add_break()
        else:
            child_formatting = _derive_child_formatting(child, formatting)
            _append_runs_from_node(paragraph, child, child_formatting)

        if child.tail and child.tail.strip():
            run = paragraph.add_run(child.tail.replace("\xa0", " "))
            _apply_run_formatting(run, formatting)


def _apply_paragraph_styles(paragraph, element, base_indent: float = 0.0) -> None:
    style = element.attrib.get("style", "")
    total_indent = base_indent
    margin_indent = _extract_margin_left_points(style)
    if margin_indent is not None:
        total_indent += margin_indent
    if total_indent:
        paragraph.paragraph_format.left_indent = Pt(total_indent)
    if "text-align" in style:
        if "center" in style:
            paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
        elif "right" in style:
            paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.RIGHT


def _add_block_element(document: Document, element, indent: float = 0.0) -> None:
    tag = element.tag.lower()

    if tag in {"h1", "h2", "h3", "h4", "h5", "h6"}:
        paragraph = document.add_paragraph()
        base_format = RunFormatting(bold=True)
        size_map = {
            "h1": Pt(22),
            "h2": Pt(20),
            "h3": Pt(18),
            "h4": Pt(16),
            "h5": Pt(14),
            "h6": Pt(12),
        }
        paragraph.paragraph_format.space_after = Pt(6)
        _apply_paragraph_styles(paragraph, element, indent)
        _append_runs_from_node(paragraph, element, base_format)
        for run in paragraph.runs:
            run.font.size = size_map.get(tag, Pt(12))
    elif tag == "p":
        paragraph = document.add_paragraph()
        paragraph.paragraph_format.space_after = Pt(6)
        _apply_paragraph_styles(paragraph, element, indent)
        _append_runs_from_node(paragraph, element, RunFormatting())
    elif tag in {"div", "section", "article"}:
        style_indent = indent + (_extract_margin_left_points(element.attrib.get("style", "")) or 0.0)

        has_block_children = any(child.tag.lower() in BLOCK_TAGS for child in element)

        inline_content = (element.text and element.text.strip()) or any(
            child.tag.lower() not in BLOCK_TAGS and (child.text or child.tail)
            for child in element
        )

        if inline_content:
            paragraph = document.add_paragraph()
            paragraph.paragraph_format.space_after = Pt(6)
            _apply_paragraph_styles(paragraph, element, style_indent)
            _append_runs_from_node(paragraph, element, RunFormatting())

        for child in element:
            child_tag = child.tag.lower()
            if child_tag in BLOCK_TAGS:
                _add_block_element(document, child, indent=style_indent)
                if child.tail and child.tail.strip():
                    tail_paragraph = document.add_paragraph()
                    tail_paragraph.paragraph_format.space_after = Pt(6)
                    _apply_paragraph_styles(tail_paragraph, element, style_indent)
                    tail_paragraph.add_run(child.tail.replace("\xa0", " "))
    elif tag in {"ul", "ol"}:
        list_indent = indent + (_extract_margin_left_points(element.attrib.get("style", "")) or 0.0)
        for li in element.findall("li"):
            paragraph = document.add_paragraph()
            if tag == "ul":
                paragraph.style = "List Bullet"
            else:
                paragraph.style = "List Number"
            paragraph.paragraph_format.space_after = Pt(3)
            _apply_paragraph_styles(paragraph, li, list_indent)
            _append_runs_from_node(paragraph, li, RunFormatting())
    elif tag == "table":
        rows = element.findall(".//tr")
        if not rows:
            return

        table_indent = indent + (_extract_margin_left_points(element.attrib.get("style", "")) or 0.0)
        cols = 0
        for row in rows:
            row_cells = row.findall("th") or row.findall("td")
            cols = max(cols, len(row_cells))
        cols = max(cols, 2)

        table = document.add_table(rows=len(rows), cols=cols)
        table.autofit = True

        for row_idx, row in enumerate(rows):
            raw_cells = row.findall("th") or row.findall("td")
            if not raw_cells:
                continue

            if len(raw_cells) == 1 and cols > 1 and row_idx != 0:
                target_indices = [1]
            else:
                target_indices = list(range(len(raw_cells)))

            for idx, cell in enumerate(raw_cells):
                col_idx = target_indices[idx] if idx < len(target_indices) else idx
                col_idx = min(col_idx, cols - 1)
                paragraph = table.cell(row_idx, col_idx).paragraphs[0]
                paragraph.paragraph_format.space_after = Pt(3)
                if table_indent:
                    paragraph.paragraph_format.left_indent = Pt(table_indent)
                _append_runs_from_node(paragraph, cell, RunFormatting(bold=cell.tag.lower() == "th"))
    else:
        paragraph = document.add_paragraph()
        paragraph.paragraph_format.space_after = Pt(6)
        _apply_paragraph_styles(paragraph, element, indent)
        _append_runs_from_node(paragraph, element, RunFormatting())


def _build_security_document(html_content: str) -> Document:
    document = Document()
    section = document.sections[0]
    section.page_height = Mm(297)
    section.page_width = Mm(210)
    section.top_margin = Mm(20)
    section.bottom_margin = Mm(20)
    section.left_margin = Mm(25)
    section.right_margin = Mm(25)

    if not html_content or not html_content.strip():
        document.add_paragraph("No content available for preview.")
        return document

    try:
        fragment = lxml_html.fragment_fromstring(html_content, create_parent=True)
    except (etree.ParserError, ValueError):
        document.add_paragraph("Unable to render preview content.")
        return document

    for element in fragment:
        _add_block_element(document, element, indent=0.0)

    return document


def _generate_security_preview(user_id: str, section: str, html_content: str) -> Path:
    user_dir = get_security_docx_dir(user_id, section, create=True)
    for existing in user_dir.glob("*.docx"):
        existing.unlink(missing_ok=True)

    document = _build_security_document(html_content)
    filename = f"{uuid.uuid4().hex}.docx"
    output_path = user_dir / filename
    document.save(str(output_path))
    return output_path


def _cleanup_security_previews(user_id: str, section: str) -> None:
    try:
        user_dir = get_security_docx_dir(user_id, section, create=False)
    except HTTPException:
        return

    if user_dir.exists():
        shutil.rmtree(user_dir)

# CORS configuration: prefer regex if provided to allow any LAN IP on port 5173
origins = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",")
origin_regex = os.getenv(
    "CORS_ORIGIN_REGEX",
    None,
)

cors_kwargs = dict(
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if origin_regex:
    app.add_middleware(
        CORSMiddleware,
        allow_origin_regex=origin_regex,
        **cors_kwargs,
    )
else:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        **cors_kwargs,
    )

app.mount("/cover/uploads", StaticFiles(directory=str(COVER_UPLOAD_ROOT)), name="cover-uploads")
app.mount("/cover/docx", StaticFiles(directory=str(COVER_DOCX_ROOT)), name="cover-docx")
app.mount("/security/docx", StaticFiles(directory=str(SECURITY_DOCX_ROOT)), name="security-docx")


@app.get("/health")
def health(db: Session = Depends(get_db)):
    started = time.time()
    ok = True
    details = {}
    try:
        db.execute(text("SELECT 1"))
    except Exception as e:
        ok = False
        details["db_error"] = str(e)
    latency_ms = int((time.time() - started) * 1000)
    return {
        "status": "ok" if ok else "degraded",
        "latency_ms": latency_ms,
        "database_url": os.getenv("DATABASE_URL", "unset"),
        "timestamp": int(time.time()),
        "details": details,
    }


# CRUD endpoints
@app.get("/components", response_model=List[ComponentOut])
def list_components(
    q: Optional[str] = Query(None, description="Search across select fields"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    query = db.query(Component)
    if q:
        like = f"%{q}%"
        query = query.filter(
            (
                (Component.class_name.ilike(like))
                | (Component.family.ilike(like))
                | (Component.component.ilike(like))
                | (Component.component_name.ilike(like))
                | (Component.element.ilike(like))
                | (Component.element_item.ilike(like))
            )
        )
    return query.offset(skip).limit(limit).all()


@app.post("/components", response_model=ComponentOut, status_code=201)
def create_component(payload: ComponentCreate, db: Session = Depends(get_db)):
    item = Component(
        class_name=payload.class_name,
        family=payload.family,
        component=payload.component,
        component_name=payload.component_name,
        element=payload.element,
        element_item=payload.element_item,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@app.get("/components/{item_id}", response_model=ComponentOut)
def get_component(item_id: int, db: Session = Depends(get_db)):
    item = db.get(Component, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Not found")
    return item


@app.put("/components/{item_id}", response_model=ComponentOut)
def update_component(item_id: int, payload: ComponentUpdate, db: Session = Depends(get_db)):
    item = db.get(Component, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Not found")
    data = payload.model_dump(exclude_unset=True, by_alias=True)
    if "class" in data:
        item.class_name = data["class"]
        del data["class"]
    for k, v in data.items():
        setattr(item, k, v)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@app.delete("/components/{item_id}", status_code=204)
def delete_component(item_id: int, db: Session = Depends(get_db)):
    item = db.get(Component, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(item)
    db.commit()
    return None


# XML Parser endpoints
@app.post("/xml/parse", response_model=XmlParseResponse)
async def parse_xml_file(file: UploadFile = File(...)):
    """Parse an uploaded XML file and return the structured data."""
    if not file.filename or not file.filename.lower().endswith('.xml'):
        raise HTTPException(status_code=400, detail="File must be an XML file")
    
    try:
        content = await file.read()
        xml_content = content.decode('utf-8')
        
        parser = XmlParserService()
        result = parser.parse_xml_file(xml_content)
        
        return XmlParseResponse(**result)
    
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="File must be valid UTF-8 encoded XML")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error parsing XML: {str(e)}")


@app.post("/xml/import", response_model=XmlImportResponse)
async def import_xml_to_database(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Parse an XML file and import components to the database using family-specific tables."""
    if not file.filename or not file.filename.lower().endswith('.xml'):
        raise HTTPException(status_code=400, detail="File must be an XML file")
    
    try:
        content = await file.read()
        xml_content = content.decode('utf-8')
        
        parser = XmlParserService()
        result = parser.import_to_database(xml_content, db)
        
        return XmlImportResponse(**result)
    
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="File must be valid UTF-8 encoded XML")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing XML: {str(e)}")


# Family Table Endpoints
@app.get("/families")
def list_family_tables():
    """List all available family tables."""
    tables = {
        "functional": [
            {"name": "fau_db", "description": "Security audit (FAU)"},
            {"name": "fco_db", "description": "Communication (FCO)"},
            {"name": "fcs_db", "description": "Cryptographic support (FCS)"},
            {"name": "fdp_db", "description": "User data protection (FDP)"},
            {"name": "fia_db", "description": "Identification and authentication (FIA)"},
            {"name": "fmt_db", "description": "Security management (FMT)"},
            {"name": "fpr_db", "description": "Privacy (FPR)"},
            {"name": "fpt_db", "description": "Protection of the TSF (FPT)"},
            {"name": "fru_db", "description": "Resource utilisation (FRU)"},
            {"name": "fta_db", "description": "TOE access (FTA)"},
            {"name": "ftp_db", "description": "Trusted path/channels (FTP)"},
        ],
        "assurance": [
            {"name": "aco_db", "description": "Composition (ACO)"},
            {"name": "adv_db", "description": "Development (ADV)"},
            {"name": "agd_db", "description": "Guidance documents (AGD)"},
            {"name": "alc_db", "description": "Life-cycle support (ALC)"},
            {"name": "ape_db", "description": "Protection Profile evaluation (APE)"},
            {"name": "ase_db", "description": "Security Target evaluation (ASE)"},
            {"name": "ate_db", "description": "Tests (ATE)"},
            {"name": "ava_db", "description": "Vulnerability assessment (AVA)"},
        ],
        "special": [
            {"name": "element_list_db", "description": "Element list for colored XML elements"},
        ]
    }
    return tables


def get_family_table_model(table_name: str):
    """Get the SQLAlchemy model for a family table."""
    table_models = {
        "fau_db": FauDb, "fco_db": FcoDb, "fcs_db": FcsDb, "fdp_db": FdpDb,
        "fia_db": FiaDb, "fmt_db": FmtDb, "fpr_db": FprDb, "fpt_db": FptDb,
        "fru_db": FruDb, "fta_db": FtaDb, "ftp_db": FtpDb,
        "aco_db": AcoDb, "adv_db": AdvDb, "agd_db": AgdDb, "alc_db": AlcDb,
        "ape_db": ApeDb, "ase_db": AseDb, "ate_db": AteDb, "ava_db": AvaDb,
        "element_list_db": ElementListDb
    }
    return table_models.get(table_name)


@app.get("/families/{table_name}", response_model=List[ComponentFamilyOut])
def list_family_components(
    table_name: str,
    q: Optional[str] = Query(None, description="Search across select fields"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """List components from a specific family table."""
    model = get_family_table_model(table_name)
    if not model:
        raise HTTPException(status_code=404, detail="Table not found")
    
    query = db.query(model)
    if q and hasattr(model, 'class_field'):
        like = f"%{q}%"
        query = query.filter(
            (
                (model.class_field.ilike(like))
                | (model.family.ilike(like))
                | (model.component.ilike(like))
                | (model.component_name.ilike(like))
                | (model.element.ilike(like))
                | (model.element_item.ilike(like))
            )
        )
    return query.offset(skip).limit(limit).all()


@app.get("/element-lists", response_model=List[ElementListOut])
def list_element_lists(
    q: Optional[str] = Query(None, description="Search across select fields"),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """List elements from the element_list_db table."""
    query = db.query(ElementListDb)
    if q:
        like = f"%{q}%"
        query = query.filter(
            (
                (ElementListDb.element.ilike(like))
                | (ElementListDb.element_index.ilike(like))
                | (ElementListDb.item_list.ilike(like))
            )
        )
    return query.offset(skip).limit(limit).all()


@app.get("/element-lists/formatted/{element_id}")
def get_formatted_element_list(element_id: str, db: Session = Depends(get_db)):
    """Get formatted element list for a specific element ID (e.g., fau_gen.1.1)."""
    # Get all element list items for this element
    element_items = db.query(ElementListDb).filter(
        ElementListDb.element == element_id
    ).order_by(ElementListDb.element_index).all()
    
    if not element_items:
        raise HTTPException(status_code=404, detail="Element not found")
    
    # Get the main element text from the component table
    main_element = db.query(FauDb).filter(FauDb.element == element_id).first()
    if not main_element:
        # Try other tables if not found in FauDb
        for model in [FcoDb, FcsDb, FdpDb, FiaDb, FmtDb, FprDb, FptDb, FruDb, FtaDb, FtpDb]:
            main_element = db.query(model).filter(model.element == element_id).first()
            if main_element:
                break
    
    main_text = main_element.element_item if main_element else ""
    
    # Format the response
    formatted_items = []
    for item in element_items:
        formatted_items.append(item.item_list)
    
    return {
        "element": element_id,
        "main_text": main_text,
        "items": formatted_items,
        "formatted_display": f"{element_id} {main_text}\n" + "\n".join(formatted_items)
    }


@app.get("/families/{family_name}/formatted")
def get_formatted_family_elements(
    family_name: str,
    db: Session = Depends(get_db)
):
    """Get formatted element lists for all elements in a family (e.g., fau_gen)."""
    # Get all elements from the family
    family_elements = db.query(ElementListDb).filter(
        ElementListDb.element.like(f"{family_name}%")
    ).all()
    
    if not family_elements:
        raise HTTPException(status_code=404, detail="No elements found for family")
    
    # Group by element
    elements_grouped = {}
    for item in family_elements:
        element_id = item.element
        if element_id not in elements_grouped:
            elements_grouped[element_id] = []
        elements_grouped[element_id].append(item.item_list)
    
    result = []
    for element_id, items in elements_grouped.items():
        # Get main element text
        main_element = db.query(FauDb).filter(FauDb.element == element_id).first()
        if not main_element:
            # Try other tables
            for model in [FcoDb, FcsDb, FdpDb, FiaDb, FmtDb, FprDb, FptDb, FruDb, FtaDb, FtpDb]:
                main_element = db.query(model).filter(model.element == element_id).first()
                if main_element:
                    break
        
        main_text = main_element.element_item if main_element else ""
        
        result.append({
            "element": element_id,
            "main_text": main_text,
            "items": items,
            "formatted_display": f"{element_id} {main_text}\n" + "\n".join(items)
        })
    
    return result


@app.get("/families/{table_name}/count")
def count_family_components(table_name: str, db: Session = Depends(get_db)):
    """Get count of components in a family table."""
    model = get_family_table_model(table_name)
    if not model:
        raise HTTPException(status_code=404, detail="Table not found")
    
    count = db.query(model).count()
    return {"table": table_name, "count": count}


@app.post("/families/{table_name}", response_model=ComponentFamilyOut, status_code=201)
def create_family_component(table_name: str, payload: ComponentCreate, db: Session = Depends(get_db)):
    """Create a new component in a specific family table."""
    model = get_family_table_model(table_name)
    if not model:
        raise HTTPException(status_code=404, detail="Table not found")
    
    # Create item using the family-specific model
    item = model(
        class_field=payload.class_name,
        family=payload.family,
        component=payload.component,
        component_name=payload.component_name,
        element=payload.element,
        element_item=payload.element_item,
    )
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@app.put("/families/{table_name}/{item_id}", response_model=ComponentFamilyOut)
def update_family_component(table_name: str, item_id: int, payload: ComponentUpdate, db: Session = Depends(get_db)):
    """Update a component in a specific family table."""
    model = get_family_table_model(table_name)
    if not model:
        raise HTTPException(status_code=404, detail="Table not found")
    
    item = db.get(model, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Not found")
    
    data = payload.model_dump(exclude_unset=True, by_alias=True)
    if "class" in data:
        item.class_field = data["class"]
        del data["class"]
    for k, v in data.items():
        setattr(item, k, v)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


@app.delete("/families/{table_name}/{item_id}", status_code=204)
def delete_family_component(table_name: str, item_id: int, db: Session = Depends(get_db)):
    """Delete a component from a specific family table."""
    model = get_family_table_model(table_name)
    if not model:
        raise HTTPException(status_code=404, detail="Table not found")

    item = db.get(model, item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Not found")

    db.delete(item)
    db.commit()
    return None


@app.post("/cover/upload")
async def upload_cover_image(
    user_id: str = Query(..., alias="user_id"),
    file: UploadFile = File(...),
):
    """Store a temporary cover image for a user session."""

    user_dir = get_user_upload_dir(user_id, create=True)

    allowed_types = {"image/jpeg", "image/png", "image/bmp", "image/x-ms-bmp"}
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Only jpg, jpeg, png, or bmp files are allowed.")

    # Determine file extension based on mime type to avoid trusting filename blindly
    extension_map = {
        "image/jpeg": ".jpg",
        "image/png": ".png",
        "image/bmp": ".bmp",
        "image/x-ms-bmp": ".bmp",
    }
    suffix = extension_map[file.content_type]

    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    # Remove any existing files for the session to keep storage minimal
    if user_dir.exists():
        for existing in user_dir.iterdir():
            if existing.is_file():
                existing.unlink()

    filename = f"{uuid.uuid4().hex}{suffix}"
    destination = user_dir / filename
    with destination.open("wb") as buffer:
        buffer.write(data)

    return {"path": f"/cover/uploads/{user_id}/{filename}"}


@app.post("/cover/preview")
async def generate_cover_preview(payload: CoverPreviewRequest):
    if not payload.user_id:
        raise HTTPException(status_code=400, detail="User identifier is required")

    # Ensure the upload directory exists to maintain parity with the image uploads
    get_user_upload_dir(payload.user_id, create=True)

    output_path = _build_cover_document(payload)
    return {"path": f"/cover/docx/{payload.user_id}/{output_path.name}"}


@app.delete("/cover/upload/{user_id}")
async def cleanup_cover_images(user_id: str):
    """Delete all temporary cover images associated with a user session."""

    user_dir = get_user_upload_dir(user_id, create=False)
    if user_dir.exists():
        shutil.rmtree(user_dir)
    docx_dir = get_user_docx_dir(user_id, create=False)
    if docx_dir.exists():
        shutil.rmtree(docx_dir)
    return {"status": "deleted"}


@app.delete("/cover/preview/{user_id}")
async def cleanup_cover_preview(user_id: str):
    """Delete generated cover preview documents for a user session."""

    docx_dir = get_user_docx_dir(user_id, create=False)
    if docx_dir.exists():
        shutil.rmtree(docx_dir)
    return {"status": "deleted"}


@app.post("/security/sfr/preview")
async def generate_sfr_preview(payload: HtmlPreviewRequest):
    if not payload.user_id:
        raise HTTPException(status_code=400, detail="User identifier is required")

    output_path = _generate_security_preview(payload.user_id, "sfr", payload.html_content)
    return {"path": f"/security/docx/sfr/{payload.user_id}/{output_path.name}"}


@app.delete("/security/sfr/preview/{user_id}")
async def cleanup_sfr_preview(user_id: str):
    _cleanup_security_previews(user_id, "sfr")
    return {"status": "deleted"}


@app.post("/security/sar/preview")
async def generate_sar_preview(payload: HtmlPreviewRequest):
    if not payload.user_id:
        raise HTTPException(status_code=400, detail="User identifier is required")

    output_path = _generate_security_preview(payload.user_id, "sar", payload.html_content)
    return {"path": f"/security/docx/sar/{payload.user_id}/{output_path.name}"}


@app.delete("/security/sar/preview/{user_id}")
async def cleanup_sar_preview(user_id: str):
    _cleanup_security_previews(user_id, "sar")
    return {"status": "deleted"}
