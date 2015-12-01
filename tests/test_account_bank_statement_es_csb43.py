# This file is part of the account_bank_statement_es_csb43 module for Tryton.
# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
import unittest
import trytond.tests.test_tryton
from trytond.tests.test_tryton import ModuleTestCase


class AccountBankStatementEsCsb43TestCase(ModuleTestCase):
    'Test Account Bank Statement Es Csb43 module'
    module = 'account_bank_statement_es_csb43'


def suite():
    suite = trytond.tests.test_tryton.suite()
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(
        AccountBankStatementEsCsb43TestCase))
    return suite