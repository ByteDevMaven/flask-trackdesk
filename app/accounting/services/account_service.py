"""Account CRUD and chart of accounts generation."""
from datetime import UTC, datetime

from app.models import db, Account, LedgerEntry, Transaction
from app.models.enums import AccountType

from ._balance import _active_ledger_conditions


class AccountService:

    @staticmethod
    def create_account(company_id: int, data) -> Account:
        name = data.get('name', '').strip()
        account_type = data.get('type', '').strip()
        description = data.get('description', '').strip()
        code = data.get('code', '').strip() or None

        if not name or not account_type:
            raise ValueError('El nombre y el tipo de cuenta son requeridos.')
        try:
            act_type_enum = AccountType(account_type)
        except ValueError:
            raise ValueError('Tipo de cuenta inválido.')

        account = Account(
            company_id=company_id,
            code=code,
            name=name,
            type=act_type_enum,
            description=description,
        )
        db.session.add(account)
        db.session.commit()
        return account

    @staticmethod
    def update_account(company_id: int, account_id: int, data) -> Account:
        account = Account.query.filter_by(id=account_id, company_id=company_id).first_or_404()
        name = data.get('name', '').strip()
        account_type = data.get('type', '').strip()
        if not name or not account_type:
            raise ValueError('Nombre y tipo son requeridos.')
        try:
            account.type = AccountType(account_type)
        except ValueError:
            raise ValueError('Tipo de cuenta inválido.')
        account.name = name
        account.code = data.get('code', '').strip() or account.code
        account.description = data.get('description', '').strip()
        account.is_active = data.get('is_active', 'true').lower() == 'true'
        db.session.commit()
        return account

    @staticmethod
    def delete_account_safe(company_id: int, account_id: int) -> None:
        """
        Soft-delete an account.
        Raises ValueError if the account has any non-voided ledger entries.
        """
        account = Account.query.filter_by(id=account_id, company_id=company_id).first_or_404()
        entry_count = (
            LedgerEntry.query
            .outerjoin(Transaction, LedgerEntry.transaction_id == Transaction.id)
            .filter(
                LedgerEntry.account_id == account_id,
                LedgerEntry.company_id == company_id,
                _active_ledger_conditions(),
            )
            .count()
        )
        if entry_count > 0:
            raise ValueError(
                f'Esta cuenta tiene {entry_count} movimiento(s) contables y no puede eliminarse. '
                'Puede desactivarla en su lugar.'
            )
        account.is_active = False
        account.is_deleted = True
        account.deleted_at = datetime.now(UTC)
        db.session.commit()

    @staticmethod
    def generate_default_accounts(company_id: int) -> int:
        default_accounts = [
            {'code': '1100', 'name': 'Caja y Bancos',          'type': AccountType.asset,     'description': 'Efectivo y saldos bancarios.'},
            {'code': '1200', 'name': 'Cuentas por Cobrar',     'type': AccountType.asset,     'description': 'Derechos de cobro a clientes.'},
            {'code': '1300', 'name': 'Inventario',             'type': AccountType.asset,     'description': 'Mercancías para la venta.'},
            {'code': '1400', 'name': 'Activos Fijos',          'type': AccountType.asset,     'description': 'Maquinaria, equipos y mobiliario.'},
            {'code': '2100', 'name': 'Cuentas por Pagar',      'type': AccountType.liability, 'description': 'Obligaciones con proveedores.'},
            {'code': '2200', 'name': 'Obligaciones Fiscales',  'type': AccountType.liability, 'description': 'Impuestos pendientes.'},
            {'code': '2300', 'name': 'Préstamos por Pagar',    'type': AccountType.liability, 'description': 'Deudas bancarias a corto y largo plazo.'},
            {'code': '3100', 'name': 'Capital Social',         'type': AccountType.equity,    'description': 'Aportaciones de socios.'},
            {'code': '3200', 'name': 'Resultados Acumulados',  'type': AccountType.equity,    'description': 'Utilidades/pérdidas de ejercicios anteriores.'},
            {'code': '4100', 'name': 'Ventas de Servicios',    'type': AccountType.revenue,   'description': 'Ingresos por servicios.'},
            {'code': '4200', 'name': 'Ventas de Productos',    'type': AccountType.revenue,   'description': 'Ingresos por ventas de bienes.'},
            {'code': '5100', 'name': 'Costo de Ventas',        'type': AccountType.expense,   'description': 'Costo directo de bienes vendidos.'},
            {'code': '5200', 'name': 'Nóminas y Salarios',     'type': AccountType.expense,   'description': 'Remuneraciones al personal.'},
            {'code': '5300', 'name': 'Gastos de Alquiler',     'type': AccountType.expense,   'description': 'Arrendamiento de locales.'},
            {'code': '5400', 'name': 'Servicios Públicos',     'type': AccountType.expense,   'description': 'Electricidad, agua, internet.'},
            {'code': '5500', 'name': 'Gastos de Marketing',    'type': AccountType.expense,   'description': 'Publicidad y promoción.'},
            {'code': '5600', 'name': 'Gastos Financieros',     'type': AccountType.expense,   'description': 'Intereses y comisiones bancarias.'},
            {'code': '5900', 'name': 'Otros Gastos',           'type': AccountType.expense,   'description': 'Gastos diversos no clasificados.'},
        ]

        created_count = 0
        for def_acc in default_accounts:
            exists = Account.query.filter_by(
                company_id=company_id, name=def_acc['name'], type=def_acc['type']
            ).first()
            if not exists:
                db.session.add(Account(
                    company_id=company_id,
                    code=def_acc['code'],
                    name=def_acc['name'],
                    type=def_acc['type'],
                    description=def_acc['description'],
                    is_default=True,
                    is_active=True,
                ))
                created_count += 1

        if created_count > 0:
            db.session.commit()
        return created_count
