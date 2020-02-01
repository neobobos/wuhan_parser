# -*- coding: utf-8 -*-
import requests
import re
import time
import re
from lxml import etree
import json
import pymysql
import operator
MYSQL_HOST ='127.0.0.1'
MYSQL_USER = 'root'  #
MYSQL_PASSWD = ''  #
MYSQL_PORT = 3306
MYSQL_DATA_DB = 'wuhan'
MYSQL_CHARSET = 'utf8mb4'

def dxy_sarl():
    url='https://3g.dxy.cn/newh5/view/pneumonia_peopleapp?from=timeline&isappinstalled=0'
    headers={
        'authority': '3g.dxy.cn',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        'user-agent': 'Mozilla/5.0 (Linux; U; Android 8.0; zh-cn; Chitanda/Akari) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30   micromessage/6.0.0.58_r884092.501 NetType/WIFI'
    }
    res = requests.get(url,headers=headers)
    res.encoding='utf-8'
    return res.text


def baidu_sarl():
    url = 'https://opendata.baidu.com/data/inner?tn=reserved_all_res_tn&dspName=iphone&from_sf=1&dsp=iphone&resource_id=28565&alr=1&query=%E8%82%BA%E7%82%8E&cb='
    url = 'https://voice.baidu.com/act/newpneumonia/newpneumonia'
    headers={
        'authority': 'opendata.baidu.com',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
        'user-agent': 'Mozilla/5.0 (Linux; U; Android 8.0; zh-cn; Chitanda/Akari) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30   micromessage/6.0.0.58_r884092.501 NetType/WIFI'
    }
    res = requests.get(url,headers=headers)
    res.encoding='utf-8'
    return res.text



def run_data_baidu(txt):
    data_dict = re.findall('V\.conf = (.*?);V\.bsData', txt)
    res = data_dict[0]
    data = json.loads(res)
    for i in data['component']:
        if isinstance(i,dict):
            for ii in i:
                if ii=='summaryDataIn':
                    total_data=i[ii]
        else:
            total_data=None
    truncate_db('sarl')
    insert_date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    print(total_data)
    province = {"provinceShortName": "全国",
                "confirmedCount": total_data['confirmed'] if total_data else 0,
                "suspectedCount": total_data['unconfirmed'] if total_data else 0,
                "curedCount": total_data['cured'] if total_data else 0,
                "deadCount": total_data['died'] if total_data else 0,
                "modifyTime": insert_date,
                "tags": "",
                "insert_date": insert_date}
    # print(province)
    table_name = 'sarl'
    cols, values = zip(*province.items())
    insert_into(table_name, cols, values)

    data_city = data['component'][0]['caseList']
    for k in data_city:
        insert_date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        # print(k)
        cities= k['subList']
        for index,city in enumerate(cities):
            if isinstance(city,dict):
                for x,y in city.items():
                    if y=='' or y=="" or y==[] or y=='[]':
                        #print(x,y,'------')
                        cities[index][x]=0
                    if y.isdigit():
                        cities[index][x]=int(y)
            else:
                cities='[]'
        if cities !='[]':
            try:
                city_str = str(sorted(cities, key=operator.itemgetter('confirmed'), reverse=True))
            except Exception as e:
                print(e,cities)
        else:
            city_str=cities

        province = {"provinceShortName": k['area'] if 'area' in k.keys() else 0,
                    "city": city_str,
                    "confirmedCount": k['confirmed'] if 'confirmed' in k.keys() and str(k['confirmed']).isdigit() else 0,
                    "suspectedCount": k['unconfirmed'] if 'unconfirmed' in k.keys() and str(k['unconfirmed']).isdigit() else 0,
                    "curedCount": k['crued'] if 'crued' in k.keys() and str(k['crued']).isdigit() else 0,
                    "deadCount": k['died'] if 'died' in k.keys() and str(k['died']).isdigit() else 0,
                    "modifyTime": insert_date,
                    "tags": "",
                    "insert_date": insert_date}
        # print(province)
        table_name = 'sarl'
        cols, values = zip(*province.items())
        insert_into(table_name, cols, values)

def truncate_db(table_name):
    while True:
        # 连接mysql
        connect = pymysql.connect(MYSQL_HOST, MYSQL_USER, MYSQL_PASSWD, MYSQL_DATA_DB, charset=MYSQL_CHARSET,
                                  port=MYSQL_PORT)
        cursor = connect.cursor()
        try:
            # 创建sql语句
            sql = "truncate {}".format(table_name)
            cursor.execute(sql)
            connect.commit()
            cursor.close()
            connect.close()
            break
        except Exception as e:
            print(e)
            cursor.close()
            connect.close()

def insert_into(table_name, cols, values):
    n=0
    while n<=3:
        # 连接mysql
        connect = pymysql.connect(MYSQL_HOST, MYSQL_USER, MYSQL_PASSWD, MYSQL_DATA_DB, charset=MYSQL_CHARSET,
                                  port=MYSQL_PORT)
        cursor = connect.cursor()
        try:
            sql = "INSERT INTO `{}` ({}) VALUES ({})".format(table_name, ','.join(cols),
                                                             ','.join(['%s'] * len(values)))
            cursor.execute(sql, values)
            connect.commit()
            cursor.close()
            connect.close()
            break
        except Exception as e:
            n+=1
            print(e)
            cursor.close()
            connect.close()

def Timestamp2time(currentTimeStamp):
    time_local = time.localtime(currentTimeStamp)#格式化时间戳为本地时间
    time_YmdHMS = time.strftime("%Y-%m-%d %H:%M:%S",time_local)#自定义时间格式
    # print('currentTimeStamp:', currentTimeStamp)
    # print('time_local:', time_local)
    print('time_YmdHMS:', time_YmdHMS)
    return time_YmdHMS


def run_data_dxy(txt):
    data_dict = re.findall('window\.getListByCountryTypeService1 = (\[.*?\}\])\}catch\(e\)\{\}</script>',txt)
    res = data_dict[0]
    data = json.loads(res)
    truncate_db('sarl')
    total_data = re.findall(
        '''"summary":"","deleted":\w+,"countRemark":"","confirmedCount":(\d+),"suspectedCount":(\d+),"curedCount":(\d+),"deadCount":(\d+),''',
        txt)
    insert_date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
    province = {"provinceShortName": "全国",
                "confirmedCount": total_data[0][0] if total_data[0] else 0,
                "suspectedCount": total_data[0][1] if total_data[0] else 0,
                "curedCount": total_data[0][2] if total_data[0] else 0,
                "deadCount": total_data[0][3] if total_data[0] else 0,
                "modifyTime": insert_date,
                "tags": "",
                "insert_date": insert_date}
    table_name = 'sarl'
    # print(province)
    cols, values = zip(*province.items())
    insert_into(table_name, cols, values)

    for k in data:
        insert_date = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
        province = {"provinceShortName": "",
                    "confirmedCount": "",
                    "suspectedCount": "",
                    "curedCount": "",
                    "deadCount": "",
                    "modifyTime": "",
                    "tags": "",
                    "insert_date": insert_date}
        for x,y in k.items():
            if x in province.keys():
                if x=='modifyTime':
                    y=Timestamp2time(int(y/1000))
                province[x]=y
        # print(province)
        table_name='sarl'
        cols,values = zip(*province.items())
        insert_into(table_name, cols, values)


def run_news(txt):
    data_dict = re.findall('window\.getTimelineService = (\[.*?\}\])\}catch\(e\)\{\}</script>', txt)
    res = data_dict[0]
    data = json.loads(res)
    truncate_db('sarl_news')
    for k in data:
        news = { 'pubDate':'',
                    'pubDateStr':'',
                    'title':'',
                    'summary':'',
                    'infoSource':'',
                    'sourceUrl':'',
                    'provinceId':'',
                    'provinceName':'',
                    'createTime':'',
                    'modifyTime':''}
        for x, y in k.items():
            if x in news.keys() :
                if 'Time' in x or x=='pubDate':
                    y = Timestamp2time(int(y / 1000))
                news[x] = y
        table_name = 'sarl_news'
        cols, values = zip(*news.items())
        # print(cols,values)
        insert_into(table_name, cols, values)



if __name__=='__main__':
    txt_dxy = dxy_sarl()
    run_news(txt_dxy)
    txt_baidu = baidu_sarl()
    run_data_baidu(txt_baidu)








