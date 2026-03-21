from .auth import router as auth
from .users import router as users
from .users import legacy_router as users_legacy
from .features import router as features
from .mentor import router as mentor
from .languages import router as languages
from .daily_messages import router as daily_messages
from .motivation import router as motivation
from .billing import router as billing
from .learna import router as learna
from .sessions import router as sessions
from .growth import router as growth
from .growth import legacy_router as growth_legacy
from .immersion import router as immersion
from .real_life import router as real_life
from .daily_challenge import router as daily_challenge
from .referral import router as referral
from .pedagogy import router as pedagogy
from .realtime import router as realtime

__all__ = [
    "auth",
    "users",
    "users_legacy",
    "features",
    "mentor",
    "languages",
    "daily_messages",
    "motivation",
    "billing",
    "learna",
    "sessions",
    "growth",
    "growth_legacy",
    "immersion",
    "real_life",
    "daily_challenge",
    "referral",
    "pedagogy",
    "realtime",
]
