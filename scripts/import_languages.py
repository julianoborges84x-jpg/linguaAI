import argparse
import csv
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.models.language import Language


def load_tab(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="latin-1") as f:
        reader = csv.DictReader(f, delimiter="\t")
        return list(reader)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", required=True, help="SQLAlchemy DB URL")
    parser.add_argument("--language-codes", required=True, help="Path to ISO 639-3 LanguageCodes.tab")
    parser.add_argument("--country-codes", required=True, help="Path to ISO 639-3 CountryCodes.tab")
    parser.add_argument("--family-map", required=False, help="CSV file with iso_code,family")
    args = parser.parse_args()

    lang_rows = load_tab(Path(args.language_codes))
    country_rows = load_tab(Path(args.country_codes))

    country_by_id = {r["Id"]: r for r in country_rows}

    family_map: dict[str, str] = {}
    if args.family_map:
        with Path(args.family_map).open("r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                family_map[row["iso_code"]] = row["family"]

    engine = create_engine(args.db)
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    session = SessionLocal()
    try:
        inserted = 0
        for row in lang_rows:
            code = row.get("Id", "").strip()
            name = row.get("Ref_Name", "").strip()
            country_id = row.get("Country_ID", "").strip()
            country = country_by_id.get(country_id, {})
            region = country.get("Name", "Unknown")
            family = family_map.get(code, "Unknown")

            if not code or not name:
                continue

            exists = session.get(Language, code)
            if exists:
                exists.name = name
                exists.region = region
                exists.family = family
            else:
                session.add(Language(iso_code=code, name=name, region=region, family=family))
            inserted += 1

        session.commit()
        print(f"Imported {inserted} languages")
    finally:
        session.close()


if __name__ == "__main__":
    main()
