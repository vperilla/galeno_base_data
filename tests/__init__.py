# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.

try:
    from trytond.modules.galeno_base_data.tests.test_galeno_base_data import suite
except ImportError:
    from .test_galeno_base_data import suite

__all__ = ['suite']
