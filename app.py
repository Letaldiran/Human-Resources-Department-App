import flask
import json
import sqlite3
import datetime
import xml.etree.ElementTree as ET
from db import DB as Database


app = flask.Flask('__main__',
                  static_folder='build/static',
                  template_folder='build')

@app.route('/')
def main():
    '''
    Route for main page
    '''
    token = list() # token - variable in which data on front-end is passed
    return flask.render_template('index.html', token=json.dumps(token)) # rendering of the page


@app.route('/workers')
def workers():
    '''
        Route for page with all workers
        '''
    token = list()
    with sqlite3.connect('database.db') as curr: # sql connection
        conn = curr.cursor() # curr.cursor() - object which can execute sql-request to db
        dbobj = Database() # database object
        token = []
        for worker in dbobj.get_all_workers(conn):
            token += [worker]
    return flask.render_template('index.html', token=json.dumps(token))

@app.route('/orders')
def orders():
    '''
        Route for page with all orders
        '''
    token = list()
    with sqlite3.connect('database.db') as curr:
        conn = curr.cursor()
        dbobj = Database()
        token = []
        for order in dbobj.get_orders(conn):
            token += [order]
    return flask.render_template('index.html', token=json.dumps(token))

@app.route('/subdivisions')
def subdivisions():
    '''
        Route for page with all subdivisions
        '''
    token = list()
    with sqlite3.connect('database.db') as curr:
        conn = curr.cursor()
        dbobj = Database()
        token = []
        for subdivision in dbobj.get_all_subdivisions(conn):
            token += [subdivision]
    return flask.render_template('index.html', token=json.dumps(token))

@app.route('/dismiss_worker_<fullname>')
def delete_worker(fullname):
    '''
        Script for firing specific worker
        '''
    date = datetime.datetime.now().strftime('%Y/%m/%d') # date is modified before being used in sql-query
    fullname = ' '.join(fullname.split('-')) # fullname was modified to be put in link (example: Alexander-Severgin), now its back in normal (ex: Alexander Severgin)
    with sqlite3.connect('database.db') as curr:
        conn = curr.cursor()
        dbobj = Database()
        dbobj.remove_worker(conn, fullname)
        dbobj.add_order(conn, 'Dismissal order', 'Dismissal', fullname + ' was dismissed', date) # With every action order is built
        curr.commit()
    return flask.redirect('/')

@app.route('/edit_worker_<fullname>', methods=['GET','POST'])
def edit_worker(fullname):
    '''
        Route for worker edit page
        '''
    if flask.request.method == 'POST': # if method of request is POST - this function will be deployed
        return edit_worker_deploy(fullname)
    else:
        return edit_worker_page(fullname) # this one if get

def edit_worker_page(fullname):
    '''
        Route for GET-request for editing workers info, loads page with options to change
        '''
    token = dict()
    fullname = ' '.join(fullname.split('-'))
    with sqlite3.connect('database.db') as curr:
        conn = curr.cursor()
        dbobj = Database()
        for line in dbobj.get_worker_by_name(conn, fullname):
            token['table'] = list(line)
        subdvs = []
        for line in dbobj.get_all_subdivisions(conn):
            subdvs += list(line)
        for subdv in subdvs:
            for line in dbobj.get_subdivision_positions(conn, subdv):
                token[subdv] = list(line) # for editing info about worker we need also know all subdivisions and positions there,
                                        # so if transfer to another department happens person would have correct position
    return flask.render_template('index.html', token=json.dumps(token))

def edit_worker_deploy(fullname):
    '''
        Route for POST-request for editing workers info, deploys changes
        '''
    date = datetime.datetime.now().strftime('%Y\%m\%d')
    fullname = ' '.join(fullname.split('-'))
    changes = []
    for i in ['fullname','position','department','salary']:
        changes.append(flask.request.form.get(i)) # gets form values
    with sqlite3.connect('database.db') as curr:
        conn = curr.cursor()
        dbobj = Database()
        for line in dbobj.get_worker_by_name(conn, fullname):
            oldworker = line
        if changes[2] == oldworker[2]: # if there were no changes in department
            ranks_of_department = dbobj.get_subdivision_positions(conn, oldworker[2])[0][0].split(', ')
            oldrank = oldworker[1]
            newrank = changes[1]
            # we would check if new position is higher or lower, on it depends order we create
            if ranks_of_department.index(oldrank) > ranks_of_department.index(newrank):
                dbobj.add_order(conn, 'Descent order', 'Descent', changes[0] + ' was descended to ' + changes[1], date)
            elif ranks_of_department.index(oldrank) < ranks_of_department.index(newrank):
                dbobj.add_order(conn, 'Promotion order', 'Promotion', changes[0] + ' was promoted to ' + changes[1], date)
            dbobj.update_worker(conn, fullname, *changes)
            curr.commit()    # curr.commit - save changes in db
        else:
            # if there were changes in department, then it means it will be transfer order
            dbobj.add_order(conn, 'Transfer order', 'Transferd', changes[0] + ' was transfered from ' + oldworker[2] + ' to ' + changes[2], date)
            dbobj.update_worker(conn, fullname, *changes)
            curr.commit()   

        
    return flask.redirect('/')


@app.route('/add_worker', methods=['GET','POST'])
def add_worker():
    '''
        Route for adding worker
        '''
    if flask.request.method == 'POST':
        return add_worker_deploy()
    else:
        return add_worker_page()

def add_worker_page():
    '''
        Route for GET-method for adding worker, shows page with forms
        '''
    token = dict()
    with sqlite3.connect('database.db') as curr:
        conn = curr.cursor()
        dbobj = Database()
        subdvs = []
        for line in dbobj.get_all_subdivisions(conn):
            subdvs += list(line)
        for subdv in subdvs:
            for line in dbobj.get_subdivision_positions(conn, subdv):
                token[subdv] = list(line)
    return flask.render_template('index.html', token=json.dumps(token))

def add_worker_deploy():
    '''
        Route for adding worker in db
        '''
    changes = []
    date = datetime.datetime.now().strftime('%Y\%m\%d')
    for i in ['fullname','position','department','salary']:
        changes.append(flask.request.form.get(i))
    with sqlite3.connect('database.db') as curr:
        conn = curr.cursor()
        dbobj = Database()
        dbobj.add_worker(conn, *changes)
        # as its new worker, than it means he has been hired so its hiring order
        dbobj.add_order(conn, 'Hiring order', 'Hiring', changes[0] + ' was hired as ' + changes[1], date)
        curr.commit()   
    return flask.redirect('/')

@app.route('/add_subdivision', methods=['GET','POST'])
def add_subdivision():
    '''
            Route for adding subdivision
            '''
    if flask.request.method == 'POST':
        return add_subdivision_deploy()
    else:
        return add_subdivision_page()

def add_subdivision_page():
    '''
       Route for loading form page for adding subdivision
                '''
    token = dict()
    return flask.render_template('index.html', token=json.dumps(token))

def add_subdivision_deploy():
    '''
     Route for adding subdivision in db
                '''
    changes = []
    date = datetime.datetime.now().strftime('%Y\%m\%d')
    changes.append(flask.request.form.get('title'))
    positions = []
    for i in ['first_position','second_position','third_position']:
        positions.append(flask.request.form.get(i))
    changes.append(', '.join(positions))
    changes.append(flask.request.form.get('unitsize'))
    with sqlite3.connect('database.db') as curr:
        conn = curr.cursor()
        dbobj = Database()
        dbobj.add_subdivision(conn, *changes)
        dbobj.add_order(conn, 'New department order', 'Department opening', changes[0] + ' was opened', date)
        curr.commit()
    return flask.redirect('/')

@app.route('/delete_subdivision_<subdivision>')
def delete_subdivision(subdivision):
    '''
        Route for deleting subdivision and all members of it
        '''
    subdivision =  ' '.join(subdivision.split('-'))
    with sqlite3.connect('database.db') as curr:
        conn = curr.cursor()
        dbobj = Database()
        dbobj.remove_subdivision_and_people(conn, subdivision)
        curr.commit()
    return flask.redirect('/')

@app.route('/update_subdivision_<subdivision>', methods=['GET','POST'])
def update_subdivission(subdivision):
    '''
        Route for updating subdivision
        '''
    if flask.request.method == 'POST':
        return update_subdivission_deploy(subdivision)
    else:
        return update_subdivision_page(subdivision)

def update_subdivision_page(subdivision):
    '''
        Route for GET-method of updating subdivision, loads page with data to update
        '''
    with sqlite3.connect('database.db') as curr:
        conn = curr.cursor()
        dbobj = Database()
        for line in dbobj.get_subdivision_by_name(conn, ' '.join(subdivision.split('-'))):
            token = line
    return flask.render_template('index.html', token=json.dumps(token))

def update_subdivission_deploy(subdivision):
    '''
        Route for POST-method of updating subdivision, deploys changes in subdivision data
        '''
    changes = []
    subdivision =  ' '.join(subdivision.split('-'))
    for i in ['title','positions','unitsize']:
        changes.append(flask.request.form.get(i))
    with sqlite3.connect('database.db') as curr:
        conn = curr.cursor()
        dbobj = Database()
        dbobj.update_positions_of_workers_in_subdivision(conn, subdivision, changes[1])
        dbobj.update_subdivisions(conn, subdivision, *changes)
        curr.commit()   
    return flask.redirect('/')

@app.route('/download_<id>')
def download_xml(id):
    '''
        Route for downloading XML-file
        '''
    token = []
    with sqlite3.connect('database.db') as curr:
        conn = curr.cursor()
        dbobj = Database()
        for line in dbobj.get_order(conn, id):
            token = line
    title = token[1]
    type = token[2]
    text = token[3]
    date = token[4]

    #I use library for creating xml. Element which will hold all info is root, new tags like title, type, text are inside. Date is attribute of root
    root = ET.Element('root')
    titleX = ET.SubElement(root, 'title')
    typeX = ET.SubElement(root, 'type')
    textX = ET.SubElement(root, 'text')
    root.set('date',date)
    titleX.text = title
    typeX.text = type
    textX.text = text

    mydata = ET.tostring(root)
    with open(f"./xmls/download_{id}.xml", "wb") as f:
        f.write(mydata)
    # Created xml will be saved to xmls, and flask will send it from xmls directory
    return flask.send_from_directory(directory='./xmls/', filename=f'download_{id}.xml', as_attachment = True)


if __name__ == "__main__":
    app.run(debug=True)
