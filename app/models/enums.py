import enum

class AccountType(enum.Enum):
    asset = 'asset'
    liability = 'liability'
    equity = 'equity'
    revenue = 'revenue'
    expense = 'expense'

class DocumentType(enum.Enum):
    quote = 'quote'
    invoice = 'invoice'

class DocumentStatus(enum.Enum):
    draft = 'draft'
    sent = 'sent'
    issued = 'issued'
    partial = 'partial'
    paid = 'paid'
    overdue = 'overdue'
    pending = 'pending'
    credit_note = 'credit_note'
    exchange = 'exchange'
    cancelled = 'cancelled'

# Legacy alias for backward compatibility
InvoiceType = DocumentStatus

class StockMovementType(enum.Enum):
    incoming = 'incoming'
    outgoing = 'outgoing'
    adjustment = 'adjustment'

class PaymentMethod(enum.Enum):
    cash = 'cash'
    bank_transfer = 'bank transfer'
    credit_card = 'credit card'
    cheque = 'cheque'
    other = 'other'

class ContactType(enum.Enum):
    customer = 'customer'
    supplier = 'supplier'

class UserStatus(enum.Enum):
    active = 'active'
    inactive = 'inactive'
    suspended = 'suspended'
