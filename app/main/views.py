from . import main
from flask import render_template, request, jsonify, flash
import pymysql
from app.models import Icinga_info
from app.db import db_init
from ..models import Host, Tag, Host_tag_relation
from .forms import InputForm


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
    print(rest_information_cooked)
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


@main.route('/hello2', methods=['GET', 'POST'])
def hello2():
    return render_template("hello2.html")


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
            tmp = []
            ip = host_information.ip
            host_name = host_information.hostname
            tmp.append(ip)
            tmp.append(host_name)
            ip_hostname.append(tmp)
    head = ['IP', 'Hostname']
    return render_template("tag_hostname.html", ip_hostname=ip_hostname, head=head)


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
                    ip_hostname.append(tmp)
            else:
                flash('无效的标签名:' + tag_name)

    return render_template("tag_hostname.html", ip_hostname=ip_hostname, form=form, tag_names=tag_names)
