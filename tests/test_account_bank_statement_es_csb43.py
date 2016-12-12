# This file is part of the account_bank_statement_es_csb43 module for Tryton.
# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
import unittest
import doctest
import trytond.tests.test_tryton
from trytond.tests.test_tryton import ModuleTestCase
from trytond.tests.test_tryton import doctest_teardown, doctest_checker


class AccountBankStatementESCSB43TestCase(ModuleTestCase):
    'Test Account Bank Statement ES CSB43 module'
    module = 'account_bank_statement_es_csb43'


def suite():
    suite = trytond.tests.test_tryton.suite()
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(
        AccountBankStatementESCSB43TestCase))
    suite.addTests(doctest.DocFileSuite('scenario_bank_statement_es_csb43.rst',
            tearDown=doctest_teardown, encoding='utf-8',
            optionflags=doctest.REPORT_ONLY_FIRST_FAILURE,
            checker=doctest_checker))
    return suite
