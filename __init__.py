# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.

from trytond.pool import Pool
from . import wizard


__all__ = ['register']


def register():
    Pool.register(
        wizard.ImportICD10Start,
        wizard.ImportICD10Succeed,
        module='galeno_base_data', type_='model')
    Pool.register(
        wizard.ImportICD10,
        module='galeno_base_data', type_='wizard')
    Pool.register(
        module='galeno_base_data', type_='report')
