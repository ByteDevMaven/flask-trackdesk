# Implementation Plan: Shared Company Email Threading

The goal is to allow users within the same company to contact clients and suppliers from a single company-based email address (e.g., `support@company.com`) and track the entire conversation (threads) within the platform, regardless of which user sent the message.

## User Review Required

> [!IMPORTANT]
> **Inbound Email Strategy**: To receive replies from clients/suppliers back into the platform, we need a way to process inbound emails. The industry standard for web applications is using a webhook from an email provider (like SendGrid Inbound Parse, Mailgun, or Postmark) rather than polling an IMAP server manually. 
> 
> *The current plan assumes we will build a webhook endpoint to receive incoming emails.* Please confirm if you have a specific email provider in mind, or if you prefer a different method (like IMAP polling).

> [!WARNING]
> **Email Provider Configuration**: This feature requires the application to set custom headers (`Message-ID`, `In-Reply-To`, `References`) to keep track of threads. Your SMTP provider must allow setting these headers.

## Open Questions

1. **Email Provider Setup**: Are you using SendGrid, Mailgun, AWS SES, or standard SMTP for sending? For receiving, which provider's webhook format should we target? (e.g., SendGrid Inbound Parse).
2. **Company Email Address**: Should the system use the existing `email` field on the `Company` model as the generic "From" address, or should we add a specific `support_email` field to `Company`?
3. **Location in UI**: Where should this "Inbox" or "Threads" view live in the navigation? Should it be a standalone "Messages" section, or integrated into the CRM/Contacts pages?

## Proposed Changes

### Database Models

#### [NEW] `app/models/communication.py`
We will create new models to store threads and messages.
- `EmailThread`: 
  - `id`
  - `company_id` (ForeignKey to `companies`)
  - `contact_id` (ForeignKey to `contacts`, optional, represents the client/supplier)
  - `subject`
  - `status` (Enum: open, resolved, closed)
  - `created_at`, `updated_at`
- `EmailMessage`:
  - `id`
  - `thread_id` (ForeignKey to `EmailThread`)
  - `user_id` (ForeignKey to `users`, if sent by an internal user)
  - `sender_email` (For incoming emails)
  - `recipient_email`
  - `body_text`, `body_html`
  - `message_id` (The unique SMTP Message-ID, used for threading)
  - `is_incoming` (Boolean)
  - `created_at`

#### [MODIFY] `app/models/enums.py`
Add a `ThreadStatus` enum.

#### [MODIFY] `app/models/__init__.py`
Import the new `communication` models to ensure they are registered with SQLAlchemy.

---

### Email Service Updates

#### [MODIFY] `app/services/email_service.py`
- Modify `send_email` or add a new `send_thread_email` method that allows overriding the `From` address (to use the company's email) and injects custom SMTP headers (`Message-ID`, `In-Reply-To`, `References`).
- Ensure the outgoing `flask_mail.Message` includes these headers so the client's email client knows it's a thread, and when they reply, their client includes our `Message-ID`.

---

### Webhook & Routes

#### [NEW] `app/communications/routes.py` (New Blueprint)
- Create a new blueprint `app.communications` (or `app.inbox`).
- **GET `/inbox`**: List all active `EmailThread`s for the user's company.
- **GET `/inbox/<thread_id>`**: View all messages in a thread.
- **POST `/inbox/<thread_id>/reply`**: Send a reply to an existing thread.
- **POST `/inbox/new`**: Compose a new email to a `Contact` starting a new thread.

#### [NEW] `app/communications/webhooks.py`
- **POST `/webhooks/incoming-email`**: This endpoint will be called by your email provider when an email is received at the company address.
  - Parse the incoming JSON payload.
  - Extract the `In-Reply-To` header to find the matching `EmailMessage.message_id`.
  - Link the new incoming email to the corresponding `EmailThread`.
  - Save the incoming message to the database as an `EmailMessage`.

---

### User Interface (HTML Templates)

#### [NEW] `app/communications/templates/communications/inbox.html`
List view of threads, sortable by updated_at, showing the contact name, subject, and status.

#### [NEW] `app/communications/templates/communications/thread.html`
A chat-like interface displaying the history of the `EmailMessage` records in chronological order, with a text area at the bottom to send a reply.

#### [NEW] `app/communications/templates/communications/compose.html`
Form to start a new email thread, selecting a `Contact` and entering a subject/body.

#### [MODIFY] `app/templates/base.html` (or sidebar/navigation)
Add a link to the new "Inbox" / "Messages" section.

---

## Verification Plan

### Automated Tests
- No automated tests are currently visible in the structure, but we will test the database relationships and the header generation manually.

### Manual Verification
1. **Database Migration**: Run `flask db migrate` and `flask db upgrade` to create the new tables, verifying they are created successfully.
2. **Send Outbound Email**: From the new UI, select a Contact and send an email. Verify that an `EmailThread` and `EmailMessage` are created in the database, and that the outgoing email has the correct `From` address and `Message-ID`.
3. **Simulate Inbound Email**: Send a POST request to the webhook endpoint simulating a reply from the client. Verify that a new `EmailMessage` is added to the thread and appears in the UI.
4. **Multi-user testing**: Log in as User 1, send an email to a Contact. Log in as User 2 (same company), verify that User 2 can see the thread in the Inbox and can send a reply that correctly threads under the same subject.
