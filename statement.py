#The COPYRIGHT file at the top level of this repository contains the full
#copyright notices and license terms.
from trytond.pool import Pool
from trytond.model import ModelSQL, ModelView, fields
from trytond.transaction import Transaction
from trytond.wizard import Wizard, StateView, StateTransition, Button
from retrofix import c43
import datetime

__all__ = ['Statement', 'ImportCSB43', 'ImportCSB43Start']


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

    def transition_import_file(self):
        BankStatement = Pool().get('account.bank.statement')
        BankStatementLine = Pool().get('account.bank.statement.line')
        Attachment = Pool().get('ir.attachment')

        statement = BankStatement(Transaction().context['active_id'])
        data = unicode(str(self.start.import_file), 'latin1')
        records = c43.read(data)
        description = []
        lines = []
        line = {}
        for record in records[1:-1]:
            if record.get('record_code') == '23':
                description.append(record.get('concept_1', '').strip())
                description.append(record.get('concept_2', '').strip())
            elif record.get('record_code') == '22':
                if line:
                    description.append(record.get('reference_1','').strip())
                    description.append(record.get('reference_2','').strip())
                    description = [x for x in description if x != '']
                    line['description'] = "/".join(description)
                    description = []
                    lines.append(line.copy())
                    line = {}
                line = {
                    'statement': statement.id,
                    'date': record.get('value_date'),
                    'amount': record.get('amount'),
                    }
                description.append(record.get('concept_1', '').strip())
                description.append(record.get('concept_2', '').strip())
        if line:
            description = [x for x in description if x != '']
            line['description'] = "/".join(description)
            lines.append(line.copy())
        BankStatementLine.create(lines)
        BankStatement.confirm([statement])
        attach = Attachment(
            name=datetime.datetime.now().strftime("%y/%m/%d hh:mm:ss"),
            type='data',
            data=self.start.import_file,
            resource=str(statement))
        attach.save()
        statement.search_reconcile()
        return 'end'


class Statement(ModelSQL, ModelView):
    __name__ = 'account.bank.statement'

    def search_reconcile(self):
        for line in self.lines:
            StatementLine = Pool().get('account.bank.statement.line')
            StatementLine.search_reconcile([line])
