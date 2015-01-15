#The COPYRIGHT file at the top level of this repository contains the full
#copyright notices and license terms.
from trytond.pool import Pool
from trytond.model import ModelSQL, ModelView, fields
from trytond.transaction import Transaction
from trytond.wizard import Wizard, StateView, StateTransition, Button
from retrofix import c43
import datetime

__all__ = ['ImportCSB43', 'ImportCSB43Start']


class ImportCSB43Start(ModelView):
    'Import CSB43 start'
    __name__ = 'account.bank.statement.import_csb43.start'
    import_file = fields.Binary('Import File', required=True)


class ImportCSB43(Wizard):
    'Import CSB43 file'
    __name__ = 'account.bank.statement.import_csb43'
    start = StateView('account.bank.statement.import_csb43.start',
        'account_bank_statement_es_csb43.import_csb43_start_view_form', [
            Button('Cancel', 'end', 'tryton-cancel'),
            Button('Import File', 'import_file', 'tryton-ok', default=True),
            ])
    import_file = StateTransition()

    @classmethod
    def __setup__(cls):
        super(ImportCSB43, cls).__setup__()
        cls._error_messages.update({
                'statement_already_has_lines':
                    'You cannot import a CSB43 bank statement file in a bank '
                        'statement with lines.',
                })

    def transition_import_file(self):
        BankStatement = Pool().get('account.bank.statement')
        BankStatementLine = Pool().get('account.bank.statement.line')
        Attachment = Pool().get('ir.attachment')

        statement = BankStatement(Transaction().context['active_id'])
        if statement.lines:
            self.raise_user_error('statement_already_has_lines')
        data = unicode(str(self.start.import_file), 'latin1')
        records = c43.read(data)
        description = []
        lines = []
        line = {}

        BankStatement.write([statement], {
            'start_date': records[0].start_date,
            'end_date': records[0].end_date,
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
                line = {
                    'statement': statement.id,
                    'date': record.value_date,
                    'amount': record.amount,
                    }
                description = [record.reference_1]
                description.append(record.reference_2)

        if line:
            description = [x.strip() for x in description if x != '']
            line['description'] = " ".join(description)
            lines.append(line.copy())
        BankStatementLine.create(lines)
        BankStatement.confirm([statement])
        attach = Attachment(
            name=datetime.datetime.now().strftime("%y/%m/%d %H:%M:%S"),
            type='data',
            data=self.start.import_file,
            resource=str(statement))
        attach.save()
        statement.search_reconcile()
        return 'end'
