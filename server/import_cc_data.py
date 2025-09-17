"""Utility script to import Common Criteria XML data into the application database."""
from __future__ import annotations

import argparse
from pathlib import Path
from typing import Sequence, Tuple, Type

from sqlalchemy import delete

from app.database import Base, SessionLocal, engine
from app.models import (
    ComponentFamilyBase,
    ElementListDb,
    FauDb,
    FcoDb,
    FcsDb,
    FdpDb,
    FiaDb,
    FmtDb,
    FprDb,
    FptDb,
    FruDb,
    FtaDb,
    FtpDb,
    AcoDb,
    AdvDb,
    AgdDb,
    AlcDb,
    ApeDb,
    AseDb,
    AteDb,
    AvaDb,
)
from app.xml_parser_service import XmlParserService


FUNCTIONAL_MODELS: Tuple[Type[ComponentFamilyBase], ...] = (
    FauDb,
    FcoDb,
    FcsDb,
    FdpDb,
    FiaDb,
    FmtDb,
    FprDb,
    FptDb,
    FruDb,
    FtaDb,
    FtpDb,
)

ASSURANCE_MODELS: Tuple[Type[ComponentFamilyBase], ...] = (
    AcoDb,
    AdvDb,
    AgdDb,
    AlcDb,
    ApeDb,
    AseDb,
    AteDb,
    AvaDb,
)

SPECIAL_MODELS: Tuple[Type[ElementListDb], ...] = (
    ElementListDb,
)


def clear_tables(models: Sequence[Type], *, session) -> None:
    """Delete all rows from the provided ORM models."""
    for model in models:
        session.execute(delete(model))


def import_xml(xml_path: Path, *, reset: bool = True) -> None:
    """Import the provided XML file into the configured database."""
    Base.metadata.create_all(bind=engine)

    session = SessionLocal()
    try:
        if reset:
            clear_tables(FUNCTIONAL_MODELS + ASSURANCE_MODELS + SPECIAL_MODELS, session=session)
            session.commit()

        xml_content = xml_path.read_text(encoding="utf-8")
        parser = XmlParserService()
        result = parser.import_to_database(xml_content, session)

        # XmlParserService commits internally, so just print the summary here.
        print("Import complete:")
        print(f"  Success: {result.get('success', False)}")
        print(f"  Components imported: {result.get('components_imported', 0)}")
        print(f"  Components failed: {result.get('components_failed', 0)}")
        print(f"  Element lists imported: {result.get('element_lists_imported', 0)}")
        tables_used = result.get('tables_used') or []
        if tables_used:
            print(f"  Tables populated: {', '.join(sorted(tables_used))}")
        if result.get('errors'):
            print("  Errors:")
            for err in result['errors']:
                print(f"    - {err}")
    finally:
        session.close()


def default_xml_path() -> Path:
    repo_root = Path(__file__).resolve().parent.parent
    return repo_root / "oldparser" / "cc.xml"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Import Common Criteria XML data into the database")
    parser.add_argument(
        "--xml",
        dest="xml",
        default=str(default_xml_path()),
        help="Path to the Common Criteria XML file (defaults to repository cc.xml)",
    )
    parser.add_argument(
        "--skip-reset",
        dest="skip_reset",
        action="store_true",
        help="Do not clear existing requirement tables before importing",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    xml_path = Path(args.xml)

    if not xml_path.exists():
        raise SystemExit(f"XML file not found: {xml_path}")

    reset = not args.skip_reset
    action = "Importing" if not reset else "Resetting tables and importing"
    print(f"{action} data from {xml_path}")
    import_xml(xml_path, reset=reset)


if __name__ == "__main__":
    main()
