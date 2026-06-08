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
    customer_supplier = "customer_supplier"
    lead = "lead"
    other = "other"

class EmployeeClass(enum.Enum):
    full_time = 'full_time'
    part_time = 'part_time'
    per_project = 'per_project'
    seasonal_full_time = 'seasonal_full_time'
    seasonal_part_time = 'seasonal_part_time'

    @property
    def label_es(self):
        return {
            'full_time': 'Tiempo Completo',
            'part_time': 'Medio Tiempo',
            'per_project': 'Por Proyecto',
            'seasonal_full_time': 'Estacional (Tiempo Completo)',
            'seasonal_part_time': 'Estacional (Medio Tiempo)'
        }.get(self.value, self.value)

class PayPeriod(enum.Enum):
    hour = 'hour'
    day = 'day'
    month = 'month'

    @property
    def label_es(self):
        return {
            'hour': 'Hora',
            'day': 'Día',
            'month': 'Mes'
        }.get(self.value, self.value)

class LeaveType(enum.Enum):
    pto = 'pto'
    sick = 'sick'
    maternity = 'maternity'

    @property
    def label_es(self):
        return {
            'pto': 'PTO / Vacaciones',
            'sick': 'Enfermedad',
            'maternity': 'Maternidad/Paternidad'
        }.get(self.value, self.value)

class LeaveStatus(enum.Enum):
    pending = 'pending'
    approved = 'approved'
    rejected = 'rejected'

    @property
    def label_es(self):
        return {
            'pending': 'Pendiente',
            'approved': 'Aprobado',
            'rejected': 'Rechazado'
        }.get(self.value, self.value)

class PTOAccrualPeriod(enum.Enum):
    day = 'day'
    month = 'month'
    year = 'year'

    @property
    def label_es(self):
        return {
            'day': 'Día',
            'month': 'Mes',
            'year': 'Año'
        }.get(self.value, self.value)

class UserStatus(enum.Enum):
    active = 'active'
    inactive = 'inactive'
    suspended = 'suspended'

    @property
    def label_es(self):
        return {
            'active': 'Activo',
            'inactive': 'Inactivo',
            'suspended': 'Suspendido'
        }.get(self.value, self.value)

class ExpenseStatus(enum.Enum):
    draft = 'draft'
    approved = 'approved'
    paid = 'paid'

class TransactionType(enum.Enum):
    journal = 'journal'
    expense = 'expense'
    income = 'income'
    payment = 'payment'
    transfer = 'transfer'
