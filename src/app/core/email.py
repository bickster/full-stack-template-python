"""Email service for sending notifications."""

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from typing import Optional

import aiosmtplib
from jinja2 import Environment, FileSystemLoader, select_autoescape

from app.core.config import settings
from app.core.logging import logger

# Email templates directory
TEMPLATES_DIR = Path(__file__).parent.parent / "templates" / "email"


class EmailService:
    """Service for sending emails."""

    def __init__(self) -> None:
        """Initialize email service."""
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER
        self.smtp_password = settings.SMTP_PASSWORD
        self.from_email = settings.EMAILS_FROM_EMAIL
        self.from_name = settings.EMAILS_FROM_NAME
        self.use_tls = settings.SMTP_TLS

        # Set up Jinja2 for email templates
        self.template_env = Environment(
            loader=FileSystemLoader(TEMPLATES_DIR),
            autoescape=select_autoescape(["html", "xml"]),
        )

    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
    ) -> bool:
        """Send an email.

        Args:
            to_email: Recipient email address
            subject: Email subject
            html_content: HTML content of the email
            text_content: Plain text content (optional)

        Returns:
            bool: True if email was sent successfully
        """
        if not all([self.smtp_host, self.smtp_user, self.smtp_password]):
            logger.warning(
                "email_not_configured", to_email=to_email, subject=subject
            )
            return False

        try:
            # Create message
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = f"{self.from_name} <{self.from_email}>"
            message["To"] = to_email

            # Add text and HTML parts
            if text_content:
                part1 = MIMEText(text_content, "plain")
                message.attach(part1)

            part2 = MIMEText(html_content, "html")
            message.attach(part2)

            # Send email
            async with aiosmtplib.SMTP(
                hostname=self.smtp_host,
                port=self.smtp_port,
                use_tls=self.use_tls,
            ) as smtp:
                await smtp.login(self.smtp_user, self.smtp_password)
                await smtp.send_message(message)

            logger.info(
                "email_sent",
                to_email=to_email,
                subject=subject,
            )
            return True

        except Exception as e:
            logger.error(
                "email_send_failed",
                to_email=to_email,
                subject=subject,
                error=str(e),
                exc_info=True,
            )
            return False

    async def send_password_reset_email(
        self,
        to_email: str,
        username: str,
        reset_token: str,
    ) -> bool:
        """Send password reset email.

        Args:
            to_email: Recipient email address
            username: User's username
            reset_token: Password reset token

        Returns:
            bool: True if email was sent successfully
        """
        reset_url = (
            f"{settings.FRONTEND_URL}/reset-password?token={reset_token}"
        )

        # Render email template
        template = self.template_env.get_template("password_reset.html")
        html_content = template.render(
            username=username,
            reset_url=reset_url,
            app_name=settings.APP_NAME,
        )

        # Plain text version
        text_content = f"""
Hello {username},

You have requested to reset your password for {settings.APP_NAME}.

Please click the link below to reset your password:
{reset_url}

This link will expire in 1 hour.

If you did not request this password reset, please ignore this email.

Best regards,
{settings.APP_NAME} Team
        """.strip()

        return await self.send_email(
            to_email=to_email,
            subject=f"Password Reset Request - {settings.APP_NAME}",
            html_content=html_content,
            text_content=text_content,
        )

    async def send_welcome_email(
        self,
        to_email: str,
        username: str,
    ) -> bool:
        """Send welcome email to new user.

        Args:
            to_email: Recipient email address
            username: User's username

        Returns:
            bool: True if email was sent successfully
        """
        # Render email template
        template = self.template_env.get_template("welcome.html")
        html_content = template.render(
            username=username,
            app_name=settings.APP_NAME,
            login_url=f"{settings.FRONTEND_URL}/login",
        )

        # Plain text version
        text_content = f"""
Welcome to {settings.APP_NAME}, {username}!

Thank you for creating an account with us.

You can now log in to your account at:
{settings.FRONTEND_URL}/login

If you have any questions or need assistance, please don't hesitate to \
contact us.

Best regards,
{settings.APP_NAME} Team
        """.strip()

        return await self.send_email(
            to_email=to_email,
            subject=f"Welcome to {settings.APP_NAME}!",
            html_content=html_content,
            text_content=text_content,
        )

    async def send_email_verification(
        self,
        to_email: str,
        username: str,
        verification_token: str,
    ) -> bool:
        """Send email verification email.

        Args:
            to_email: Recipient email address
            username: User's username
            verification_token: Email verification token

        Returns:
            bool: True if email was sent successfully
        """
        verification_url = (
            f"{settings.FRONTEND_URL}/verify-email?token={verification_token}"
        )

        # Render email template
        template = self.template_env.get_template("email_verification.html")
        html_content = template.render(
            username=username,
            verification_url=verification_url,
            app_name=settings.APP_NAME,
        )

        # Plain text version
        text_content = f"""
Hello {username},

Please verify your email address to complete your registration with \
{settings.APP_NAME}.

Click the link below to verify your email:
{verification_url}

This link will expire in 24 hours.

If you did not create an account, please ignore this email.

Best regards,
{settings.APP_NAME} Team
        """.strip()

        return await self.send_email(
            to_email=to_email,
            subject=f"Verify your email - {settings.APP_NAME}",
            html_content=html_content,
            text_content=text_content,
        )


# Global email service instance
email_service = EmailService()
