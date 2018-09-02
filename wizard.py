from trytond.model import ModelView, fields
from trytond.pool import Pool
from trytond.wizard import Wizard, StateView, StateTransition, Button
from trytond.transaction import Transaction
from trytond.tools import file_open

import csv

__all__ = ['ImportICD10Start', 'ImportICD10Succeed', 'ImportICD10']


class ImportICD10Start(ModelView):
    'Import ICD10 Start'
    __name__ = 'galeno.import.icd10.start'

    language = fields.Many2One('ir.lang', 'Language', required=True)


class ImportICD10Succeed(ModelView):
    'Import ICD10 Succeed'
    __name__ = 'galeno.import.icd10.succeed'


class ImportICD10(Wizard):
    'Import ICD10'
    __name__ = 'galeno.import.icd10'

    start = StateView('galeno.import.icd10.start',
        'galeno_base_data.import_icd10_start_view_form', [
            Button('Cancel', 'end', 'tryton-cancel'),
            Button('OK', 'import_icd10', 'tryton-ok', default=True)
        ])
    import_icd10 = StateTransition()
    succeed = StateView('galeno.import.icd10.succeed',
        'galeno_base_data.import_icd10_succeed_view_form', [
            Button('OK', 'end', 'tryton-ok', default=True),
            ])

    def transition_import_icd10(self):
        pool = Pool()
        Group = pool.get('galeno.disease.group')
        Category = pool.get('galeno.disease.category')
        Disease = pool.get('galeno.disease')
        Procedure = pool.get('galeno.procedure')
        cursor = Transaction().connection.cursor()
        lang = self.start.language.code
        path = 'galeno_base_data/data/diseases/groups_' + lang + '.csv'
        with file_open(path, mode='r', encoding='utf-8') as group_file:
            fieldnames = ['code', 'name', 'description', 'information']
            reader = csv.DictReader(
                group_file, delimiter='|', fieldnames=fieldnames)
            next(reader)  # Skip header
            for row in reader:
                group = Group()
                for field in row:
                    if row[field] == '':
                        value = None
                    else:
                        value = row[field]
                    setattr(group, field, value)
                group.core = True
                group.save()

        path = 'galeno_base_data/data/diseases/categories_' + lang + '.csv'
        with file_open(path, mode='r', encoding='utf-8') as category_file:
            fieldnames = ['code', 'name', 'parent']
            reader = csv.DictReader(
                category_file, delimiter='|', fieldnames=fieldnames)
            next(reader)  # Skip header
            for row in reader:
                if row['parent'] != '':
                    parent, = Category.search([('code', '=', row['parent'])])
                else:
                    parent = None
                category = Category()
                category.code = row['code']
                category.name = row['name']
                category.parent = parent
                category.core = True
                category.save()

        groups = {}
        categories = {}
        for group in Group.search([]):
            groups[group.code] = group
        for category in Category.search([]):
            categories[category.code] = category

        to_save = []
        path = 'galeno_base_data/data/diseases/diseases_' + lang + '.csv'
        with file_open(path, mode='r', encoding='utf-8') as disease_file:
            fieldnames = ['code', 'name', 'category', 'groups', 'chromosome',
                'protein', 'gene', 'information', 'active']
            reader = csv.DictReader(
                disease_file, delimiter='|', fieldnames=fieldnames)
            next(reader)  # Skip header
            for row in reader:
                disease = Disease()
                for field in row:
                    if row[field] == '':
                        value = None
                    else:
                        if field == 'active':
                            value = bool(row[field])
                        elif field == 'category':
                            value = categories[row[field]]
                        elif field == 'groups':
                            value = []
                            for group_code in row[field].split(','):
                                value.append(groups[group_code].id)
                        else:
                            value = row[field]
                    setattr(disease, field, value)
                disease.core = True
                to_save.append(disease)
            Disease.save(to_save)

        table = Procedure.__table__()
        columns = [table.code, table.name, table.core]
        values = []
        path = 'galeno_base_data/data/procedures/procedures_' + lang + '.csv'
        with file_open(path, mode='r', encoding='utf-8') as procedure_file:
            fieldnames = ['code', 'name']
            reader = csv.DictReader(
                procedure_file, delimiter='|', fieldnames=fieldnames)
            next(reader)  # Skip header
            for row in reader:
                record = []
                for field in row:
                    if row[field] == '':
                        value = None
                    else:
                        value = row[field]
                    record.append(value)
                record.append(True)
                values.append(record)

            cursor.execute(*table.insert(columns, values))
            Procedure.save(to_save)

        return 'succeed'
