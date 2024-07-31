# ========================================
# Account Bank Statement ES CSB43 Scenario
# ========================================

# Imports
from trytond.modules.account.tests.tools import create_fiscalyear, create_chart, get_accounts
from trytond.modules.company.tests.tools import create_company, get_company
from trytond.tests.tools import activate_modules
from proteus import Model, Wizard
import os
import datetime
import unittest
from trytond.tests.test_tryton import drop_db
from trytond.modules.account_bank_statement_es_csb43.tests.tools import read_file

class Test(unittest.TestCase):
    def setUp(self):
        drop_db()
        super().setUp()

    def tearDown(self):
        drop_db()
        super().tearDown()

    def test(self):

        today = datetime.date.today()
        now = datetime.datetime.now()

        # Activate account_bank_statement_es_csb43 module
        config = activate_modules('account_bank_statement_es_csb43')

        # Create company
        _ = create_company()
        company = get_company()

        # Create fiscal year
        fiscalyear = create_fiscalyear(company)
        fiscalyear.click('create_period')

        # Create chart of accounts
        _ = create_chart(company)
        accounts = get_accounts(company)
        receivable = accounts['receivable']
        revenue = accounts['revenue']
        expense = accounts['expense']
        payable = accounts['payable']
        cash = accounts['cash']
        cash.bank_reconcile = True
        cash.save()

        # Create party
        Party = Model.get('party.party')
        party = Party(name='Party')
        party.save()

        # Create Journal
        Sequence = Model.get('ir.sequence')
        SequenceType = Model.get('ir.sequence.type')
        sequence_type, = SequenceType.find([('name', '=', 'Account Journal')])
        sequence = Sequence(name='Bank', sequence_type=sequence_type,
            company=company)
        sequence.save()
        AccountJournal = Model.get('account.journal')
        account_journal = AccountJournal(name='Statement',
            type='cash',
            sequence=sequence)
        account_journal.save()

        # Create Statement Journal
        StatementJournal = Model.get('account.bank.statement.journal')
        statement_journal = StatementJournal(name='Test',
            journal=account_journal, currency=company.currency, account=cash)
        statement_journal.save()

        # Create Bank Statement
        BankStatement = Model.get('account.bank.statement')
        StatementLine = Model.get('account.bank.statement.line')
        statement = BankStatement(journal=statement_journal, date=now)
        statement.save()
        statement.reload()

        # Import CSB43 file
        csb43file = os.path.join(os.path.dirname(__file__), 'c43.txt')
        wizard = Wizard('account.bank.statement.import', [statement])
        wizard.form.import_file = read_file(csb43file)
        wizard.form.type = 'csb43'
        wizard.form.confirm = True
        wizard.execute('import_file')
        statement.reload()
        self.assertEqual(len(statement.lines)
        , 22
        )