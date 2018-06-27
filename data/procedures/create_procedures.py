from proteus import config, Model
import csv
import pdb
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter


def create_procedures(host, port, database, username, password, filename):
    pdb.set_trace()
    config.set_xmlrpc('http://%s:%s@%s:%s/%s/'
        % (username, password, host, port, database))

    Procedure = Model.get('galeno.procedure')
    to_save = []
    cont = 0

    with open(filename, 'rb') as procedure_file:
        fieldnames = ['code', 'name']
        reader = csv.DictReader(
            procedure_file, delimiter='|', fieldnames=fieldnames)
        next(reader)  # Skip header
        for row in reader:
            cont += 1
            print((cont, row))
            procedure = Procedure()
            for field in row:
                if row[field] == '':
                    value = None
                else:
                    value = row[field]
                setattr(procedure, field, value)
            procedure.core = True
            to_save.append(procedure)
        Procedure.save(to_save)


if __name__ == '__main__':
    parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument('--host', dest='host',
        help='host', default='localhost')
    parser.add_argument('--port', dest='port',
        help='port', default='8000')
    parser.add_argument('--database', dest='database',
        help='database', required=True)
    parser.add_argument('--user', dest='user',
        help='user', required=True)
    parser.add_argument('--password', dest='password',
        help='password', required=True)
    parser.add_argument('--filename', dest='filename',
        help='filename', required=True)
    options = parser.parse_args()
    create_procedures(options.host, options.port, options.database,
        options.user, options.password, options.filename)
