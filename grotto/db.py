import csv
from datetime import datetime
import sqlite3
from urllib import parse

import click
from flask import current_app, g
from flask.cli import with_appcontext
from werkzeug.security import generate_password_hash


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            current_app.config['DATABASE'],
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row

    return g.db


def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()


def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))

    db.execute(
        'INSERT INTO user (username, password, admin) VALUES (?, ?, ?)',
        ('Evan', generate_password_hash('Test1234'), True)
    )
    db.commit()


@click.command('init-db')
@with_appcontext
def init_db_command():
    '''Clear the existing data and create new tables.'''
    init_db()
    click.echo('Initialised the database.')


def seed_db():
    count = 0
    errors = []
    db = get_db()

    now = datetime.now().strftime("%d-%m-%Y")
    user = 'Admin'

    last_modified = '{0} - {1}'.format(now, user)

    with open('data.csv', newline='', errors='ignore') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row['Location'] == '':
                errors.append(row)
                continue
            elif row['Quantities'] == '':
                errors.append(row)
                continue
            elif row['Supplier'] == '':
                errors.append(row)
                continue
            elif row['Quantities'] in('BOX', 'EMPTY', 'Assorted', 'N/A', '0'):
                errors.append(row)
                continue
            else:
                quantity = int(row['Quantities'])
                supplier = ''.join(c for c in row['Supplier'] if c not in '?:!/;')

            try:
                db.execute(
                    'INSERT INTO stock (supplier_code, tidings_code, supplier, location, quantity, last_modified) VALUES (?, ?, ?, ?, ?, ?)',
                    (row['Suplier Code'], row['Our Code'], supplier, row['Location'], quantity, last_modified)
                )
                db.commit()
                count += 1
            except db.Error:
                errors.append(row)

    with open('errors.csv', 'w', newline='') as csvfile:
        fieldnames = ['Suplier Code', 'Our Code', 'Supplier', 'Location', 'Quantities', 'Date Modified', 'Amazon']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for row in errors:
            writer.writerow(row)

    print('{0} entries added to the database.'.format(count))
    print('{0} entries with errors.'.format(len(errors)))


@click.command('seed-db')
@with_appcontext
def seed_db_command():
    '''Seed database from .csv file.'''
    seed_db()
    click.echo('Database seeded.')


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
    app.cli.add_command(seed_db_command)
