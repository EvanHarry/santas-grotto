import csv
from datetime import datetime
import os
import shutil
import sqlite3
import time

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

    from grotto.auth import generate_password
    print('Creating default user...')
    username = input('Name: ')
    pwd = generate_password()

    db.execute(
        'INSERT INTO user (username, password, admin) VALUES (?, ?, ?)',
        (username, generate_password_hash(pwd), True)
    )
    db.commit()

    print('\nGenerated default account, {0}.'.format(username))
    print('Password {0}.\n'.format(pwd))


@click.command('init-db')
@with_appcontext
def init_db_command():
    '''Clear the existing data and create new tables.'''
    init_db()
    click.echo('Initialised the database.')


def seed_db(wipe=False):
    count = 0
    errors = []
    db = get_db()

    now = datetime.now().strftime("%d-%m-%Y")
    user = 'Admin'

    last_modified = '{0} - {1}'.format(now, user)

    print('Seeding the database...')

    if wipe:
        print('Wiping stock table.')
        db.execute(
            'DELETE FROM stock'
        )

    if os.path.isfile('data.csv') is False:
        print('\nSeed file does not exist.\n')
        return

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
            elif row['Quantities'] in('BOX', 'EMPTY', 'Assorted', 'N/A'):
                errors.append(row)
                continue
            else:
                quantity = int(row['Quantities'])

            try:
                db.execute(
                    'INSERT INTO stock (supplier_code, tidings_code, supplier, location, quantity, last_modified) VALUES (?, ?, ?, ?, ?, ?)',
                    (row['Suplier Code'], row['Our Code'], row['Supplier'], row['Location'], quantity, last_modified)
                )
                count += 1
            except db.Error:
                errors.append(row)

    db.commit()

    with open('errors.csv', 'w', newline='') as csvfile:
        fieldnames = ['Suplier Code', 'Our Code', 'Supplier', 'Location', 'Quantities', 'Date Modified', 'Amazon']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for row in errors:
            writer.writerow(row)

    print('\n{0} entries added to the database.'.format(count))
    print('{0} entries with errors.\n'.format(len(errors)))


@click.command('seed-db')
@click.option('--wipe', type=click.Choice(['yes', 'no']))
@with_appcontext
def seed_db_command(wipe):
    '''Seed database from .csv file.'''
    if wipe == 'yes':
        seed_db(True)
    else:
        seed_db()
    click.echo('Database seeded.')


def reset_user():
    username = input('Username: ')

    db = get_db()

    cursor = db.execute(
        'SELECT * FROM user WHERE username = ?', (username,)
    ).fetchone()

    if cursor is None:
        print('\nUser not found.\n')
        return

    from grotto.auth import generate_password
    pwd = generate_password()

    try:
        db.execute(
            'UPDATE user SET password = ? WHERE username = ?',
            (generate_password_hash(pwd), username)
        )
        db.commit()
    except db.Error:
        print('\nError updating user.\n')
        return

    print('\nNew password: {0}.\n'.format(pwd))


@click.command('reset-user')
@with_appcontext
def reset_user_command():
    '''Resets user password.'''
    reset_user()
    click.echo('User password reset.')


def app_version():
    from grotto import __version__
    print('Grotto version {0}'.format(__version__))


@click.command('app-version')
@with_appcontext
def app_version_command():
    '''Prints app version.'''
    app_version()


def backup_db():
    db = get_db()

    print('Starting database backup...')

    db.execute(
        'BEGIN IMMEDIATE'
    )

    if not os.path.exists('backups'):
        os.makedirs('backups')

    original_file = os.path.join(current_app.instance_path, 'grotto.sqlite')
    backup_file = os.path.join('backups', 'grotto' + time.strftime("_%d-%m-%Y.sqlite"))

    shutil.copyfile(original_file, backup_file)

    db.rollback()

    print('\nDatabase backup stored in {0}.'.format(backup_file))


@click.command('backup-db')
@with_appcontext
def backup_db_command():
    '''Make a local backup of the database.'''
    backup_db()


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)
    app.cli.add_command(seed_db_command)
    app.cli.add_command(reset_user_command)
    app.cli.add_command(app_version_command)
    app.cli.add_command(backup_db_command)
