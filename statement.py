# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from datetime import datetime
from retrofix import c43
from retrofix.exception import RetrofixException
from trytond.pool import Pool, PoolMeta
from trytond.model import fields
from trytond.i18n import gettext
from trytond.exceptions import UserError


__all__ = ['Configuration', 'ConfigurationDefaultAccount', 'Import',
    'ImportStart']

csb43_date = fields.Selection([
    ('operation_date', 'Operation Date'),
    ('value_date', 'Value Date'),
    ], 'CSB43 Date',
    help='Set date line from CSB43 file')


class Configuration(metaclass=PoolMeta):
    __name__ = 'account.configuration'
    csb43_date = fields.MultiValue(csb43_date)

    @classmethod
    def multivalue_model(cls, field):
        pool = Pool()
        if field == 'csb43_date':
            return pool.get('account.configuration.default_account')
        return super(Configuration, cls).multivalue_model(field)

    @classmethod
    def default_csb43_date(cls, **pattern):
        return cls.multivalue_model('csb43_date').default_csb43_date()


class ConfigurationDefaultAccount(metaclass=PoolMeta):
    __name__ = 'account.configuration.default_account'
    csb43_date = csb43_date

    @classmethod
    def default_csb43_date(cls):
        return 'operation_date'


class ImportStart(metaclass=PoolMeta):
    __name__ = 'account.bank.statement.import.start'

    @classmethod
    def __setup__(cls):
        super(ImportStart, cls).__setup__()
        cls.type.selection += [('csb43', 'CSB 43')]


class Import(metaclass=PoolMeta):
    __name__ = 'account.bank.statement.import'

    def process(self, statement):
        super(Import, self).process(statement)
        if self.start.type != 'csb43':
            return

        pool = Pool()
        BankStatement = pool.get('account.bank.statement')
        BankStatementLine = pool.get('account.bank.statement.line')

        data = self.start.import_file.decode('latin1').replace('\r', '')
        try:
            records = c43.read(data)
        except RetrofixException as e:
            raise UserError(gettext('account_bank_statement.format_error',
                error=str(e)))

        description = []
        lines = []
        line = {}
        start_date = records[0].start_date
        if isinstance(start_date, datetime):
            start_date = start_date.date()
        end_date = records[0].end_date
        if isinstance(end_date, datetime):
            end_date = end_date.date()

        BankStatement.write([statement], {
            'start_date': start_date,
            'end_date': end_date,
            'start_balance': records[0].initial_balance,
            'end_balance': records[-1].final_balance,
            })

        for record in records[1:-1]:
            if record.record_code == '23':
                description.append(record.concept_1)
                description.append(record.concept_2)
            elif record.record_code == '22':
                if line:
                    description = [x.strip() for x in description if x != '']
                    line['description'] = " ".join(description)
                    lines.append(line.copy())
                line = self.get_line_vals_from_record(record, statement)
                description = [record.reference_1]
                description.append(record.reference_2)

        if line:
            description = [x.strip() for x in description if x != '']
            line['description'] = " ".join(description)
            lines.append(line.copy())
        BankStatementLine.create(lines)
        return 'end'

    def get_line_vals_from_record(self, record, statement):
        Config = Pool().get('account.configuration')
        config = Config(1)

        return {
            'statement': statement.id,
            'date': getattr(record, config.csb43_date or 'value_date'),
            'amount': record.amount,
            }
