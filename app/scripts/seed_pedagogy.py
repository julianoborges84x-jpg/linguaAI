from app.core.database import SessionLocal
from app.services.pedagogy_seed import ensure_pedagogical_seed


def run() -> None:
    db = SessionLocal()
    try:
        ensure_pedagogical_seed(db)
        print('Pedagogical seed applied successfully.')
    finally:
        db.close()


if __name__ == '__main__':
    run()
