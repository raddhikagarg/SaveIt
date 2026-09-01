"""
JWT Authentication + Platform Account Linking
"""

import random
import string
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models import User, LinkCode, Opportunity

from app.schemas import (
    RegisterRequest,
    LoginRequest,
    TokenResponse,
    UserOut,
    LinkCodeGenerateRequest,
    LinkCodeOut,
)

from app.utils.security import (
    create_access_token,
    get_current_user,
    hash_password,
    verify_password,
)
router = APIRouter(prefix="/auth", tags=["auth"])

PLATFORM_INSTRUCTIONS = {
    "telegram": "Send this code to @SaveItBot on Telegram as: /link {code}",
    "instagram": "DM this code to @SaveIt on Instagram as: LINK {code}",
    "whatsapp": "Send this code as a WhatsApp message to our number: LINK {code}",
}


# ---------------- AUTH ---------------- #

@router.post("/register", response_model=TokenResponse)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == payload.email).first()

    if existing:
        raise HTTPException(
            status_code=400,
            detail="An account with this email already exists",
        )

    user = User(
        email=payload.email,
        name=payload.name,
        password_hash=hash_password(payload.password),
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(user.id)

    return TokenResponse(
        access_token=token,
        user=user,
    )


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()

    if (
        not user
        or not user.password_hash
        or not verify_password(payload.password, user.password_hash)
    ):
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password",
        )

    token = create_access_token(user.id)

    return TokenResponse(
        access_token=token,
        user=user,
    )


@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user


# ---------------- LINK CODES ---------------- #

@router.post("/link/generate", response_model=LinkCodeOut)
def generate_link_code(
    payload: LinkCodeGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    code = "".join(
        random.choices(string.ascii_uppercase + string.digits, k=6)
    )

    expires_at = datetime.utcnow() + timedelta(
        minutes=settings.LINK_CODE_EXPIRE_MINUTES
    )

    link_code = LinkCode(
        user_id=current_user.id,
        code=code,
        platform=payload.platform,
        expires_at=expires_at,
    )

    db.add(link_code)
    db.commit()

    instructions = PLATFORM_INSTRUCTIONS.get(
        payload.platform.value,
        "",
    ).format(code=code)

    return LinkCodeOut(
        code=code,
        platform=payload.platform,
        expires_at=expires_at,
        instructions=instructions,
    )


def resolve_link_code(
    db: Session,
    code: str,
    platform_field: str,
    platform_value: str,
) -> User | None:
    """
    Called from webhooks.py when a platform sends a link code.
    Links the platform account to the logged-in web account.
    """

    link_code = (
        db.query(LinkCode)
        .filter(
            LinkCode.code == code,
            LinkCode.used == False,
        )
        .first()
    )

    if not link_code or link_code.expires_at < datetime.utcnow():
        return None

    target_user = (
        db.query(User)
        .filter(User.id == link_code.user_id)
        .first()
    )

    if not target_user:
        return None

    # Merge anonymous account if it already exists
    existing = (
        db.query(User)
        .filter(getattr(User, platform_field) == platform_value)
        .first()
    )

    if existing and existing.id != target_user.id:
        (
            db.query(Opportunity)
            .filter(Opportunity.user_id == existing.id)
            .update({"user_id": target_user.id})
        )

        db.delete(existing)

    setattr(target_user, platform_field, platform_value)

    link_code.used = True

    db.commit()

    return target_user