from flask import Flask
from functools import wraps
from flask import request, Response, redirect
from flask import render_template
from calendar import Calendar
from datetime import date
import calendar
from flask.ext.wtf import Form
from wtforms import BooleanField, StringField, PasswordField, validators, HiddenField, SubmitField
import sqlite3
from flask import g
import os


DATABASE = 'sqlite.db'


def init_db(db):
    cur = db.cursor()
    cur.execute(
        'CREATE TABLE tasks (id INTEGER PRIMARY KEY ASC, date TEXT, task TEXT, state TEXT, color TEXT)')
    db.commit()


def get_db():
    new_database = False
    if not os.path.isfile(DATABASE):
        new_database = True

    db = getattr(g, '_database', None)
    if db is None:
        db = sqlite3.connect(DATABASE)
        g._database = db

    if new_database:
        init_db(db)

    db.row_factory = sqlite3.Row

    return db


def close():
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


def execute_non_query(q, params):
    db = get_db()
    cur = db.cursor()
    cur.execute(q, params)
    db.commit()


def execute_fetch_all(q, params):
    db = get_db()
    cur = db.execute(q, params)
    rs = cur.fetchall()
    cur.close()
    return rs


def execute_fetch_first(q, params):
    return execute_fetch_all(q, params)[0]


def create_task(date, task, color):
    execute_non_query(
        "INSERT INTO tasks (id, date, task, state, color) VALUES (NULL, ?, ?, ?, ?)", (date, task, 'active', color))


def edit_task(id, date, task, state, color):
    execute_non_query(
        'UPDATE tasks SET date=?, task=?, state=?, color=? WHERE id=?', (date, task, state, color, id))


def delete_task(id):
    execute_non_query('DELETE FROM tasks WHERE id=?', (id,))


def get_tasks(date_start, date_end):
    return execute_fetch_all('SELECT * from tasks WHERE date>=date(?) and date<=date(?)', (str(date_start), str(date_end)))


def get_task(id):
    return execute_fetch_first('SELECT * FROM tasks WHERE id=?', (id,))
