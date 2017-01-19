from flask import Flask, g
from flask_restful import Resource, Api, reqparse
import sqlite3
import os
import sys
import datetime
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Text, create_engine, desc
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.orm.exc import NoResultFound
from flask_cors import CORS, cross_origin
from flask_socketio import SocketIO, send, emit

Base = declarative_base()

class ProductType(Base):
    __tablename__ = 'ProductType'
    id = Column(Integer, primary_key=True)
    ProductName = Column(String(250), nullable=False)

class Product(Base):
    __tablename__ = 'Product'
    id = Column(Integer, primary_key=True)
    TypeId = Column(Integer, nullable=False, ForeignKey(ProductType.id))
    Descriptor = Column(String(250), default=None)
    QNUM = Column(Integer, default=None)
    QMass = Column(Integer, default=None)
    Notes = Column(Text(), default=None)

engine = create_engine('sqlite:///inventory.db')
Base.metadata.create_all(engine)
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)

session = DBSession()

app = Flask(__name__)
CORS(app)
api = Api(app)
socketio = SocketIO(app)


class Products(Resource):
    def get(self):
        try:

            try:
                products = session.query(Product).all()
            except NoResultFound:
                products = []

            parsed_products = []

            for product in products:
                temp_product = {
                    'QNUM': product.QNUM,
                    'QMass': product.QMass,
                    'Descriptor': product.Descriptor,
                    'Notes': product.Notes,
                    'id': product.id,
                    'TypeId': product.TypeId
                }
                parsed_products.append(temp_product)
            return {
                'products': parsed_products
            }

        except Exception as e:
            return {'error': str(e)}

    def post(self):
        try:
            parser = reqparse.RequestParser()
            parser.add_argument('id', type=int, help='id for product to be added to the db')
            parser.add_argument('TypeId', type=int, help='id for name of product to be added to the db')
            parser.add_argument('QNUM', type=int, help='quantity of product in numerical total to be added to the db')
            parser.add_argument('QMass', type=int, help='the quantity in mass of product to be added to the db')
            parser.add_argument('Descriptor', type=str, help='the strain or descriptor of product to be added to the db')
            parser.add_argument('Notes', type=str, help='notes of product to be added to the db')


            args = parser.parse_args()

            if args['Id'] is not None:
                product = session.query(Product).filter(Product.id == args['id']).first()
                product.Notes = args['Notes']
                product.QNUM = args['QNUM']
                product.QMass = args['QMass']
                product.Descriptor = args['Descriptor']
            else:
                new_product = Product(TypeId=args['TypeId'], QNUM=args['QNUM'], Descriptor=args['Descriptor']
                    QMass=args['QMass'], Notes=args['Notes'])
                session.add(new_product)

            session.commit()

            return {'product': 'success'}

        except Exception as e:
            return {'error': str(e)}

api.add_resource(Products, '/products')



if __name__ == '__main__':
    socketio.run(app)
