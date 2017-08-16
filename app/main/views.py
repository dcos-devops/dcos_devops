from . import main
from flask import render_template, request, jsonify
import pymysql
from app.models import Icinga_info
from app.db import db_init 
import json,urllib

@main.route('/', methods=['GET', 'POST'])
def index():
    sql_info = "SELECT DISTINCT LEVEL from icinga_info"
    levels = db_init.execute_sql(sql_info)
    return render_template('index.html', levels=levels)


@main.route('/get_ip', methods=['GET'])
def get_ip():
    level = request.args.get('level')
    sql_info = 'SELECT DISTINCT ip from icinga_info WHERE LEVEL = {}'.format(repr(level))
    ip_raw = db_init.execute_sql(sql_info)
    ip_pool = []
    for ip in ip_raw:
        ip_pool.append(ip[0])
    ip_cooked = {"ip": ip_pool}
    return jsonify(ip_cooked)


@main.route('/get_rest_information', methods=['GET'])
def get_table_information():
    level = request.args.get('level')
    ip = request.args.get('ip')
    table_information = [('Time', 'IP', 'Service', 'Message')]
    rest_information_raw = Icinga_info.query.filter_by(ip=ip, level=level).all()
    for item in rest_information_raw:
        table_information.append((item.time, item.ip, item.service, item.message))
    rest_information_cooked = {"information": table_information}

    return jsonify(rest_information_cooked)

#    page = request.args.get('page', 1, type=int)
#    pagination = Icinga_info.query.filter_by(ip=ip, level=level).paginate(
#        page, per_page=2, error_out=False
#    )
#    posts = pagination.items
#    print(posts)
#    return render_template("test.html", pagination=pagination, posts=posts)


@main.route('/get_service_time', methods=['GET'])
def get_service_time():
    level = request.args.get('level')
    ip = request.args.get('ip')
    sql_info = "select service, count(*) from icinga_info where ip='{}' and level='{}' GROUP BY service;".format(ip, level)
    service_time, service_name = [], []
    d = []
    service_information_raw = db_init.execute_sql(sql_info)
    for item in service_information_raw:
        a = {}
        a['value']=item[1]
        a['name'] = item[0]
        d.append(a)
        service_name.append(item[0])
        service_time.append((item[1]))
    #print(service_name,service_time)

    service_information = {"service_name": service_name, "service_time": service_time, "d": d}
    return jsonify(service_information)


@main.route('/hello1', methods=['GET', 'POST'])
def hello1():
    return render_template("hello1.html",mesos=mesos)


@main.route('/hello2', methods=['GET', 'POST'])
def hello2():
    dmz_mesos_ips=["20.26.28.22:5050","20.26.28.23:5050","20.26.28.24:5050"]
    dmz_marathon_ips=["20.26.28.25","20.26.28.26"]
    dmz_mesos=[]
    # mesos=[("mesos-master","http://192.168.0.1:5050","No",1),("mesos-master","192.168.0.2","No",1),("mesos-master","192.168.0.3","No",0)]
    marathon=[]
    dmz_mesos_leader = get_mesos_leader(dmz_mesos_ips)
    for mesosip in dmz_mesos_ips:
        obj = MesosChecker(mesosip.split(":")[0],mesosip.split(":")[1])
        _is_ok = obj.check()
        _is_leader = ["No" if dmz_mesos_leader.split("//")[-1].strip('/') != mesosip else "Yes"][0]
        info = ("mesos-master","http://{}".format(mesosip),_is_leader,_is_ok)
        dmz_mesos.append(info)
    
    # dmz_maraton_leader = get_marathon_leader(dmz_marathon_ips)
    
    


    return render_template("hello2.html",mesos=dmz_mesos,marathon=marathon)



class MesosChecker:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port

    def _get_url(self):
        return 'http://{}:{}/metrics/snapshot'.format(self.ip, self.port)

    def check(self):
        try:
            node = self._get_url()
            response = urllib.request.urlopen(node, timeout=10)
            return True
        except:
            return False


def get_mesos_leader(mesos_master_nodes):
    for mmn in mesos_master_nodes:
        baseurl = None
        try:
            url = "http://{0}/redirect".format(mmn)
            baseurl = get_redirected_url(url)
        except Exception as e:
            logger.error("failed to get url: {} ".format(url))
            logger.exception(e)
        if baseurl:
            break

    if baseurl is None:
        raise Exception
    return baseurl

def get_redirected_url(url):
    opener = urllib.request.build_opener(urllib.request.HTTPRedirectHandler)
    request = opener.open(url, timeout=10)
    return request.url
