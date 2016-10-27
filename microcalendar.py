import os
import re
from flask import Flask
from functools import wraps
from flask import request, Response, render_template, g
from datetime import date
import calendar
from flask.ext.wtf import Form
from wtforms import StringField, validators, HiddenField, SubmitField, DateField
import sqlite3
import storage
from settings import settings


app = Flask(__name__)
app.config.from_object('flask_config')


@app.teardown_appcontext
def close_connection(exception):
    storage.close()


#=========================================================================

def check_auth(username, password):
    return username == settings['login'] and password == settings['password']


def authenticate():
    return Response('invalid password', 401, {'WWW-Authenticate': 'Basic realm="Login Required"'})


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

#=========================================================================


def get_prev_month(year, month):
    if month == 1:
        return year - 1, 12
    else:
        return year, month - 1


def get_next_month(year, month):
    if month == 12:
        return year + 1, 1
    else:
        return year, month + 1


def parse_date(date):
    m = re.match("^([0-9]{4})-([0-9]{1,2})(-([0-9]{1,2}))?$", date)
    if m:
        year = m.group(1)
        month = m.group(2)
        day = m.group(4)
        if day is None:
            day = 0
        return int(year), int(month), int(day)
    return 0, 0, 0


def date_to_string(year, month, day=0):
    if day != 0:
        return "{0}-{1:0>2}-{2:0>2}".format(year, month, day)
    else:
        return "{0}-{1:0>2}".format(year, month)


def state_to_backcolor(state):
    if state == 'active':
        return settings['color_active']
    elif state == 'done':
        return settings['color_done']
    else:
        return 'ffffff'


def create_link(page_url):
    return "{0}/{1}".format(settings["application_url"], page_url).replace("//", "/")


def move_calendar(year, month, id):
    task = storage.get_task(id)

    cal = calendar.Calendar(0)
    month_cal = cal.monthdatescalendar(year, month)

    month_data = []

    for week in month_cal:
        week_data = []
        for day in week:
            day_data = {}
            day_data['move_link'] = create_link('/move-task/{0}/{1}-{2}-{3}'.format(id, day.year, day.month, day.day))
            day_data['day'] = day.day
            if date_to_string(day.year, day.month, day.day) == task['date']:
                day_data['backcolor'] = settings['color_active']
            elif day == date.today():
                day_data['backcolor'] = settings['color_today']
            elif day.weekday() > 4:
                day_data['backcolor'] = settings['color_weekend']
            else:
                day_data['backcolor'] = '#ffffff'
            week_data.append(day_data)
        month_data.append(week_data)

    return month_data

#=========================================================================


class TaskEditForm(Form):
    date = HiddenField('date')
    id = HiddenField('id')
    state = HiddenField('state')

    task_text = StringField('text', [validators.Length(min=1, max=1000)])

    submit_edit = SubmitField(label='ok')
    submit_done = SubmitField(label='done')
    submit_delete = SubmitField(label='delete')
    submit_activate = SubmitField(label='activate')
    submit_back = SubmitField(label='back')

#=========================================================================


@app.route(settings['route_url'] + '/save-task', methods=['GET', 'POST'])
@requires_auth
def save_task_page():
    form = TaskEditForm()

    if form.submit_back.data:
        return calendar_page(create_link("/{0}".format(form.date.data)))

    id = int(form.id.data)

    if form.validate_on_submit():
        if form.submit_delete.data == True:
            storage.delete_task(id)

        elif form.submit_done.data == True:
            storage.edit_task(id, date=form.date.data, task=form.task_text.data, state='done', color='default')

        elif form.submit_activate.data == True:
            storage.edit_task(id, date=form.date.data, task=form.task_text.data, state='active', color='default')

        elif form.submit_edit.data == True:
            if id < 0:
                storage.create_task(date=form.date.data, task=form.task_text.data, color='default')
            else:
                storage.edit_task(id=id, date=form.date.data, task=form.task_text.data, state=form.state.data, color='default')

        return calendar_page(create_link("/{0}".format(form.date.data)))

    else:
        if id < 0:
            return create_task_page(form.date.data)
        else:
            return edit_task_page(id)


@app.route(settings['route_url'] + '/move-task/<id>/<date>')
@requires_auth
def move_task_page(id, date):
    id = int(id)
    year, month, day = parse_date(date)
    storage.edit_task_date(id, date_to_string(year, month, day))
    return calendar_page(create_link("/{0}".format(date_to_string(year, month))))


@app.route(settings['route_url'] + '/create-task/<date>')
@requires_auth
def create_task_page(date):
    form = TaskEditForm()
    form.date.data = date
    form.id.data = -1
    form.state.data = 'active'

    data = {}
    data['title'] = 'create task'
    data['state'] = 'create'
    data['save_task_link'] = create_link('/save-task')

    return render_template('edit-task.html', form=form, data=data)


@app.route(settings['route_url'] + '/edit-task/<id>')
@requires_auth
def edit_task_page(id):
    r = storage.get_task(id)

    form = TaskEditForm()
    form.id.data = id
    form.date.data = r['date']
    form.task_text.data = r['task']
    form.state.data = r['state']

    data = {}
    data['title'] = 'edit task'
    data['state'] = r['state']
    data['save_task_link'] = create_link('/save-task')

    cur_year, cur_month, cur_day = parse_date(r['date'])
    prev_year, prev_month = get_prev_month(cur_year, cur_month)
    next_year, next_month = get_next_month(cur_year, cur_month)

    data['move_prev_month'] = move_calendar(prev_year, prev_month, id)
    data['move_prev_month_title'] = calendar.month_name[prev_month].lower()[:3]
    data['move_cur_month'] = move_calendar(cur_year, cur_month, id)
    data['move_cur_month_title'] = calendar.month_name[cur_month].lower()[:3]
    data['move_next_month'] = move_calendar(next_year, next_month, id)
    data['move_next_month_title'] = calendar.month_name[next_month].lower()[:3]

    return render_template('edit-task.html', form=form, data=data)


root_url = settings['route_url']
if root_url == "":
    root_url = "/"


@app.route(root_url, defaults={'page_date': ''})
@app.route(settings['route_url'] + '/<page_date>')
@requires_auth
def calendar_page(page_date):
    year, month, day = parse_date(page_date)

    today = date.today()

    if year == 0 or month == 0:
        year = today.year
        month = today.month

    cal = calendar.Calendar(0)
    month_cal = cal.monthdatescalendar(year, month)

    date_start = month_cal[0][0]
    date_end = month_cal[len(month_cal) - 1][len(month_cal[len(month_cal) - 1]) - 1]

    tasks = storage.get_tasks(date_start, date_end)

    month_data = []

    for week in month_cal:
        week_data = []
        for day in week:
            day_data = {}
            day_data['day'] = day.day

            if day == today:
                day_data['header_backcolor'] = settings['color_today']
            elif day.weekday() > 4:
                day_data['header_backcolor'] = settings['color_weekend']
            else:
                day_data['header_backcolor'] = settings['color_header']

            day_data['create_task_link'] = create_link('/create-task/{0}'.format(date_to_string(day.year, day.month, day.day)))
            day_data['tasks'] = []
            for db_task in tasks:
                if str(day) == db_task['date']:
                    html_task = {}
                    html_task['id'] = db_task['id']
                    html_task['date'] = db_task['date']
                    html_task['task'] = db_task['task']
                    html_task['edit_link'] = create_link('/edit-task/{0}'.format(db_task['id']))
                    html_task['backcolor'] = state_to_backcolor(db_task['state'])
                    day_data['tasks'].append(html_task)

            week_data.append(day_data)
        month_data.append(week_data)

    data = {'month': month_data}

    prev_year, prev_month = get_prev_month(year, month)
    next_year, next_month = get_next_month(year, month)

    data['prev_month_link'] = create_link(str.format('/{0}', date_to_string(prev_year, prev_month)))
    data['next_month_link'] = create_link(str.format('/{0}', date_to_string(next_year, next_month)))

    data["title"] = "{0} {1}".format(year, calendar.month_name[month])

    return render_template('month.html', data=data)


if __name__ == "__main__":
    app.debug = True
    app.run(host='0.0.0.0')
