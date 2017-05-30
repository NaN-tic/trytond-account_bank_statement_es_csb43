#The COPYRIGHT file at the top level of this repository contains the full
#copyright notices and license terms.
from trytond.pool import Pool
from . import statement


def register():
    Pool.register(
        statement.Configuration,
        statement.Statement,
        statement.ImportCSB43Start,
        module='account_bank_statement_es_csb43', type_='model')
    Pool.register(
        statement.ImportCSB43,
        module='account_bank_statement_es_csb43', type_='wizard')
