import random
import sqlite3
import string

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

    for i in range(1, 1000):
        supplier_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
        tidings_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
        supplier = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
        location = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
        quantity = int(''.join(random.choices(string.digits, k=2)))

        db.execute(
            'INSERT INTO stock (supplier_code, tidings_code, supplier, location, quantity) VALUES (?, ?, ?, ?, ?)',
            (supplier_code, tidings_code, supplier, location, quantity)
        )
        db.commit()


@click.command('init-db')
@with_appcontext
def init_db_command():
    '''Clear the existing data and create new tables.'''
    init_db()
    click.echo('Initialised the database.')


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
