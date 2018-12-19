from datetime import datetime

from flask import g

from grotto import db


class Stock(db.Model):
    __tablename__ = 'stock'
    id = db.Column(db.Integer(), primary_key=True)
    supplier_code = db.Column(db.String())
    tidings_code = db.Column(db.String())
    supplier = db.Column(db.String())
    location = db.Column(db.String())
    quantity = db.Column(db.Integer())
    last_modified = db.Column(db.String())

    def __init__(self, supplier, location, quantity, supplier_code=None, tidings_code=None):
        self.supplier_code = supplier_code
        self.tidings_code = tidings_code
        self.supplier = supplier
        self.location = location
        self.quantity = quantity

        now = datetime.now().strftime("%d-%m-%Y")

        try:
            user = g.current_user.username
        except AttributeError:
            user = 'Admin'

        self.last_modified = '{0} - {1}'.format(now, user)

    def to_json(self):
        return {
            'id': self.id,
            'supplier_code': self.supplier_code,
            'tidings_code': self.tidings_code,
            'supplier': self.supplier,
            'location': self.location,
            'quantity': self.quantity,
            'last_modified': self.last_modified
        }

    def __repr__(self):
        if self.supplier_code:
            code = self.supplier_code
        elif self.tidings_code:
            code = self.tidings_code
        else:
            code = 'No code provided.'

        return '<Item {0}>'.format(code)
