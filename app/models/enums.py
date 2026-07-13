import enum

class AccountType(enum.Enum):
    asset = 'asset'
    liability = 'liability'
    equity = 'equity'
    revenue = 'revenue'
    expense = 'expense'

    @property
    def label_es(self):
        return {
            'asset': 'Activo',
            'liability': 'Pasivo',
            'equity': 'Patrimonio',
            'revenue': 'Ingreso',
            'expense': 'Gasto'
        }.get(self.value, self.value.title())

class DocumentType(enum.Enum):
    quote = 'quote'
    invoice = 'invoice'

    @property
    def label_es(self):
        return {
            'quote': 'Cotización',
            'invoice': 'Factura'
        }.get(self.value, self.value.title())

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

    @property
    def label_es(self):
        return {
            'draft': 'Borrador',
            'sent': 'Enviado',
            'issued': 'Emitido',
            'partial': 'Parcial',
            'paid': 'Pagado',
            'overdue': 'Vencido',
            'pending': 'Pendiente',
            'credit_note': 'Nota de Crédito',
            'exchange': 'Intercambio',
            'cancelled': 'Cancelado'
        }.get(self.value, self.value.title())

# Legacy alias for backward compatibility
InvoiceType = DocumentStatus

class StockMovementType(enum.Enum):
    incoming = 'incoming'
    outgoing = 'outgoing'
    adjustment = 'adjustment'

    @property
    def label_es(self):
        return {
            'incoming': 'Entrada',
            'outgoing': 'Salida',
            'adjustment': 'Ajuste'
        }.get(self.value, self.value.title())

class PaymentMethod(enum.Enum):
    cash = 'cash'
    bank_transfer = 'bank_transfer'
    credit_card = 'credit_card'
    cheque = 'cheque'
    other = 'other'

    @property
    def label_es(self):
        return {
            'cash': 'Efectivo',
            'bank_transfer': 'Transferencia',
            'credit_card': 'Tarjeta',
            'cheque': 'Cheque',
            'other': 'Otro'
        }.get(self.value, self.value.title())

class ContactType(enum.Enum):
    customer = 'customer'
    supplier = 'supplier'
    customer_supplier = "customer_supplier"
    lead = "lead"
    other = "other"

    @property
    def label_es(self):
        return {
            'customer': 'Cliente',
            'supplier': 'Proveedor',
            'customer_supplier': 'Cliente/Proveedor',
            'lead': 'Lead',
            'other': 'Otro'
        }.get(self.value, self.value.title())

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
    pending = 'pending'
    approved = 'approved'
    paid = 'paid'

    @property
    def label_es(self):
        return {
            'draft': 'Borrador',
            'pending': 'Pendiente',
            'approved': 'Aprobado',
            'paid': 'Pagado'
        }.get(self.value, self.value.title())

class TransactionType(enum.Enum):
    journal = 'journal'
    expense = 'expense'
    income = 'income'
    payment = 'payment'
    transfer = 'transfer'

    @property
    def label_es(self):
        return {
            'journal': 'Diario',
            'expense': 'Gasto',
            'income': 'Ingreso',
            'payment': 'Pago',
            'transfer': 'Transferencia'
        }.get(self.value, self.value.title())
