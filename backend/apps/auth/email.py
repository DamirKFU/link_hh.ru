from fastapi import (
    BackgroundTasks,
)
from fastapi_babel import _
from fastapi_mail import NameEmail

from backend.common.email import EmailBackend
from backend.core.config import settings
from backend.utils.urls import build_frontend_url


def send_reset_password_email(
    background_tasks: BackgroundTasks,
    mailer: EmailBackend,
    email: str,
    token: str,
) -> None:
    link = build_frontend_url(
        settings.frontend_route.reset_password_path,
        token=token,
    )

    background_tasks.add_task(
        mailer.send_with_template,
        subject=_("FORGOT_PASSWORD_SUBJECT_TEXT"),
        recipients=[NameEmail(email, email)],
        template_name="auth/reset_password.html",
        context={
            "link": link,
        },
    )


def send_verification_email(
    background_tasks: BackgroundTasks,
    mailer: EmailBackend,
    email: str,
    token: str,
) -> None:
    link = build_frontend_url(
        settings.frontend_route.reset_password_path,
        token=token,
    )

    background_tasks.add_task(
        mailer.send_with_template,
        subject=_("VERIFICATION_SUBJECT_TEXT"),
        recipients=[NameEmail(email, email)],
        template_name="auth/verification.html",
        context={
            "link": link,
        },
    )
