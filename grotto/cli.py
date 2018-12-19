import csv
import os

import click
from flask.cli import with_appcontext
from sqlalchemy.exc import SQLAlchemyError

from grotto import db
from grotto.models import Stock, User
from grotto.utils import generate_password


def init_db():
    print('Creating default user...\n')
    db.drop_all()
    db.create_all()

    username = input('Name: ')

    user = User.query.filter_by(username=username).first()

    if user is not None:
        print('User already exists.')
        return

    pwd = generate_password()

    u = User(username=username, password=pwd, admin=True)
    db.session.add(u)
    db.session.commit()

    print('\nGenerated default account: {0}, password: {1}.'.format(username, pwd))


@click.command('init-db')
@with_appcontext
def init_db_command():
    '''Clear the existing data and create new tables.'''
    init_db()


def seed_db(wipe=False):
    count = 0
    errors = []

    print('Seeding the database...')

    if wipe:
        print('Wiping stock table.')
        rows_deleted = db.session.query(Stock).delete()
        print('{0} rows deleted.'.format(rows_deleted))

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
                stock = Stock(supplier=row['Supplier'], location=row['Location'], quantity=quantity,
                              supplier_code=row['Suplier Code'], tidings_code=row['Our Code'])

                db.session.add(stock)
                count += 1
            except SQLAlchemyError:
                errors.append(row)

    db.session.commit()

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


def init_app(app):
    app.cli.add_command(init_db_command)
    app.cli.add_command(seed_db_command)
