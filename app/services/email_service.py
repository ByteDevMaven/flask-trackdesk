import traceback
from threading import Thread
from flask import current_app, render_template
from flask_mail import Message
from app.extensions import mail

class EmailService:
    @staticmethod
    def send_async_email(app, msg):
        with app.app_context():
            try:
                mail.send(msg)
            except Exception as e:
                app.logger.error(f"Error sending email: {e}")

    @staticmethod
    def send_email(subject, sender, recipients, text_body, html_body=None):
        msg = Message(subject, sender=sender, recipients=recipients)
        msg.body = text_body
        if html_body:
            msg.html = html_body
        
        # Run asynchronously to avoid blocking the request
        Thread(
            target=EmailService.send_async_email,
            args=(current_app._get_current_object(), msg)
        ).start()

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
            text_body = f"Dear {user.name},\n\nPlease click the following link to reset your password:\n{reset_url}\n\nIf you did not request this, please ignore this email."
            html_body = f"<p>Dear {user.name},</p><p>Please click the link below to reset your password:</p><p><a href='{reset_url}'>{reset_url}</a></p><p>If you did not request this, please ignore this email.</p>"

        EmailService.send_email(
            subject=subject,
            sender=sender,
            recipients=[user.email],
            text_body=text_body,
            html_body=html_body
        )
