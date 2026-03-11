import argparse
import sys

from app.core.config import settings
from app.core.database import SessionLocal
from app.models.user import PlanEnum, User


def _is_dev_environment() -> bool:
    return settings.app_env.strip().lower() in {"dev", "development", "test"}


def promote_user_to_pro(email: str, level: int, xp_total: int) -> int:
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        if not user:
            print(f"User not found: {email}")
            return 1

        user.plan = PlanEnum.PRO
        user.level = max(level, user.level or 0)
        user.xp_total = max(xp_total, user.xp_total or 0)
        user.subscription_status = "active"
        db.commit()
        print(
            f"OK: user={user.email} plan={user.plan.value} level={user.level} xp_total={user.xp_total}"
        )
        return 0
    finally:
        db.close()


def main() -> int:
    parser = argparse.ArgumentParser(description="Promove usuário para plano PRO (somente ambiente dev/test).")
    parser.add_argument("--email", required=True, help="Email do usuário")
    parser.add_argument("--level", type=int, default=5, help="Nível mínimo para setar")
    parser.add_argument("--xp-total", type=int, default=1400, help="XP total mínimo para setar")
    args = parser.parse_args()

    if not _is_dev_environment():
        print(f"Blocked: APP_ENV '{settings.app_env}' is not allowed for this script.")
        return 2

    return promote_user_to_pro(args.email, args.level, args.xp_total)


if __name__ == "__main__":
    raise SystemExit(main())
