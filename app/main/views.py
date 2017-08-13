from . import main
from flask import render_template, request, jsonify
import pymysql
from app.models import Icinga_info
from app.db import db_init 

@main.route('/', methods=['GET', 'POST'])
def index():
    sql_info = "SELECT DISTINCT LEVEL from icinga_info"
    levels = db_init.execute_sql(sql_info)
    return render_template('index_pie.html', levels=levels)


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
def get_rest_information():
    level = request.args.get('level')
    ip = request.args.get('ip')
    rest_information = []
    rest_information_raw = Icinga_info.query.filter_by(ip=ip, level=level).all()
    for item in rest_information_raw:
        rest_information.append((item.time, item.ip, item.service, item.message))
    rest_information_cooked = {"information": rest_information}

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
    print(service_name,service_time)

    service_information = {"service_name": service_name, "service_time": service_time, "d": d}
    return jsonify(service_information)
