import enum
from flask_babel import _

class DocumentType(enum.Enum):
    quote = 'quote'
    invoice = 'invoice'

class InvoiceType(enum.Enum):
    sent = _('sent')
    draft = _('draft')
    issued = _('issued')
    cancelled = _('cancelled')
    partial = _('partial')
    paid = _('paid')
    overdue = _('overdue')
    pending = _('pending')
    credit = _('credit')
    exchange = _('exchange')

class StockMovementType(enum.Enum):
    incoming = 'incoming'
    outgoing = 'outgoing'
    adjustment = 'adjustment'

class PaymentMethod(enum.Enum):
    cash = _('cash')
    bank_transfer = _('bank transfer')
    credit_card = _('credit card')
    cheque = _('cheque')
    other = _('other')

class ContactType(enum.Enum):
    customer = 'customer'
    supplier = 'supplier'
