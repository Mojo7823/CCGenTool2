import json
import os
import re
import shutil
import tempfile
import time
import uuid
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
from html import escape
from lxml import html as lxml_html

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
SFR_DOCX_ROOT = Path(os.getenv("SFR_DOCX_DIR", Path(tempfile.gettempdir()) / "ccgentool2_sfr_docx"))
SFR_DOCX_ROOT.mkdir(parents=True, exist_ok=True)
SAR_DOCX_ROOT = Path(os.getenv("SAR_DOCX_DIR", Path(tempfile.gettempdir()) / "ccgentool2_sar_docx"))
SAR_DOCX_ROOT.mkdir(parents=True, exist_ok=True)
ST_INTRO_DATA_ROOT = Path(
    os.getenv("ST_INTRO_DATA_DIR", Path(tempfile.gettempdir()) / "ccgentool2_st_intro_data")
)
ST_INTRO_DATA_ROOT.mkdir(parents=True, exist_ok=True)
ST_INTRO_DOCX_ROOT = Path(
    os.getenv("ST_INTRO_DOCX_DIR", Path(tempfile.gettempdir()) / "ccgentool2_st_intro_docx")
)
ST_INTRO_DOCX_ROOT.mkdir(parents=True, exist_ok=True)

USER_ID_PATTERN = re.compile(r"^[A-Za-z0-9_-]{1,64}$")


def get_user_upload_dir(user_id: str, *, create: bool = False) -> Path:
    if not USER_ID_PATTERN.match(user_id):
        raise HTTPException(status_code=400, detail="Invalid user identifier")

    user_dir = COVER_UPLOAD_ROOT / user_id
    if create:
        user_dir.mkdir(parents=True, exist_ok=True)
    return user_dir


def _get_preview_docx_dir(root: Path, user_id: str, *, create: bool = False) -> Path:
    if not USER_ID_PATTERN.match(user_id):
        raise HTTPException(status_code=400, detail="Invalid user identifier")

    user_dir = root / user_id
    if create:
        user_dir.mkdir(parents=True, exist_ok=True)
    return user_dir


def get_user_docx_dir(user_id: str, *, create: bool = False) -> Path:
    return _get_preview_docx_dir(COVER_DOCX_ROOT, user_id, create=create)


def _get_session_data_file(user_id: str, *, create: bool = False) -> Path:
    if not USER_ID_PATTERN.match(user_id):
        raise HTTPException(status_code=400, detail="Invalid user identifier")

    user_dir = ST_INTRO_DATA_ROOT / user_id
    if create:
        user_dir.mkdir(parents=True, exist_ok=True)
    return user_dir / "data.json"


def _load_session_data(user_id: str) -> dict:
    session_file = _get_session_data_file(user_id, create=False)
    if not session_file.exists():
        return {}

    try:
        with session_file.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except json.JSONDecodeError:
        return {}


def _save_session_data(user_id: str, data: dict) -> None:
    session_file = _get_session_data_file(user_id, create=True)
    with session_file.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2)


def _update_session_section(user_id: str, section: str, payload: dict) -> dict:
    data = _load_session_data(user_id)
    data[section] = payload
    _save_session_data(user_id, data)
    return payload


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


class StReferenceSaveRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    user_id: str = Field(..., alias="user_id")
    st_title: Optional[str] = Field(None, alias="st_title")
    st_version: Optional[str] = Field(None, alias="st_version")
    st_date: Optional[str] = Field(None, alias="st_date")
    author: Optional[str] = None


class ToeReferenceSaveRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    user_id: str = Field(..., alias="user_id")
    toe_name: Optional[str] = Field(None, alias="toe_name")
    toe_version: Optional[str] = Field(None, alias="toe_version")
    toe_identification: Optional[str] = Field(None, alias="toe_identification")
    toe_type: Optional[str] = Field(None, alias="toe_type")


class ToeOverviewSaveRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    user_id: str = Field(..., alias="user_id")
    overview: Optional[str] = None
    toe_type: Optional[str] = Field(None, alias="toe_type")
    toe_usage: Optional[str] = Field(None, alias="toe_usage")
    toe_security_features: Optional[str] = Field(None, alias="toe_security_features")
    non_toe_hw: Optional[str] = Field(None, alias="non_toe_hw")


class ToeDescriptionSaveRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    user_id: str = Field(..., alias="user_id")
    physical_scope: Optional[str] = Field(None, alias="physical_scope")
    logical_scope: Optional[str] = Field(None, alias="logical_scope")


class StIntroductionPreviewRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    user_id: str = Field(..., alias="user_id")


class HtmlPreviewRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    user_id: str = Field(..., alias="user_id")
    html_content: str = Field(..., alias="html_content")


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


def _normalize_string(value: Optional[str]) -> str:
    return value.strip() if isinstance(value, str) else ""


def _sanitize_rich_text(value: Optional[str]) -> str:
    if not value or not value.strip():
        return "<p>&mdash;</p>"

    try:
        fragment = lxml_html.fragment_fromstring(value, create_parent=True)
    except (ValueError, TypeError):
        return f"<p>{escape(value)}</p>"

    for element in fragment.xpath('.//script|.//style'):
        parent = element.getparent()
        if parent is not None:
            parent.remove(element)

    serialized = "".join(
        lxml_html.tostring(child, encoding="unicode") for child in fragment
    ).strip()

    return serialized or "<p>&mdash;</p>"


def _format_multiline_text(value: Optional[str]) -> str:
    if not value:
        return "&mdash;"
    lines = [escape(line) for line in value.splitlines()]
    if not any(line.strip() for line in lines):
        return "&mdash;"
    joined = "<br/>".join(lines)
    return joined or "&mdash;"


def _build_cover_html(payload: CoverPreviewRequest) -> str:
    rows = [
        ("Security Target Title", escape(_normalize_string(payload.title)) or "&mdash;"),
        ("Security Target Version", escape(_normalize_string(payload.version)) or "&mdash;"),
        ("Revision", escape(_normalize_string(payload.revision)) or "&mdash;"),
        ("Additional Description", _format_multiline_text(payload.description)),
        (
            "Manufacturer/Laboratory Name",
            escape(_normalize_string(payload.manufacturer)) or "&mdash;",
        ),
        ("Date", _format_cover_date(_normalize_string(payload.date))),
    ]

    if payload.image_path:
        rows.insert(0, ("Cover Image", escape(payload.image_path)))

    table_rows = "".join(
        f"<tr><th>{label}</th><td>{value}</td></tr>" for label, value in rows
    )

    return (
        "<h2>Cover</h2>"
        "<table>"
        "<tbody>"
        f"{table_rows}"
        "</tbody>"
        "</table>"
    )


def _build_st_reference_html(payload: StReferenceSaveRequest) -> str:
    title_cell = escape(_normalize_string(payload.st_title)) or "&mdash;"
    version_cell = escape(_normalize_string(payload.st_version)) or "&mdash;"
    date_cell = _format_cover_date(_normalize_string(payload.st_date))
    author_cell = _format_multiline_text(payload.author)

    return "".join(
        [
            "<h2>1. Security Target Introduction</h2>",
            "<p>This section presents the following information required for a Common Criteria (CC) evaluation:</p>",
            "<ul>",
            "<li>Identifies the Security Target (ST) and the Target of Evaluation (TOE)</li>",
            "<li>Specifies the security target conventions</li>",
            "<li>Describes the organization of the security target</li>",
            "</ul>",
            "<h3>1.1 ST Reference</h3>",
            "<table>",
            "<tbody>",
            f"<tr><th>ST Title</th><td>{title_cell}</td></tr>",
            f"<tr><th>ST Version</th><td>{version_cell}</td></tr>",
            f"<tr><th>ST Date</th><td>{date_cell}</td></tr>",
            f"<tr><th>Author</th><td>{author_cell}</td></tr>",
            "</tbody>",
            "</table>",
            "<p>Table 1 Security Target reference</p>",
        ]
    )


def _build_toe_reference_html(payload: ToeReferenceSaveRequest) -> str:
    name_cell = _sanitize_rich_text(payload.toe_name)
    version_cell = _sanitize_rich_text(payload.toe_version)
    identification_cell = _sanitize_rich_text(payload.toe_identification)
    type_cell = _sanitize_rich_text(payload.toe_type)

    return "".join(
        [
            "<h3>1.2 TOE Reference</h3>",
            "<table>",
            "<tbody>",
            f"<tr><th>TOE Name</th><td>{name_cell}</td></tr>",
            f"<tr><th>TOE Version</th><td>{version_cell}</td></tr>",
            f"<tr><th>TOE Identification</th><td>{identification_cell}</td></tr>",
            f"<tr><th>TOE Type</th><td>{type_cell}</td></tr>",
            "</tbody>",
            "</table>",
            "<p>Table 2 TOE reference</p>",
        ]
    )


def _build_toe_overview_html(payload: ToeOverviewSaveRequest) -> str:
    overview_html = _sanitize_rich_text(payload.overview)
    toe_type_html = _sanitize_rich_text(payload.toe_type)
    usage_html = _sanitize_rich_text(payload.toe_usage)
    security_features_html = _sanitize_rich_text(payload.toe_security_features)
    non_toe_html = _sanitize_rich_text(payload.non_toe_hw)

    return "".join(
        [
            "<h3>1.3 TOE Overview</h3>",
            overview_html,
            "<h4>1.3.1 TOE Type</h4>",
            toe_type_html,
            "<h4>1.3.2 TOE Usage</h4>",
            usage_html,
            "<h4>1.3.3 TOE Major Security Features</h4>",
            security_features_html,
            "<h4>1.3.4 Non-TOE Hardware/Software/Firmware</h4>",
            non_toe_html,
        ]
    )


def _build_toe_description_html(payload: ToeDescriptionSaveRequest) -> str:
    physical_html = _sanitize_rich_text(payload.physical_scope)
    logical_html = _sanitize_rich_text(payload.logical_scope)

    return "".join(
        [
            "<h3>1.4 TOE Description</h3>",
            "<h4>1.4.1 TOE Physical Scope</h4>",
            physical_html,
            "<h4>1.4.2 TOE Logical Scope</h4>",
            logical_html,
        ]
    )


def _save_cover_section(payload: CoverPreviewRequest) -> dict:
    html = _build_cover_html(payload)
    section = {
        "fields": {
            "title": _normalize_string(payload.title),
            "version": _normalize_string(payload.version),
            "revision": _normalize_string(payload.revision),
            "description": _normalize_string(payload.description),
            "manufacturer": _normalize_string(payload.manufacturer),
            "date": _normalize_string(payload.date),
        },
        "image_path": payload.image_path or "",
        "html": html,
    }
    return _update_session_section(payload.user_id, "cover", section)


def _save_st_reference_section(payload: StReferenceSaveRequest) -> dict:
    html = _build_st_reference_html(payload)
    section = {
        "fields": {
            "st_title": _normalize_string(payload.st_title),
            "st_version": _normalize_string(payload.st_version),
            "st_date": _normalize_string(payload.st_date),
            "author": _normalize_string(payload.author),
        },
        "html": html,
    }
    return _update_session_section(payload.user_id, "st_reference", section)


def _save_toe_reference_section(payload: ToeReferenceSaveRequest) -> dict:
    html = _build_toe_reference_html(payload)
    section = {
        "fields": {
            "toe_name": _normalize_string(payload.toe_name),
            "toe_version": _normalize_string(payload.toe_version),
            "toe_identification": _normalize_string(payload.toe_identification),
            "toe_type": _normalize_string(payload.toe_type),
        },
        "rich_text": {
            "toe_name": payload.toe_name or "",
            "toe_version": payload.toe_version or "",
            "toe_identification": payload.toe_identification or "",
            "toe_type": payload.toe_type or "",
        },
        "html": html,
    }
    return _update_session_section(payload.user_id, "toe_reference", section)


def _save_toe_overview_section(payload: ToeOverviewSaveRequest) -> dict:
    html = _build_toe_overview_html(payload)
    section = {
        "fields": {
            "overview": payload.overview or "",
            "toe_type": payload.toe_type or "",
            "toe_usage": payload.toe_usage or "",
            "toe_security_features": payload.toe_security_features or "",
            "non_toe_hw": payload.non_toe_hw or "",
        },
        "html": html,
    }
    return _update_session_section(payload.user_id, "toe_overview", section)


def _save_toe_description_section(payload: ToeDescriptionSaveRequest) -> dict:
    html = _build_toe_description_html(payload)
    section = {
        "fields": {
            "physical_scope": payload.physical_scope or "",
            "logical_scope": payload.logical_scope or "",
        },
        "html": html,
    }
    return _update_session_section(payload.user_id, "toe_description", section)


def _px_to_points(px_value: float) -> float:
    # Approximate conversion assuming 96px = 72pt
    return px_value * 0.75


def _parse_margin_left(style: Optional[str]) -> Optional[float]:
    if not style:
        return None
    match = re.search(r"margin-left\s*:\s*([0-9.]+)px", style)
    if not match:
        return None
    try:
        return _px_to_points(float(match.group(1)))
    except ValueError:
        return None


def _parse_color(value: Optional[str]) -> Optional[RGBColor]:
    if not value:
        return None

    color = value.strip().lower()
    if color.startswith("#"):
        hex_value = color[1:]
        if len(hex_value) == 3:
            hex_value = "".join(ch * 2 for ch in hex_value)
        if len(hex_value) == 6:
            try:
                r = int(hex_value[0:2], 16)
                g = int(hex_value[2:4], 16)
                b = int(hex_value[4:6], 16)
                return RGBColor(r, g, b)
            except ValueError:
                return None
    elif color.startswith("rgb"):
        numbers = re.findall(r"[0-9]{1,3}", color)
        if len(numbers) >= 3:
            try:
                r, g, b = (min(255, max(0, int(num))) for num in numbers[:3])
                return RGBColor(r, g, b)
            except ValueError:
                return None
    return None


def _collect_inline_styles(element) -> dict:
    styles = {
        "bold": False,
        "italic": False,
        "underline": False,
        "strike": False,
        "color": None,
        "size": None,
    }

    tag = (element.tag or "").lower()
    if tag in {"strong", "b"}:
        styles["bold"] = True
    if tag in {"em", "i"}:
        styles["italic"] = True
    if tag in {"u", "ins"}:
        styles["underline"] = True
    if tag in {"s", "strike", "del"}:
        styles["strike"] = True

    style_attr = element.get("style", "")
    for rule in style_attr.split(";"):
        rule = rule.strip().lower()
        if not rule:
            continue
        if "bold" in rule:
            styles["bold"] = True
        if "italic" in rule:
            styles["italic"] = True
        if "underline" in rule:
            styles["underline"] = True
        if "line-through" in rule:
            styles["strike"] = True
        if rule.startswith("color"):
            parts = rule.split(":", 1)
            if len(parts) == 2:
                parsed = _parse_color(parts[1])
                if parsed:
                    styles["color"] = parsed

    color_attr = element.get("color")
    parsed_color = _parse_color(color_attr)
    if parsed_color:
        styles["color"] = parsed_color

    return styles


def _apply_styles_to_run(run, styles: dict):
    if styles.get("bold"):
        run.bold = True
    if styles.get("italic"):
        run.italic = True
    if styles.get("underline"):
        run.underline = True
    if styles.get("strike"):
        run.strike = True
    color = styles.get("color")
    if color:
        run.font.color.rgb = color
    size = styles.get("size")
    if size:
        run.font.size = size


def _merge_styles(parent: dict, child: dict) -> dict:
    merged = parent.copy()
    for key, value in child.items():
        if key in {"color", "size"}:
            if value is not None:
                merged[key] = value
        elif value:
            merged[key] = True
    return merged


def _append_inline_content(paragraph, element, inherited_styles: Optional[dict] = None):
    styles = _collect_inline_styles(element)
    combined_styles = _merge_styles(inherited_styles or {
        "bold": False,
        "italic": False,
        "underline": False,
        "strike": False,
        "color": None,
        "size": None,
    }, styles)

    text = element.text or ""
    if text:
        run = paragraph.add_run(text.replace("\xa0", " "))
        _apply_styles_to_run(run, combined_styles)

    for child in element:
        _append_inline_content(paragraph, child, combined_styles)
        tail = child.tail or ""
        if tail:
            run = paragraph.add_run(tail.replace("\xa0", " "))
            _apply_styles_to_run(run, combined_styles)


def _append_block_element(document: Document, element, inherited_indent: Optional[float] = None):
    tag = (element.tag or "").lower()
    style_attr = element.get("style")
    margin_left = _parse_margin_left(style_attr)
    indent = margin_left if margin_left is not None else inherited_indent

    heading_map = {
        "h1": Pt(24),
        "h2": Pt(20),
        "h3": Pt(18),
        "h4": Pt(16),
        "h5": Pt(14),
        "h6": Pt(12),
    }

    if tag in heading_map:
        paragraph = document.add_paragraph()
        if indent:
            paragraph.paragraph_format.left_indent = Pt(indent)
        base_styles = {
            "bold": True,
            "italic": False,
            "underline": False,
            "strike": False,
            "color": None,
            "size": heading_map[tag],
        }
        _append_inline_content(paragraph, element, base_styles)
        return

    if tag == "p":
        text_content = (element.text or "") + "".join(
            (child.text or "") + (child.tail or "") for child in element
        )
        if not text_content.strip() and not element.findall("*"):
            document.add_paragraph()
            return

        paragraph = document.add_paragraph()
        if indent:
            paragraph.paragraph_format.left_indent = Pt(indent)
        _append_inline_content(paragraph, element)
        return

    if tag in {"div", "section"}:
        child_indent = indent if indent is not None else inherited_indent
        text = (element.text or "").strip()
        if text:
            paragraph = document.add_paragraph(text)
            if child_indent:
                paragraph.paragraph_format.left_indent = Pt(child_indent)
        for child in element:
            _append_block_element(document, child, child_indent)
        tail = (element.tail or "").strip()
        if tail:
            paragraph = document.add_paragraph(tail)
            if child_indent:
                paragraph.paragraph_format.left_indent = Pt(child_indent)
        return

    if tag in {"ul", "ol"}:
        items = [child for child in element if (child.tag or "").lower() == "li"]
        for idx, child in enumerate(items, start=1):
            paragraph = document.add_paragraph()
            if indent:
                paragraph.paragraph_format.left_indent = Pt(indent)
            prefix = "• " if tag == "ul" else f"{idx}. "
            run = paragraph.add_run(prefix)
            _append_inline_content(paragraph, child, {
                "bold": False,
                "italic": False,
                "underline": False,
                "strike": False,
                "color": None,
                "size": None,
            })
        return

    if tag == "table":
        rows = [row for row in element.findall(".//tr")]
        if not rows:
            return

        max_cells = 0
        table_rows = []
        for row in rows:
            cells = [cell for cell in row if (cell.tag or "").lower() in {"th", "td"}]
            table_rows.append(cells)
            max_cells = max(max_cells, len(cells))

        if max_cells == 0:
            return

        table = document.add_table(rows=len(table_rows), cols=max_cells)
        table.style = "Table Grid"

        for row_index, cells in enumerate(table_rows):
            for col_index, cell in enumerate(cells):
                if col_index >= max_cells:
                    continue
                paragraph = table.cell(row_index, col_index).paragraphs[0]
                paragraph.text = ""
                _append_inline_content(paragraph, cell)
                if (cell.tag or "").lower() == "th":
                    for run in paragraph.runs:
                        run.bold = True
        return

    if tag == "br":
        document.add_paragraph()
        return

    # Fallback: treat unknown block elements as paragraphs.
    paragraph = document.add_paragraph()
    if indent:
        paragraph.paragraph_format.left_indent = Pt(indent)
    _append_inline_content(paragraph, element)


def _append_html_to_document(document: Document, html_content: str):
    if not html_content or not html_content.strip():
        return

    try:
        fragment = lxml_html.fragment_fromstring(html_content, create_parent=True)
    except (ValueError, TypeError):
        paragraph = document.add_paragraph(html_content)
        return

    for child in fragment:
        _append_block_element(document, child)


def _build_html_preview_document(html_content: str, user_id: str, root: Path) -> Path:
    docx_dir = _get_preview_docx_dir(root, user_id, create=True)

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

    _append_html_to_document(document, html_content)

    filename = f"{uuid.uuid4().hex}.docx"
    output_path = docx_dir / filename
    document.save(str(output_path))
    return output_path

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
app.mount("/security/sfr/docx", StaticFiles(directory=str(SFR_DOCX_ROOT)), name="sfr-docx")
app.mount("/security/sar/docx", StaticFiles(directory=str(SAR_DOCX_ROOT)), name="sar-docx")
app.mount(
    "/st-introduction/docx",
    StaticFiles(directory=str(ST_INTRO_DOCX_ROOT)),
    name="st-introduction-docx",
)


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

    if payload.image_path:
        _resolve_uploaded_image_path(payload.image_path, payload.user_id)

    _save_cover_section(payload)

    output_path = _build_cover_document(payload)
    return {"path": f"/cover/docx/{payload.user_id}/{output_path.name}"}


@app.post("/st-introduction/cover")
async def store_cover_section(payload: CoverPreviewRequest):
    if not payload.user_id:
        raise HTTPException(status_code=400, detail="User identifier is required")

    get_user_upload_dir(payload.user_id, create=True)

    if payload.image_path:
        _resolve_uploaded_image_path(payload.image_path, payload.user_id)

    section = _save_cover_section(payload)
    return section


@app.post("/st-introduction/st-reference")
async def store_st_reference_section(payload: StReferenceSaveRequest):
    if not payload.user_id:
        raise HTTPException(status_code=400, detail="User identifier is required")

    section = _save_st_reference_section(payload)
    return section


@app.post("/st-introduction/toe-reference")
async def store_toe_reference_section(payload: ToeReferenceSaveRequest):
    if not payload.user_id:
        raise HTTPException(status_code=400, detail="User identifier is required")

    section = _save_toe_reference_section(payload)
    return section


@app.post("/st-introduction/toe-overview")
async def store_toe_overview_section(payload: ToeOverviewSaveRequest):
    if not payload.user_id:
        raise HTTPException(status_code=400, detail="User identifier is required")

    section = _save_toe_overview_section(payload)
    return section


@app.post("/st-introduction/toe-description")
async def store_toe_description_section(payload: ToeDescriptionSaveRequest):
    if not payload.user_id:
        raise HTTPException(status_code=400, detail="User identifier is required")

    section = _save_toe_description_section(payload)
    return section


def _default_cover_section() -> dict:
    return {"fields": {"title": "", "version": "", "revision": "", "description": "", "manufacturer": "", "date": ""}, "image_path": "", "html": ""}


def _merge_section(default: dict, stored: Optional[dict]) -> dict:
    if not stored:
        return default

    merged = {**default}
    for key, value in stored.items():
        if key == "fields" and isinstance(value, dict):
            merged_fields = {**default.get("fields", {})}
            merged_fields.update(value)
            merged["fields"] = merged_fields
        else:
            merged[key] = value
    return merged


@app.get("/st-introduction/{user_id}")
async def get_st_introduction(user_id: str):
    if not USER_ID_PATTERN.match(user_id):
        raise HTTPException(status_code=400, detail="Invalid user identifier")

    data = _load_session_data(user_id)

    defaults = {
        "cover": _default_cover_section(),
        "st_reference": {"fields": {"st_title": "", "st_version": "", "st_date": "", "author": ""}, "html": ""},
        "toe_reference": {
            "fields": {"toe_name": "", "toe_version": "", "toe_identification": "", "toe_type": ""},
            "rich_text": {"toe_name": "", "toe_version": "", "toe_identification": "", "toe_type": ""},
            "html": "",
        },
        "toe_overview": {
            "fields": {
                "overview": "",
                "toe_type": "",
                "toe_usage": "",
                "toe_security_features": "",
                "non_toe_hw": "",
            },
            "html": "",
        },
        "toe_description": {
            "fields": {"physical_scope": "", "logical_scope": ""},
            "html": "",
        },
    }

    response = {
        key: _merge_section(defaults[key], data.get(key)) if key in data else defaults[key]
        for key in defaults
    }

    return response


def _collect_st_introduction_html(user_id: str) -> str:
    data = _load_session_data(user_id)
    sections = [
        data.get("cover", {}).get("html", ""),
        data.get("st_reference", {}).get("html", ""),
        data.get("toe_reference", {}).get("html", ""),
        data.get("toe_overview", {}).get("html", ""),
        data.get("toe_description", {}).get("html", ""),
    ]

    combined = "\n".join(section for section in sections if section)
    if not combined.strip():
        raise HTTPException(status_code=400, detail="No ST Introduction content available for preview")
    return combined


@app.post("/st-introduction/preview")
async def generate_st_introduction_preview(payload: StIntroductionPreviewRequest):
    if not payload.user_id:
        raise HTTPException(status_code=400, detail="User identifier is required")

    combined_html = _collect_st_introduction_html(payload.user_id)
    output_path = _build_html_preview_document(combined_html, payload.user_id, ST_INTRO_DOCX_ROOT)
    return {"path": f"/st-introduction/docx/{payload.user_id}/{output_path.name}"}

@app.post("/security/sfr/preview")
async def generate_sfr_preview(payload: HtmlPreviewRequest):
    if not payload.user_id:
        raise HTTPException(status_code=400, detail="User identifier is required")

    output_path = _build_html_preview_document(payload.html_content, payload.user_id, SFR_DOCX_ROOT)
    return {"path": f"/security/sfr/docx/{payload.user_id}/{output_path.name}"}


@app.post("/security/sar/preview")
async def generate_sar_preview(payload: HtmlPreviewRequest):
    if not payload.user_id:
        raise HTTPException(status_code=400, detail="User identifier is required")

    output_path = _build_html_preview_document(payload.html_content, payload.user_id, SAR_DOCX_ROOT)
    return {"path": f"/security/sar/docx/{payload.user_id}/{output_path.name}"}


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


@app.delete("/security/sfr/preview/{user_id}")
async def cleanup_sfr_preview(user_id: str):
    docx_dir = _get_preview_docx_dir(SFR_DOCX_ROOT, user_id, create=False)
    if docx_dir.exists():
        shutil.rmtree(docx_dir)
    return {"status": "deleted"}


@app.delete("/security/sar/preview/{user_id}")
async def cleanup_sar_preview(user_id: str):
    docx_dir = _get_preview_docx_dir(SAR_DOCX_ROOT, user_id, create=False)
    if docx_dir.exists():
        shutil.rmtree(docx_dir)
    return {"status": "deleted"}


@app.delete("/st-introduction/docx/{user_id}")
async def cleanup_st_introduction_preview(user_id: str):
    docx_dir = _get_preview_docx_dir(ST_INTRO_DOCX_ROOT, user_id, create=False)
    if docx_dir.exists():
        shutil.rmtree(docx_dir)
    return {"status": "deleted"}
