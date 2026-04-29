import json
from datetime import datetime, timezone
from functools import cache
from pathlib import Path
from typing import Annotated, List, Optional, Protocol

from fastapi import Depends
from fastapi_babel import _
from fastapi_mail import (
    ConnectionConfig,
    FastMail,
    MessageSchema,
    MessageType,
)
from jinja2 import Environment, FileSystemLoader
from pydantic import NameEmail

from backend.common.exceptions.errors import (
    SendEmailError,
)
from backend.common.logging import log
from backend.common.resources import strings
from backend.core.config import settings
from backend.core.path_conf import BASE_PATH
from backend.utils.dynamic_import import get_all_templates


class EmailBackend(Protocol):
    async def send_email(
        self,
        recipients: list[NameEmail],
        subject: str = "",
        body: Optional[str] = None,
        subtype: MessageType = MessageType.plain,
        context: Optional[dict[str, str]] = None,
        template_name: Optional[str] = None,
    ) -> None: ...

    async def send_with_template(
        self,
        subject: str,
        recipients: List[NameEmail],
        template_name: str,
        context: dict[str, str],
        subtype: MessageType = MessageType.html,
    ) -> None: ...


class MultiTemplateConnectionConfig(ConnectionConfig):
    TEMPLATE_FOLDERS: list[Path] = get_all_templates()

    #  fastapi mail stub
    TEMPLATE_FOLDER: Path = Path()

    def template_engine(self) -> Environment:
        loader = FileSystemLoader(self.TEMPLATE_FOLDERS)
        env = Environment(loader=loader)
        env.globals.update(_=_)
        return env


class Mailer(EmailBackend):
    def __init__(self, fast_mail: FastMail) -> None:
        self.fast_mail = fast_mail

    async def send_with_template(
        self,
        subject: str,
        recipients: List[NameEmail],
        template_name: str,
        context: dict[str, str],
        subtype: MessageType = MessageType.html,
    ) -> None:

        await self.send_email(
            recipients=recipients,
            subject=subject,
            template_name=template_name,
            context=context,
            subtype=subtype,
        )

    async def send_email(
        self,
        recipients: list[NameEmail],
        subject: str = "",
        body: Optional[str] = None,
        subtype: MessageType = MessageType.plain,
        context: Optional[dict[str, str]] = None,
        template_name: Optional[str] = None,
    ) -> None:
        try:
            await self._send_email(
                subject=subject,
                recipients=recipients,
                body=body,
                subtype=subtype,
                context=context,
                template_name=template_name,
            )
            log.debug(
                strings.SEND_MESSAGE_SUCCESS,
                subject,
                recipients,
            )
        except Exception as e:
            log.error(strings.SEND_MESSAGE_ERROR, e)
            raise SendEmailError(
                strings.SEND_MESSAGE_ERROR,
            ) from e

    async def _send_email(
        self,
        recipients: list[NameEmail],
        subject: str = "",
        body: Optional[str] = None,
        subtype: MessageType = MessageType.plain,
        context: Optional[dict[str, str]] = None,
        template_name: Optional[str] = None,
    ) -> None:
        message = self.get_message(
            subject=subject,
            recipients=recipients,
            body=body,
            context=context,
            subtype=subtype,
        )
        await self.fast_mail.send_message(
            message,
            template_name=template_name,
        )

    def get_message(
        self,
        recipients: list[NameEmail],
        subject: str = "",
        body: Optional[str] = None,
        subtype: MessageType = MessageType.plain,
        context: Optional[dict[str, str]] = None,
    ) -> MessageSchema:
        return MessageSchema(
            subject=subject,
            recipients=recipients,
            body=body,
            template_body=context,
            subtype=subtype,
        )


class FileEmailBackend:
    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self.base_dir.mkdir(parents=True, exist_ok=True)

    async def send_with_template(
        self,
        subject: str,
        recipients: List[NameEmail],
        template_name: str,
        context: dict[str, str],
        subtype: MessageType = MessageType.html,
    ) -> None:
        await self.send_email(
            recipients=recipients,
            subject=subject,
            context=context,
            template_name=template_name,
        )

    async def send_email(
        self,
        recipients: list[NameEmail],
        subject: str = "",
        body: Optional[str] = None,
        subtype: MessageType = MessageType.plain,
        context: Optional[dict[str, str]] = None,
        template_name: Optional[str] = None,
    ) -> None:
        ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_%f")

        data = {
            "subject": subject,
            "recipients": [r.email for r in recipients],
            "body": body,
            "context": context,
            "template": template_name,
        }

        file = self.base_dir / f"{ts}.json"
        file.write_text(json.dumps(data, indent=2, ensure_ascii=False))


@cache
def get_email_backend() -> EmailBackend:
    if settings.mail.backend == "smtp":
        conf = MultiTemplateConnectionConfig(
            MAIL_USERNAME=settings.mail.username,
            MAIL_PASSWORD=settings.mail.password,
            MAIL_FROM=settings.mail.from_email,
            MAIL_PORT=settings.mail.port,
            MAIL_SERVER=settings.mail.server,
            MAIL_STARTTLS=settings.mail.mail_starttls,
            MAIL_SSL_TLS=settings.mail.mail_ssl_tls,
            USE_CREDENTIALS=settings.mail.use_credentials,
            VALIDATE_CERTS=settings.mail.validate_certs,
        )
        fast_mail = FastMail(conf)
        return Mailer(fast_mail)

    return FileEmailBackend(
        base_dir=BASE_PATH,
    )


EmailBackendDep = Annotated[EmailBackend, Depends(get_email_backend)]
