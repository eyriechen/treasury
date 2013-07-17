#!/usr/bin/env python
# -*- coding: utf-8 -*-

import webapp2
import jinja2
import os

from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.ext.db import Key
import logging

import datetime

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

def validate_user(page):
    user = users.get_current_user()
    if user:
        logging.info("request from "+user.email())
        if user.email() == "eyriechen@gmail.com":
            pass
        else:
            pass
        #    page.redirect('/error')
    else:
        page.redirect(users.create_login_url(page.request.uri))

class Record(db.Model):
    date = db.DateProperty()
    usage = db.StringProperty()
    place = db.StringProperty()
    amount = db.FloatProperty()

class Person(db.Model):
    name = db.StringProperty()

class Card(db.Model):
    card_number = db.StringProperty()
    issuer = db.StringProperty()
    expiration_date = db.StringProperty()
    card_type = db.StringProperty()
    holder = db.StringProperty()
    balance = db.FloatProperty()
    icon = db.StringProperty()

class MainHandler(webapp2.RequestHandler):
    def get(self):
        validate_user(self)
        self.response.write('Hello world!')

class AddPerson(webapp2.RequestHandler):
    def get(self):
        validate_user(self)
        persons = db.GqlQuery("SELECT * FROM Person")
        self.response.headers['Content-Type'] = 'text/html'
        self.response.write("""
<html>
<head>
    <meta charset="utf-8">
    <title>添加用户</title>
</head>
<body>
    <form method="post">
        """)
        for person in persons:
            if person.name:
                self.response.write("""
<p>%s</p>
                """%(person.name) )
        self.response.write("""
        <input type="text" name="person_name"/>
        <input type="submit" value="添加"/>
    </form>
</body>
        """)
    def post(self):
        validate_user(self)
        person_name = self.request.get('person_name')
        person = Person()
        person.name = person_name
        person.put()
        self.redirect('/add_person')

class AddCard(webapp2.RequestHandler):
    def get(self):
        validate_user(self)
        persons = db.GqlQuery("SELECT * FROM Person")
        cards = db.GqlQuery("SELECT * FROM Card")
        self.response.headers['Content-Type'] = 'text/html'
        self.response.write("""
<html>
<head>
    <meta charset="utf-8">
    <title>添加卡</title>
</head>
<body>
    """)
        for card in cards:
            self.response.write("""
            <div>%s,%s,%s,%s</div>
    """%(card.holder,card.issuer,card.card_number,card.balance))
        self.response.write("""
    <p>持卡人:</p>
    <form method="post">
        <select name="person_name">
    """)
        for person in persons:
            if person.name:
                self.response.write("""
                <option vaule="%s">%s</option>
                """%(person.name,person.name))
        self.response.write("""
        </select>
        <p>卡号:</p>
        <input type="text" name="card_number"/>
        <p>发行银行:</p>
        <input type="text" name="issuer"/>
        <p>类型:</p>
        <select name="card_type">
            <option value="信用卡">信用卡</option>
            <option value="储蓄卡">储蓄卡</option>
            <option value="工资卡">工资卡</option>
        </select>
        <p>余额:</p>
        <input type="text" name="balance"/>
        <p>过期时间(MMYY):</p>
        <input type="text" name="expiration_date"/>
        <input type="submit" value="添加"/>
    </form>
</body>
        """)
    def post(self):
        validate_user(self)
        person_name = self.request.get('person_name')
        card_number = self.request.get('card_number')
        issuer = self.request.get('issuer')
        card_type = self.request.get('card_type')
        balance = self.request.get('balance')
        expiration_date = self.request.get('expiration_date')


        queryPerson = db.GqlQuery("SELECT * FROM Person where name = :1 LIMIT 1",person_name)
        person = queryPerson.get()

        card = Card(parent=person)
        card.card_number = card_number
        card.card_type = card_type
        card.issuer = issuer
        card.balance = float(balance)
        if expiration_date:
            card.expiration_date = expiration_date
        card.holder = person.name
        card.put()

        self.redirect('/add_card')
class Sheet(webapp2.RequestHandler):
    def get(self):
        cards = db.GqlQuery("SELECT * FROM Card")
        totalBalance = 0.0
        for card in cards:
            totalBalance += card.balance
        template_values = {
            'cards': cards,
            'totalBalance': totalBalance,
        }
        template = jinja_environment.get_template('sheet.html')
        self.response.out.write(template.render(template_values))

class CardDetail(webapp2.RequestHandler):
    def get(self):
        key = self.request.get('key')
        q = Card.all()
        q.filter('__key__ = ',Key(key))
        card = q.get()
        
        q = Record.all()
        q.ancestor(card)
        q.order('-date')
        records = q.run()

        template_values = {
            'card': card,
            'records': records,
        }
        template = jinja_environment.get_template('card_detail.html')
        self.response.out.write(template.render(template_values))

class AddRecord(webapp2.RequestHandler):
    def post(self):
        date = self.request.get('date')
        parent = self.request.get('parent')
        place = self.request.get('place')
        usage = self.request.get('usage')
        amount = float(self.request.get('amount'))


        q = Card.all()
        q.filter('__key__ = ',Key(parent))
        card = q.get()

        record  = Record(parent=card)
        record.date = datetime.datetime.strptime(date,'%Y-%m-%d').date()
        record.usage = usage;
        record.place = place;
        record.amount = amount;
        record.put()

        card.balance += amount
        card.put()

        self.response.out.write(parent);

class ErrorPage(webapp2.RequestHandler):
    def get(self):
        url = users.create_login_url(self.request.uri)
        self.response.out.write("""
        Error<br/><a href="%s">sign in</a>
        """%url);


app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/add_person', AddPerson),
    ('/add_card', AddCard),
    ('/card_detail',CardDetail),
    ('/add_record',AddRecord),
    ('/sheet',Sheet),
    ('/error',ErrorPage)
], debug=True)

