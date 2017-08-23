from . import main
from flask import render_template, request, jsonify, flash
import pymysql
from app.models import Icinga_info
import json,urllib
from app.db import db_init
from ..models import Host, Tag, Host_tag_relation
from .forms import InputForm, GetClusterResourceForm
import requests


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
#    print(rest_information_cooked)
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


@main.route('/dcos_cluster', methods=['GET', 'POST'])
def dcos_cluster():
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
    return render_template("dcos_cluster.html",mesos=dmz_mesos,marathon=marathon)

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
            print("failed to get url: {} ".format(url))
        if baseurl:
            break

    if baseurl is None:
        raise Exception
    return baseurl

def get_redirected_url(url):
    opener = urllib.request.build_opener(urllib.request.HTTPRedirectHandler)
    request = opener.open(url, timeout=10)
    return request.url

@main.route('/v1/cmdb/tag=<string:tag_name_pool>', methods=['GET', 'POST'])
def get_host_information(tag_name_pool):
    tag_names = tag_name_pool.split(',')
    ip_hostname = []
    for tag_name in tag_names:
        tag_id = Tag.query.filter_by(tag_name=tag_name).all()[0].id
        host_ids = Host_tag_relation.query.filter_by(tag_name=tag_id).all()
        ids = []
        for host_id in host_ids:
            ids.append(host_id.host_id)
        host_informations = []
        for id in ids:
            host_informations.append(Host.query.filter_by(id=id).all()[0])
        for host_information in host_informations:
            tmp = {}
            ip = host_information.ip
            host_name = host_information.hostname
            tmp['ip'] = ip
            tmp['host_name'] = host_name
            tmp['tag_name'] = tag_name
            ip_hostname.append(tmp)
    info_ip_hostname = {'info': ip_hostname}
    json_ip_hostname = json.dumps(info_ip_hostname)
    return json_ip_hostname


@main.route('/cmdb/tag', methods=['GET', 'POST'])
def get_host_information_show():
    tag_names_database_pool = []
    tag_names_database = Tag.query.all()
    for item in tag_names_database:
        tag_names_database_pool.append(item.tag_name)

    tag_names = None
    form = InputForm()
    ip_hostname, head = [], []
    if form.validate_on_submit():
        tag_names = form.tag_names.data.split(',')
        form.tag_names.data = ''
        for item in tag_names:
            tag_name = item.strip()
            if tag_name in tag_names_database_pool:
                tag_id = Tag.query.filter_by(tag_name=tag_name).all()[0].id
                host_ids = Host_tag_relation.query.filter_by(tag_name=tag_id).all()
                ids = []
                for host_id in host_ids:
                    ids.append(host_id.host_id)
                host_informations = []
                for id in ids:
                    host_informations.append(Host.query.filter_by(id=id).all()[0])
                for host_information in host_informations:
                    tmp = []
                    ip = host_information.ip
                    host_name = host_information.hostname
                    tmp.append(ip)
                    tmp.append(host_name)
                    tmp.append(tag_name)
                    ip_hostname.append(tmp)
            else:
                flash('无效的标签名:' + tag_name)

    return render_template("tag_hostname.html", ip_hostname=ip_hostname, form=form, tag_names=tag_names)


@main.route('/cluster_resource', methods=['POST', 'GET'])
def cluster_resource():

    zj01_name, mesos_master_name = "zj-dcos01", "mesos-master"
    zj01_mesos_ips = ["20.26.25.11:5050", "20.26.25.12:5050", "20.26.25.13:5050"]
    mesos_master_ips = ["20.26.28.22:5050", "20.26.28.23:5050", "20.26.28.24:5050"]
    zj01_tmp = get_mesos_leader(zj01_mesos_ips)
    zj01_mesos_leader = zj01_tmp + "master/state"
    mesos_master_tmp = get_mesos_leader(mesos_master_ips)
    mesos_master_leader = mesos_master_tmp + "master/state"

    zj01_resource = get_cluster_resource(zj01_mesos_leader)
    zj01_attribute_name, zj01_attribute_resources = zj01_resource[0], zj01_resource[1]
    mesos_master_resource = get_cluster_resource(mesos_master_leader)
    mesos_attribute_name, mesos_master_attribute_resources = mesos_master_resource[0], mesos_master_resource[1]

    return render_template("get_cluster_resource.html",
                           zj01_name=zj01_name,
                           zj01_attribute_names=zj01_attribute_name,
                           zj01_attribute_resources=zj01_attribute_resources,
                           mesos_master_name=mesos_master_name,
                           mesos_attribute_names=mesos_attribute_name,
                           mesos_master_attribute_resources=mesos_master_attribute_resources)


def get_cluster_resource(url):
    headers = {
        "User-Agent": "Mozilla / 5.0(Windows NT 6.1;Win64;x64)"
                      "AppleWebKit / 537.36(KHTML, likeGecko)"
                      "Chrome / 58.0.3029.110"
                      "Safari / 537.36",
    }
    html = requests.get(url=url, headers=headers).text
    jsonstr = json.loads(html)

    res = []
    attributes_all = []
    attributes_resources = {}
    attributes_prefixs = set()
    for slave in jsonstr['slaves']:
        attributes_prefix_tmp = slave['attributes'].keys()
        for item in attributes_prefix_tmp:
            attributes_prefixs.add(item)
        for attributes_prefix in attributes_prefixs:
            attributes = attributes_prefix + ':' + slave['attributes'][attributes_prefix]
            if attributes not in attributes_all:
                attributes_all.append(attributes)
            resources = slave['resources']
            used_resources = slave['used_resources']
            cpus_left = resources['cpus'] - used_resources['cpus']
            mem_left = resources['mem'] - used_resources['mem']
            disk_left = resources['disk'] - used_resources['disk']
            ports_used = len(used_resources['ports'].split(',')) if 'ports' in used_resources.keys() else 0
            ports_tmp = resources['ports'].split('-')
            ports_total = int(ports_tmp[1][:-1]) - int(ports_tmp[0][1:])
            ports_left = ports_total - ports_used

            if attributes not in attributes_resources:
                attributes_resources[attributes] = {}
                attributes_resources[attributes]['cpus_left'] = cpus_left
                attributes_resources[attributes]['mem_left'] = mem_left
                attributes_resources[attributes]['disk_left'] = disk_left
                attributes_resources[attributes]['ports_left'] = ports_left
            else:
                attributes_resources[attributes]['cpus_left'] += cpus_left
                attributes_resources[attributes]['mem_left'] += mem_left
                attributes_resources[attributes]['disk_left'] += disk_left
                attributes_resources[attributes]['ports_left'] += ports_left

    res.append(attributes_all)
    res.append(attributes_resources)
    return res
