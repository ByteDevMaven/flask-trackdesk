import smtplib
import socket
from threading import Thread
from flask import current_app, render_template
from flask_mail import Message
from app.extensions import mail

class EmailService:
    @staticmethod
    def _safe_mail_context(app, msg):
        recipients = list(msg.recipients or [])
        return {
            'mail_server': app.config.get('MAIL_SERVER'),
            'mail_port': app.config.get('MAIL_PORT'),
            'mail_use_tls': app.config.get('MAIL_USE_TLS'),
            'mail_use_ssl': app.config.get('MAIL_USE_SSL'),
            'mail_username_set': bool(app.config.get('MAIL_USERNAME')),
            'mail_password_set': bool(app.config.get('MAIL_PASSWORD')),
            'sender': msg.sender,
            'recipient_count': len(recipients),
            'recipients': recipients,
            'subject': msg.subject,
        }

    @staticmethod
    def send_async_email(app, msg):
        with app.app_context():
            try:
                app.logger.info(
                    "Sending email subject=%r recipients=%s server=%s:%s tls=%s ssl=%s username_set=%s",
                    msg.subject,
                    msg.recipients,
                    app.config.get('MAIL_SERVER'),
                    app.config.get('MAIL_PORT'),
                    app.config.get('MAIL_USE_TLS'),
                    app.config.get('MAIL_USE_SSL'),
                    bool(app.config.get('MAIL_USERNAME')),
                )
                mail.send(msg)
                app.logger.info("Email sent successfully subject=%r recipients=%s", msg.subject, msg.recipients)
            except smtplib.SMTPAuthenticationError as e:
                app.logger.exception(
                    "SMTP authentication failed while sending email. context=%s smtp_code=%s smtp_error=%r",
                    EmailService._safe_mail_context(app, msg),
                    getattr(e, 'smtp_code', None),
                    getattr(e, 'smtp_error', None),
                )
            except smtplib.SMTPRecipientsRefused as e:
                app.logger.exception(
                    "SMTP rejected all recipients while sending email. context=%s recipients=%r",
                    EmailService._safe_mail_context(app, msg),
                    getattr(e, 'recipients', None),
                )
            except smtplib.SMTPSenderRefused as e:
                app.logger.exception(
                    "SMTP rejected sender while sending email. context=%s smtp_code=%s sender=%r smtp_error=%r",
                    EmailService._safe_mail_context(app, msg),
                    getattr(e, 'smtp_code', None),
                    getattr(e, 'sender', None),
                    getattr(e, 'smtp_error', None),
                )
            except (smtplib.SMTPConnectError, smtplib.SMTPServerDisconnected, socket.timeout, OSError) as e:
                app.logger.exception(
                    "SMTP connection error while sending email. context=%s error_type=%s error=%r",
                    EmailService._safe_mail_context(app, msg),
                    type(e).__name__,
                    e,
                )
            except Exception as e:
                app.logger.exception(
                    "Unexpected error sending email. context=%s error_type=%s error=%r",
                    EmailService._safe_mail_context(app, msg),
                    type(e).__name__,
                    e,
                )

    @staticmethod
    def send_email(subject, sender, recipients, text_body, html_body=None):
        if not recipients:
            current_app.logger.warning("Skipping email with no recipients. subject=%r sender=%r", subject, sender)
            return None

        msg = Message(subject, sender=sender, recipients=recipients)
        msg.body = text_body
        if html_body:
            msg.html = html_body
        
        # Run asynchronously to avoid blocking the request
        thread = Thread(
            target=EmailService.send_async_email,
            args=(current_app._get_current_object(), msg),
            daemon=True,
        )
        thread.start()
        return thread

    @staticmethod
    def notify_error(error, stack_trace=None):
        """Sends an error notification to the configured admin email."""
        admin_email = current_app.config.get('TRACKDESK_ADMIN')
        if not admin_email:
            current_app.logger.warning("No TRACKDESK_ADMIN email configured. Skipping error notification.")
            return

        subject = f"{current_app.config.get('TRACKDESK_MAIL_SUBJECT_PREFIX', '[TrackDesk]')} Server Error: {error}"
        sender = current_app.config.get('TRACKDESK_MAIL_SENDER', 'error@trackdesk.local')
        
        text_body = f"An error occurred in TrackDesk.\n\nError: {error}\n\n"
        if stack_trace:
            text_body += f"Stack Trace:\n{stack_trace}"
        
        EmailService.send_email(
            subject=subject,
            sender=sender,
            recipients=[admin_email],
            text_body=text_body
        )

    @staticmethod
    def send_password_reset(user, reset_url):
        """Sends a password reset email."""
        if not user.email:
            return
            
        subject = f"{current_app.config.get('TRACKDESK_MAIL_SUBJECT_PREFIX', '[TrackDesk]')} Reset Your Password"
        sender = current_app.config.get('TRACKDESK_MAIL_SENDER', 'noreply@trackdesk.local')
        
        try:
            text_body = render_template('emails/reset_password.txt', user=user, reset_url=reset_url)
            html_body = render_template('emails/reset_password.html', user=user, reset_url=reset_url)
        except Exception:
            # Fallback if templates are not created yet
            current_app.logger.exception("Error rendering password reset email templates for user_id=%s", user.id)
            text_body = f"Dear {user.name},\n\nPlease click the following link to reset your password:\n{reset_url}\n\nIf you did not request this, please ignore this email."
            html_body = f"<p>Dear {user.name},</p><p>Please click the link below to reset your password:</p><p><a href='{reset_url}'>{reset_url}</a></p><p>If you did not request this, please ignore this email.</p>"

        EmailService.send_email(
            subject=subject,
            sender=sender,
            recipients=[user.email],
            text_body=text_body,
            html_body=html_body
        )
