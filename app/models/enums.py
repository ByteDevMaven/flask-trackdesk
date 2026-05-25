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

class InvoiceType(enum.Enum):
    sent = 'sent'
    draft = 'draft'
    issued = 'issued'
    cancelled = 'cancelled'
    partial = 'partial'
    paid = 'paid'
    overdue = 'overdue'
    pending = 'pending'
    credit = 'credit'
    exchange = 'exchange'

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
