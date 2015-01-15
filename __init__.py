#The COPYRIGHT file at the top level of this repository contains the full
#copyright notices and license terms.
from trytond.pool import Pool
from .statement import *

def register():
    Pool.register(
        ImportCSB43Start,
        module='account_bank_statement_es_csb43', type_='model')
    Pool.register(
        ImportCSB43,
        module='account_bank_statement_es_csb43', type_='wizard')
