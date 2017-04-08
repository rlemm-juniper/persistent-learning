#!/usr/bin/python
# -*- coding: utf-8 -*-
from multiprocessing.dummy import Pool as ThreadPool
from multiprocessing import cpu_count
import traceback
from jnpr.junos import Device
from jnpr.junos.exception import RpcError
from jnpr.junos.factory.factory_loader import FactoryLoader
import logging
from logging import getLogger
from logging.handlers import RotatingFileHandler as RFHandler
import multiprocessing.pool
from threading import Thread
from flask import *
import cherrypy
import sys

logfilesize = 1048576
numberofbackups = 3
def setup_logging_to_file(logfile):
    try:
        logging.basicConfig(filename=logfile,
                        filemode='a',
                        level=logging.DEBUG,
                        format='%(asctime)s - %(levelname)s - %(message)s',
                        datefmt='%m/%d/%Y %I:%M:%S %p')
        log = getLogger()
        rotateHandler = RFHandler(logfile, "a", logfilesize, numberofbackups)
        log.addHandler(rotateHandler)

    except Exception, e:
        log_exception(e)
        return str(e)

def extract_function_name():
    try:
        tb = sys.exc_info()[-1]
        stk = traceback.extract_tb(tb, 1)
        fname = stk[0][3]
        return fname

    except Exception, e:
        log_exception(e)
        return str(e)

def log_exception(e):
    try:
        logging.error(
            "Function {function_name} raised {exception_class} ({exception_docstring}): {exception_message}".format(
                function_name=extract_function_name(),
                exception_class=e.__class__,
                exception_docstring=e.__doc__,
                exception_message=e.message))

    except Exception, e:
        log_exception(e)
        return str(e)

t1 = Thread(target=setup_logging_to_file("messages.log"))
t1.start()

results = ''
test = []
macaddr = ''
uname = ''
upass = ''
onedevice = ''
hosts = open('./iplist.txt', 'r')
ip_list = hosts.readlines()
hosts.close()
from flask import *
app = Flask(__name__)

@app.route('/')

def index():
    global macaddr, uname, upass
    ip_list = open('./iplist.txt', 'r')
    hosts_tmp = ip_list.read()
    hosts = hosts_tmp.replace(' ', '')
    ip_list.close()
    try:
        index_html = open("./templates/index.html", "wb")
        process_index_html = Markup('''<html>
        <body>
            <center><form class="container text-center" method="POST" action="/runjob">
                <form action="/runjob"><br><br>
                Username<br><input type="text" name="uname"><br><br>
                Password<br><input type="password" name="upass"><br><br>
                MAC Address<br><input type="text" name="addressinput" enabled><br><br>
            		<br>
            		<br>
                <center><button type="submit" name="button" class="btn btn-primary btn-sml" enabled><strong>OK</strong></button></center><br>
                <center>Click the "OK" button to remove MAC Address from persistent-learning table</center>
                </form></p>
            </form><center>
            <center><form class="container text-center" method="POST" action="/addhosts">
            <textarea name="hosts" cols="25" rows="5">''' + hosts + '''
                </textarea><br><br>
            		<br>
            		<br>
                <center><button type="submit" name="button" class="btn btn-primary btn-sml" enabled><strong>Add EX-Switches</strong></button></center><br>
                <center>Click the "Add EX-Switches" button to add EX-Series Switches</center>
                </form></p>
            </form><center>
        </body>
        </html>''')
        index_html.write(process_index_html + '\n')
        index_html.close()
        return render_template('index.html')

    except Exception, e:
        log_exception(e)
        return str(e)

@app.route('/addhosts', methods=['GET', 'POST'])
def addhosts():
    global ip_list
    hosts_tmp = request.form['hosts']
    hosts_tmp2 = hosts_tmp.replace(' ', '')
    hosts = hosts_tmp2[:-1]
    ex_hosts = open("iplist.txt", "w")
    ex_hosts.write(str(hosts))
    ex_hosts.close()
    hosts_new = open('./iplist.txt', 'r')
    ip_list = hosts_new.readlines()
    hosts_new.close()
    return redirect(url_for('index'))

@app.route('/runjob', methods=['GET', 'POST'])

def runjob():
    global macaddr, uname, upass
    macaddr = request.form.get("addressinput")
    uname = request.form.get("uname")
    upass = request.form.get("upass")
    onefn(multiRun)
    return redirect(url_for('index'))

def process_device(ip, **kwargs):
    global macaddr, uname, upass
    dev = Device(host=ip, **kwargs)
    logging.info('Processing ' + ip)
    try:
        dev.open(gather_facts = False)
        dev.rpc.clear_ethernet_switching_table_persistent_learning_mac(address=macaddr)

    except RpcError:
        msg = "{0} was Skipped due to RPC Error.  Device is not EX Series Switch (ELS)".format(ip.rstrip())
        logging.info(msg)
        dev.close()

    except Exception, e:
        e = "{0} was skipped due to unhandled exception.\n{1}".format(ip.rstrip(), err)
        log_exception(e)
        return str(e)
        dev.close()

    dev.close()

def Run(ip):
    test.append(ip)
    result = process_device(ip, user=uname, password=upass)
    return result

def multiRun():
    pool = ThreadPool(cpu_count() * 16)
    global ip_list
    global results
    results = pool.map_async(Run, ip_list)
    pool.close()
    pool.join()

def onefn(runner):
    runner()

def run_web_server():
    try:
        logging.info('Starting Web Server')
        cherrypy.tree.graft(app, "/")
        cherrypy.server.unsubscribe()
        server = cherrypy._cpserver.Server()
        server.socket_host = "0.0.0.0"
        server.socket_port = 443
        server.thread_pool = 1000
        server.ssl_module = 'pyopenssl'
        server.ssl_certificate = 'server.crt'
        server.ssl_private_key = 'server.key'
        server.subscribe()
        cherrypy.engine.start()
        cherrypy.engine.block()

    except Exception, e:
        log_exception(e)
        return str(e)

t1 = Thread(target=run_web_server)
t1.start()
