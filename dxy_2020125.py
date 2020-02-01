# -*- coding: utf-8 -*-

import requests
import re
import time
import re
from lxml import etree
import json
import pymysql
from share import MYSQL_DATA_DB,MYSQL_PORT,MYSQL_USER,MYSQL_PASSWD,MYSQL_CHARSET,MYSQL_HOST
import operator
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
    # try:

    # print(data)
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
    # except Exception as e:
    #
    #     print(e,k)
    #
    # return data





# currentTimeStamp = time.time()#获取当前时间戳

def truncate_db(table_name):
    while True:
        # 连接mysql
        connect = pymysql.connect(MYSQL_HOST, MYSQL_USER, MYSQL_PASSWD, MYSQL_DATA_DB, charset=MYSQL_CHARSET,
                                  port=MYSQL_PORT)
        cursor = connect.cursor()
        try:

            # 创建sql语句
            sql = "truncate {}".format(table_name)
            # print(sql)
            # print(values)
            # 执行sql语句
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

            # 创建sql语句
            sql = "INSERT INTO `{}` ({}) VALUES ({})".format(table_name, ','.join(cols),
                                                             ','.join(['%s'] * len(values)))
            # print(sql)
            # print(values)
            # 执行sql语句
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

        # print(news)
        table_name = 'sarl_news'
        cols, values = zip(*news.items())
        # print(cols,values)
        insert_into(table_name, cols, values)



if __name__=='__main__':
    txt_dxy = dxy_sarl()
    run_news(txt_dxy)
    txt_baidu = baidu_sarl()
    run_data_baidu(txt_baidu)


    # print(total_data)
    data={'page': {'title': '实时更新：新型冠状病毒肺炎疫情地图', 'seo': [], 'hasTongji': True, 'type': 'Window', 'name': '页面', 'id': 0, 'sharePageUrl': 'http://voice.baidu.com/act/newpneumonia/newpneumonia', 'shareDesc': '全国新型冠状病毒肺炎实时地图', 'shareTitle': '实时更新：新型冠状病毒肺炎疫情地图', 'shareImg': 'https://mms-res.cdn.bcebos.com/mms-res/voicefe/captain/images/ecc4e1b0a447b66941edd59b05c2a01a.png?size=96*96'}, 'component': [{'backgroundColor': '#00bac5', 'title': '疫情实时大数据报告', 'mapLastUpdatedTime': '2020.01.31 18:25', 'caseList': [{'confirmed': '1', 'died': '', 'crued': '', 'area': '西藏', 'subList': [{'city': '拉萨', 'confirmed': '1', 'died': '', 'crued': ''}]}, {'crued': '', 'confirmed': '7', 'died': '', 'unconfirmed': '', 'area': '澳门', 'subList': []}, {'confirmed': '8', 'died': '', 'crued': '', 'area': '青海', 'subList': [{'city': '西宁', 'confirmed': '8', 'died': '', 'crued': ''}]}, {'crued': '', 'confirmed': '9', 'died': '', 'unconfirmed': '228', 'area': '台湾', 'subList': []}, {'confirmed': '12', 'died': '', 'crued': '', 'area': '香港', 'subList': []}, {'confirmed': '29', 'died': '', 'crued': '1', 'area': '贵州', 'subList': [{'city': '六盘水', 'confirmed': '8', 'died': '', 'crued': ''}, {'city': '毕节', 'confirmed': '3', 'died': '', 'crued': ''}, {'city': '黔西南州', 'confirmed': '1', 'died': '', 'crued': ''}, {'city': '黔南州', 'confirmed': '4', 'died': '', 'crued': ''}, {'city': '黔东南州', 'confirmed': '2', 'died': '', 'crued': ''}, {'city': '贵阳', 'confirmed': '4', 'died': '', 'crued': '1'}, {'city': '铜仁地区', 'confirmed': '3', 'died': '', 'crued': ''}, {'city': '遵义', 'confirmed': '4', 'died': '', 'crued': ''}]}, {'confirmed': '14', 'died': '', 'crued': '1', 'area': '吉林', 'subList': [{'city': '延边', 'confirmed': '2', 'died': '', 'crued': ''}, {'city': '四平', 'confirmed': '1', 'died': '', 'crued': ''}, {'city': '通化', 'confirmed': '1', 'died': '', 'crued': ''}, {'city': '吉林市', 'confirmed': '3', 'died': '', 'crued': ''}, {'city': '公主岭', 'confirmed': '1', 'died': '', 'crued': ''}, {'city': '松原', 'confirmed': '2', 'died': '', 'crued': ''}, {'city': '长春', 'confirmed': '3', 'died': '', 'crued': '1'}]}, {'confirmed': '17', 'died': '', 'crued': '', 'area': '新疆', 'subList': [{'city': '乌鲁木齐', 'confirmed': '8', 'died': '', 'crued': ''}, {'city': '第七师', 'confirmed': '1', 'died': '', 'crued': ''}, {'city': '第八师', 'confirmed': '1', 'died': '', 'crued': ''}, {'city': '吐鲁番地区', 'confirmed': '1', 'died': '', 'crued': ''}, {'city': '伊犁州', 'confirmed': '5', 'died': '', 'crued': ''}, {'city': '阿克苏地区', 'confirmed': '1', 'died': '', 'crued': ''}]}, {'confirmed': '21', 'died': '', 'crued': '', 'area': '宁夏', 'subList': [{'city': '中卫', 'confirmed': '2', 'died': '', 'crued': ''}, {'city': '吴忠', 'confirmed': '5', 'died': '', 'crued': ''}, {'city': '银川', 'confirmed': '11', 'died': '', 'crued': ''}, {'city': '宁东管委会', 'confirmed': '1', 'died': '', 'crued': ''}, {'city': '固原', 'confirmed': '2', 'died': '', 'crued': ''}]}, {'confirmed': '20', 'died': '', 'crued': '1', 'area': '内蒙古', 'subList': [{'city': '锡林郭勒', 'confirmed': '2', 'died': '', 'crued': ''}, {'city': '包头', 'confirmed': '3', 'died': '', 'crued': ''}, {'city': '呼伦贝尔', 'confirmed': '2', 'died': '', 'crued': ''}, {'city': '呼和浩特', 'confirmed': '2', 'died': '', 'crued': ''}, {'city': '兴安盟', 'confirmed': '1', 'died': '', 'crued': ''}, {'city': '巴彦淖尔', 'confirmed': '2', 'died': '', 'crued': ''}, {'city': '赤峰', 'confirmed': '2', 'died': '', 'crued': ''}, {'city': '通辽', 'confirmed': '1', 'died': '', 'crued': ''}, {'city': '鄂尔多斯', 'confirmed': '3', 'died': '', 'crued': ''}, {'city': '乌兰察布', 'confirmed': '2', 'died': '', 'crued': ''}, {'city': '满洲里', 'confirmed': '', 'died': '', 'crued': '1'}]}, {'crued': '', 'confirmed': '29', 'died': '', 'unconfirmed': '1', 'area': '甘肃', 'subList': [{'city': '平凉', 'crued': '', 'confirmed': '1', 'died': '', 'unconfirmed': ''}, {'city': '金昌', 'crued': '', 'confirmed': '1', 'died': '', 'unconfirmed': ''}, {'city': '天水', 'crued': '', 'confirmed': '2', 'died': '', 'unconfirmed': ''}, {'city': '张掖', 'crued': '', 'confirmed': '2', 'died': '', 'unconfirmed': ''}, {'city': '陇南', 'crued': '', 'confirmed': '3', 'died': '', 'unconfirmed': ''}, {'city': '白银', 'crued': '', 'confirmed': '1', 'died': '', 'unconfirmed': ''}, {'city': '临夏州', 'crued': '', 'confirmed': '2', 'died': '', 'unconfirmed': ''}, {'city': '兰州', 'crued': '', 'confirmed': '15', 'died': '', 'unconfirmed': ''}, {'city': '定西', 'crued': '', 'confirmed': '2', 'died': '', 'unconfirmed': ''}]}, {'confirmed': '32', 'died': '', 'crued': '', 'area': '天津', 'subList': [{'city': '红桥区', 'confirmed': '2', 'died': '', 'crued': ''}, {'city': '和平区', 'confirmed': '3', 'died': '', 'crued': ''}, {'city': '滨海新区', 'confirmed': '2', 'died': '', 'crued': ''}, {'city': '西青区', 'confirmed': '2', 'died': '', 'crued': ''}, {'city': '南开区', 'confirmed': '2', 'died': '', 'crued': ''}, {'city': '河东区', 'confirmed': '5', 'died': '', 'crued': ''}, {'city': '河北区', 'confirmed': '8', 'died': '', 'crued': ''}, {'city': '河西区', 'confirmed': '3', 'died': '', 'crued': ''}, {'city': '外地来津人员', 'confirmed': '4', 'died': '', 'crued': ''}, {'city': '宁河区', 'confirmed': '1', 'died': '', 'crued': ''}]}, {'confirmed': '39', 'died': '', 'crued': '1', 'area': '山西', 'subList': [{'city': '朔州', 'confirmed': '3', 'died': '', 'crued': ''}, {'city': '晋中', 'confirmed': '9', 'died': '', 'crued': ''}, {'city': '运城', 'confirmed': '8', 'died': '', 'crued': ''}, {'city': '阳泉', 'confirmed': '1', 'died': '', 'crued': ''}, {'city': '吕梁', 'confirmed': '5', 'died': '', 'crued': ''}, {'city': '大同', 'confirmed': '5', 'died': '', 'crued': ''}, {'city': '长治', 'confirmed': '3', 'died': '', 'crued': ''}, {'city': '临汾', 'confirmed': '1', 'died': '', 'crued': ''}, {'city': '太原', 'confirmed': '4', 'died': '', 'crued': '1'}]}, {'confirmed': '48', 'died': '', 'crued': '1', 'area': '辽宁', 'subList': [{'city': '朝阳', 'confirmed': '5', 'died': '', 'crued': ''}, {'city': '铁岭', 'confirmed': '3', 'died': '', 'crued': ''}, {'city': '葫芦岛', 'confirmed': '4', 'died': '', 'crued': ''}, {'city': '锦州', 'confirmed': '5', 'died': '', 'crued': ''}, {'city': '大连', 'confirmed': '7', 'died': '', 'crued': '1'}, {'city': '营口', 'confirmed': '1', 'died': '', 'crued': ''}, {'city': '丹东', 'confirmed': '5', 'died': '', 'crued': ''}, {'city': '沈阳', 'confirmed': '10', 'died': '', 'crued': ''}, {'city': '辽阳', 'confirmed': '1', 'died': '', 'crued': ''}, {'city': '盘锦', 'confirmed': '4', 'died': '', 'crued': ''}, {'city': '本溪', 'confirmed': '3', 'died': '', 'crued': ''}]}, {'confirmed': '59', 'died': '2', 'crued': '', 'area': '黑龙江', 'subList': [{'city': '鹤岗', 'confirmed': '1', 'died': '', 'crued': ''}, {'city': '七台河', 'confirmed': '3', 'died': '', 'crued': ''}, {'city': '大兴安岭地区', 'confirmed': '2', 'died': '', 'crued': ''}, {'city': '佳木斯', 'confirmed': '8', 'died': '', 'crued': ''}, {'city': '牡丹江', 'confirmed': '2', 'died': '', 'crued': ''}, {'city': '鸡西', 'confirmed': '2', 'died': '', 'crued': ''}, {'city': '绥化', 'confirmed': '12', 'died': '2', 'crued': ''}, {'city': '齐齐哈尔', 'confirmed': '3', 'died': '', 'crued': ''}, {'city': '双鸭山', 'confirmed': '1', 'died': '', 'crued': ''}, {'city': '哈尔滨', 'confirmed': '18', 'died': '', 'crued': ''}, {'city': '大庆', 'confirmed': '7', 'died': '', 'crued': ''}]}, {'confirmed': '52', 'died': '1', 'crued': '1', 'area': '海南', 'subList': [{'city': '陵水黎族自治县', 'confirmed': '3', 'died': '', 'crued': ''}, {'city': '琼中黎族苗族自治县', 'confirmed': '1', 'died': '', 'crued': ''}, {'city': '琼海', 'confirmed': '4', 'died': '', 'crued': ''}, {'city': '儋州', 'confirmed': '5', 'died': '', 'crued': ''}, {'city': '万宁', 'confirmed': '8', 'died': '', 'crued': ''}, {'city': '东方', 'confirmed': '1', 'died': '', 'crued': ''}, {'city': '临高', 'confirmed': '2', 'died': '', 'crued': ''}, {'city': '海口', 'confirmed': '9', 'died': '', 'crued': ''}, {'city': '澄迈', 'confirmed': '2', 'died': '1', 'crued': ''}, {'city': '三亚', 'confirmed': '14', 'died': '', 'crued': '1'}, {'city': '昌江', 'confirmed': '1', 'died': '', 'crued': ''}, {'city': '定安', 'confirmed': '1', 'died': '', 'crued': ''}, {'city': '乐东', 'confirmed': '1', 'died': '', 'crued': ''}, {'city': '待确认', 'confirmed': '1', 'died': '', 'crued': ''}]}, {'confirmed': '82', 'died': '1', 'crued': '', 'area': '河北', 'subList': [{'city': '张家口', 'confirmed': '6', 'died': '', 'crued': ''}, {'city': '保定', 'confirmed': '11', 'died': '', 'crued': ''}, {'city': '邢台', 'confirmed': '7', 'died': '', 'crued': ''}, {'city': '沧州', 'confirmed': '18', 'died': '1', 'crued': ''}, {'city': '石家庄', 'confirmed': '11', 'died': '', 'crued': ''}, {'city': '承德', 'confirmed': '2', 'died': '', 'crued': ''}, {'city': '廊坊', 'confirmed': '9', 'died': '', 'crued': ''}, {'city': '邯郸', 'confirmed': '7', 'died': '', 'crued': ''}, {'city': '衡水', 'confirmed': '4', 'died': '', 'crued': ''}, {'city': '唐山', 'confirmed': '7', 'died': '', 'crued': ''}]}, {'confirmed': '87', 'died': '', 'crued': '', 'area': '陕西', 'subList': [{'city': '榆林', 'confirmed': '1', 'died': '', 'crued': ''}, {'city': '西安', 'confirmed': '32', 'died': '', 'crued': ''}, {'city': '咸阳', 'confirmed': '6', 'died': '', 'crued': ''}, {'city': '商洛', 'confirmed': '2', 'died': '', 'crued': ''}, {'city': '安康', 'confirmed': '13', 'died': '', 'crued': ''}, {'city': '延安', 'confirmed': '7', 'died': '', 'crued': ''}, {'city': '韩城', 'confirmed': '1', 'died': '', 'crued': ''}, {'city': '汉中', 'confirmed': '11', 'died': '', 'crued': ''}, {'city': '宝鸡', 'confirmed': '4', 'died': '', 'crued': ''}, {'city': '渭南', 'confirmed': '5', 'died': '', 'crued': ''}, {'city': '铜川', 'confirmed': '5', 'died': '', 'crued': ''}]}, {'confirmed': '83', 'died': '', 'crued': '2', 'area': '云南', 'subList': [{'city': '丽江', 'confirmed': '6', 'died': '', 'crued': ''}, {'city': '红河州', 'confirmed': '4', 'died': '', 'crued': '1'}, {'city': '大理州', 'confirmed': '6', 'died': '', 'crued': ''}, {'city': '保山', 'confirmed': '6', 'died': '', 'crued': ''}, {'city': '昭通', 'confirmed': '4', 'died': '', 'crued': ''}, {'city': '德宏州', 'confirmed': '3', 'died': '', 'crued': ''}, {'city': '曲靖', 'confirmed': '5', 'died': '', 'crued': ''}, {'city': '西双版纳傣族自治州', 'confirmed': '12', 'died': '', 'crued': ''}, {'city': '玉溪', 'confirmed': '6', 'died': '', 'crued': ''}, {'city': '普洱', 'confirmed': '4', 'died': '', 'crued': ''}, {'city': '昆明', 'confirmed': '24', 'died': '', 'crued': ''}, {'city': '待确认', 'confirmed': '3', 'died': '', 'crued': '1'}]}, {'confirmed': '87', 'died': '', 'crued': '2', 'area': '广西', 'subList': [{'city': '桂林', 'confirmed': '18', 'died': '', 'crued': ''}, {'city': '河池', 'confirmed': '6', 'died': '', 'crued': ''}, {'city': '南宁', 'confirmed': '16', 'died': '', 'crued': ''}, {'city': '防城港', 'confirmed': '7', 'died': '', 'crued': '1'}, {'city': '贺州', 'confirmed': '1', 'died': '', 'crued': ''}, {'city': '柳州', 'confirmed': '11', 'died': '', 'crued': ''}, {'city': '玉林', 'confirmed': '4', 'died': '', 'crued': ''}, {'city': '北海', 'confirmed': '17', 'died': '', 'crued': ''}, {'city': '钦州', 'confirmed': '1', 'died': '', 'crued': ''}, {'city': '梧州', 'confirmed': '4', 'died': '', 'crued': '1'}, {'city': '百色', 'confirmed': '2', 'died': '', 'crued': ''}]}, {'confirmed': '120', 'died': '', 'crued': '', 'area': '福建', 'subList': [{'city': '厦门', 'confirmed': '13', 'died': '', 'crued': ''}, {'city': '南平', 'confirmed': '3', 'died': '', 'crued': ''}, {'city': '莆田', 'confirmed': '22', 'died': '', 'crued': ''}, {'city': '泉州', 'confirmed': '22', 'died': '', 'crued': ''}, {'city': '漳州', 'confirmed': '8', 'died': '', 'crued': ''}, {'city': '三明', 'confirmed': '10', 'died': '', 'crued': ''}, {'city': '宁德', 'confirmed': '9', 'died': '', 'crued': ''}, {'city': '龙岩', 'confirmed': '1', 'died': '', 'crued': ''}, {'city': '福州', 'confirmed': '32', 'died': '', 'crued': ''}]}, {'confirmed': '135', 'died': '1', 'crued': '9', 'area': '上海', 'subList': [{'city': '嘉定区', 'confirmed': '2', 'died': '', 'crued': ''}, {'city': '外地来沪人员', 'confirmed': '62', 'died': '', 'crued': ''}, {'city': '松江区', 'confirmed': '3', 'died': '', 'crued': ''}, {'city': '黄浦区', 'confirmed': '4', 'died': '', 'crued': ''}, {'city': '长宁区', 'confirmed': '6', 'died': '', 'crued': ''}, {'city': '待确认', 'confirmed': '', 'died': '1', 'crued': '9'}, {'city': '青浦区', 'confirmed': '2', 'died': '', 'crued': ''}, {'city': '闵行区', 'confirmed': '5', 'died': '', 'crued': ''}, {'city': '静安区', 'confirmed': '8', 'died': '', 'crued': ''}, {'city': '虹口区', 'confirmed': '4', 'died': '', 'crued': ''}, {'city': '宝山区', 'confirmed': '2', 'died': '', 'crued': ''}, {'city': '浦东新区', 'confirmed': '25', 'died': '', 'crued': ''}, {'city': '杨浦区', 'confirmed': '1', 'died': '', 'crued': ''}, {'city': '徐汇区', 'confirmed': '5', 'died': '', 'crued': ''}, {'city': '奉贤区', 'confirmed': '5', 'died': '', 'crued': ''}, {'city': '金山区', 'confirmed': '1', 'died': '', 'crued': ''}]}, {'confirmed': '139', 'died': '1', 'crued': '10', 'area': '北京', 'subList': [{'city': '东城区', 'confirmed': '3', 'died': '', 'crued': ''}, {'city': '海淀区', 'confirmed': '27', 'died': '', 'crued': ''}, {'city': '大兴区', 'confirmed': '17', 'died': '', 'crued': '2'}, {'city': '朝阳区', 'confirmed': '24', 'died': '', 'crued': '1'}, {'city': '丰台区', 'confirmed': '11', 'died': '', 'crued': ''}, {'city': '门头沟区', 'confirmed': '1', 'died': '', 'crued': ''}, {'city': '通州区', 'confirmed': '12', 'died': '', 'crued': ''}, {'city': '顺义区', 'confirmed': '2', 'died': '', 'crued': ''}, {'city': '石景山区', 'confirmed': '2', 'died': '', 'crued': ''}, {'city': '西城区', 'confirmed': '16', 'died': '', 'crued': ''}, {'city': '怀柔区', 'confirmed': '1', 'died': '', 'crued': ''}, {'city': '昌平区', 'confirmed': '12', 'died': '', 'crued': ''}, {'city': '外地来京人员', 'confirmed': '11', 'died': '', 'crued': '2'}]}, {'confirmed': '168', 'died': '', 'crued': '5', 'area': '江苏', 'subList': [{'city': '徐州', 'confirmed': '20', 'died': '', 'crued': ''}, {'city': '扬州', 'confirmed': '8', 'died': '', 'crued': ''}, {'city': '宿迁', 'confirmed': '7', 'died': '', 'crued': ''}, {'city': '镇江', 'confirmed': '2', 'died': '', 'crued': ''}, {'city': '连云港', 'confirmed': '9', 'died': '', 'crued': '1'}, {'city': '无锡', 'confirmed': '12', 'died': '', 'crued': ''}, {'city': '泰州', 'confirmed': '12', 'died': '', 'crued': ''}, {'city': '盐城', 'confirmed': '8', 'died': '', 'crued': ''}, {'city': '淮安', 'confirmed': '10', 'died': '', 'crued': ''}, {'city': '南通', 'confirmed': '10', 'died': '', 'crued': ''}, {'city': '南京', 'confirmed': '25', 'died': '', 'crued': '2'}, {'city': '常州', 'confirmed': '13', 'died': '', 'crued': ''}, {'city': '苏州', 'confirmed': '32', 'died': '', 'crued': '2'}]}, {'confirmed': '177', 'died': '1', 'crued': '1', 'area': '四川', 'subList': [{'city': '遂宁', 'confirmed': '5', 'died': '', 'crued': ''}, {'city': '达州', 'confirmed': '8', 'died': '', 'crued': ''}, {'city': '内江', 'confirmed': '6', 'died': '', 'crued': ''}, {'city': '广安', 'confirmed': '13', 'died': '', 'crued': ''}, {'city': '宜宾', 'confirmed': '7', 'died': '', 'crued': ''}, {'city': '凉山州', 'confirmed': '3', 'died': '', 'crued': ''}, {'city': '乐山', 'confirmed': '2', 'died': '', 'crued': ''}, {'city': '眉山', 'confirmed': '2', 'died': '', 'crued': ''}, {'city': '德阳', 'confirmed': '7', 'died': '', 'crued': ''}, {'city': '巴中', 'confirmed': '5', 'died': '', 'crued': ''}, {'city': '成都', 'confirmed': '69', 'died': '1', 'crued': '1'}, {'city': '南充', 'confirmed': '11', 'died': '', 'crued': ''}, {'city': '泸州', 'confirmed': '5', 'died': '', 'crued': ''}, {'city': '绵阳', 'confirmed': '11', 'died': '', 'crued': ''}, {'city': '甘孜州', 'confirmed': '5', 'died': '', 'crued': ''}, {'city': '广元', 'confirmed': '2', 'died': '', 'crued': ''}, {'city': '资阳', 'confirmed': '2', 'died': '', 'crued': ''}, {'city': '自贡', 'confirmed': '9', 'died': '', 'crued': ''}, {'city': '雅安', 'confirmed': '3', 'died': '', 'crued': ''}, {'city': '攀枝花', 'confirmed': '1', 'died': '', 'crued': ''}, {'city': '阿坝州', 'confirmed': '1', 'died': '', 'crued': ''}]}, {'confirmed': '184', 'died': '', 'crued': '2', 'area': '山东', 'subList': [{'city': '威海', 'confirmed': '19', 'died': '', 'crued': ''}, {'city': '泰安', 'confirmed': '4', 'died': '', 'crued': ''}, {'city': '济南', 'confirmed': '16', 'died': '', 'crued': ''}, {'city': '枣庄', 'confirmed': '9', 'died': '', 'crued': ''}, {'city': '济宁', 'confirmed': '8', 'died': '', 'crued': ''}, {'city': '临沂', 'confirmed': '23', 'died': '', 'crued': ''}, {'city': '青岛', 'confirmed': '21', 'died': '', 'crued': '1'}, {'city': '日照', 'confirmed': '9', 'died': '', 'crued': ''}, {'city': '菏泽', 'confirmed': '8', 'died': '', 'crued': ''}, {'city': '聊城', 'confirmed': '7', 'died': '', 'crued': ''}, {'city': '滨州', 'confirmed': '9', 'died': '', 'crued': ''}, {'city': '潍坊', 'confirmed': '8', 'died': '', 'crued': ''}, {'city': '德州', 'confirmed': '16', 'died': '', 'crued': '1'}, {'city': '烟台', 'confirmed': '18', 'died': '', 'crued': ''}, {'city': '淄博', 'confirmed': '9', 'died': '', 'crued': ''}]}, {'confirmed': '240', 'died': '', 'crued': '7', 'area': '江西', 'subList': [{'city': '吉安', 'confirmed': '8', 'died': '', 'crued': '1'}, {'city': '上饶', 'confirmed': '12', 'died': '', 'crued': '1'}, {'city': '九江', 'confirmed': '42', 'died': '', 'crued': ''}, {'city': '新余', 'confirmed': '28', 'died': '', 'crued': '2'}, {'city': '抚州', 'confirmed': '15', 'died': '', 'crued': ''}, {'city': '鹰潭', 'confirmed': '4', 'died': '', 'crued': ''}, {'city': '宜春', 'confirmed': '26', 'died': '', 'crued': ''}, {'city': '景德镇', 'confirmed': '3', 'died': '', 'crued': '1'}, {'city': '萍乡', 'confirmed': '8', 'died': '', 'crued': '1'}, {'city': '赣州', 'confirmed': '27', 'died': '', 'crued': ''}, {'city': '南昌', 'confirmed': '67', 'died': '', 'crued': '1'}]}, {'confirmed': '211', 'died': '', 'crued': '1', 'area': '重庆', 'subList': [{'city': '奉节县 ', 'confirmed': '5', 'died': '', 'crued': ''}, {'city': '武隆区', 'confirmed': '1', 'died': '', 'crued': ''}, {'city': '永川区', 'confirmed': '3', 'died': '', 'crued': ''}, {'city': '两江新区', 'confirmed': '9', 'died': '', 'crued': ''}, {'city': '渝北区', 'confirmed': '10', 'died': '', 'crued': ''}, {'city': '开州区', 'confirmed': '16', 'died': '', 'crued': ''}, {'city': '丰都县', 'confirmed': '3', 'died': '', 'crued': ''}, {'city': '巫山县', 'confirmed': '6', 'died': '', 'crued': '1'}, {'city': '大足区', 'confirmed': '4', 'died': '', 'crued': ''}, {'city': '忠县', 'confirmed': '12', 'died': '', 'crued': ''}, {'city': '云阳县', 'confirmed': '15', 'died': '', 'crued': ''}, {'city': '璧山区', 'confirmed': '6', 'died': '', 'crued': ''}, {'city': '九龙坡区', 'confirmed': '8', 'died': '', 'crued': ''}, {'city': '潼南区', 'confirmed': '2', 'died': '', 'crued': ''}, {'city': '大渡口区', 'confirmed': '6', 'died': '', 'crued': ''}, {'city': '梁平区', 'confirmed': '2', 'died': '', 'crued': ''}, {'city': '秀山县', 'confirmed': '1', 'died': '', 'crued': ''}, {'city': '万州区', 'confirmed': '29', 'died': '', 'crued': ''}, {'city': '南岸区', 'confirmed': '3', 'died': '', 'crued': ''}, {'city': '石柱县', 'confirmed': '8', 'died': '', 'crued': ''}, {'city': '涪陵区', 'confirmed': '1', 'died': '', 'crued': ''}, {'city': '江北区', 'confirmed': '8', 'died': '', 'crued': ''}, {'city': '綦江区', 'confirmed': '4', 'died': '', 'crued': ''}, {'city': '巫溪县', 'confirmed': '10', 'died': '', 'crued': ''}, {'city': '长寿区', 'confirmed': '9', 'died': '', 'crued': ''}, {'city': '城口县', 'confirmed': '1', 'died': '', 'crued': ''}, {'city': '合川区', 'confirmed': '6', 'died': '', 'crued': ''}, {'city': '垫江县', 'confirmed': '8', 'died': '', 'crued': ''}, {'city': '江津区 ', 'confirmed': '3', 'died': '', 'crued': ''}, {'city': '黔江区', 'confirmed': '2', 'died': '', 'crued': ''}, {'city': '渝中区', 'confirmed': '6', 'died': '', 'crued': ''}, {'city': '巴南区', 'confirmed': '1', 'died': '', 'crued': ''}, {'city': '铜梁区', 'confirmed': '2', 'died': '', 'crued': ''}, {'city': '荣昌区', 'confirmed': '1', 'died': '', 'crued': ''}]}, {'confirmed': '237', 'died': '', 'crued': '3', 'area': '安徽', 'subList': [{'city': '安庆', 'confirmed': '18', 'died': '', 'crued': ''}, {'city': '芜湖', 'confirmed': '14', 'died': '', 'crued': ''}, {'city': '亳州', 'confirmed': '20', 'died': '', 'crued': '1'}, {'city': '黄山', 'confirmed': '9', 'died': '', 'crued': ''}, {'city': '淮北', 'confirmed': '2', 'died': '', 'crued': ''}, {'city': '蚌埠', 'confirmed': '15', 'died': '', 'crued': ''}, {'city': '马鞍山', 'confirmed': '14', 'died': '', 'crued': ''}, {'city': '铜陵', 'confirmed': '14', 'died': '', 'crued': ''}, {'city': '池州', 'confirmed': '4', 'died': '', 'crued': ''}, {'city': '宿州', 'confirmed': '10', 'died': '', 'crued': ''}, {'city': '合肥', 'confirmed': '50', 'died': '', 'crued': '1'}, {'city': '宣城', 'confirmed': '4', 'died': '', 'crued': ''}, {'city': '滁州', 'confirmed': '4', 'died': '', 'crued': ''}, {'city': '阜阳', 'confirmed': '38', 'died': '', 'crued': ''}, {'city': '淮南', 'confirmed': '6', 'died': '', 'crued': ''}, {'city': '六安', 'confirmed': '9', 'died': '', 'crued': '1'}, {'city': '宿松', 'confirmed': '6', 'died': '', 'crued': ''}]}, {'confirmed': '332', 'died': '', 'crued': '2', 'area': '湖南', 'subList': [{'city': '衡阳', 'confirmed': '25', 'died': '', 'crued': ''}, {'city': '娄底', 'confirmed': '20', 'died': '', 'crued': ''}, {'city': '湘潭', 'confirmed': '10', 'died': '', 'crued': ''}, {'city': '永州', 'confirmed': '16', 'died': '', 'crued': ''}, {'city': '常德', 'confirmed': '37', 'died': '', 'crued': ''}, {'city': '张家界', 'confirmed': '1', 'died': '', 'crued': ''}, {'city': '岳阳', 'confirmed': '37', 'died': '', 'crued': ''}, {'city': '株洲', 'confirmed': '19', 'died': '', 'crued': ''}, {'city': '长沙', 'confirmed': '68', 'died': '', 'crued': '1'}, {'city': '邵阳', 'confirmed': '36', 'died': '', 'crued': ''}, {'city': '湘西州', 'confirmed': '5', 'died': '', 'crued': ''}, {'city': '郴州', 'confirmed': '12', 'died': '', 'crued': '1'}, {'city': '怀化', 'confirmed': '26', 'died': '', 'crued': ''}, {'city': '益阳', 'confirmed': '20', 'died': '', 'crued': ''}]}, {'confirmed': '352', 'died': '2', 'crued': '3', 'area': '河南', 'subList': [{'city': '安阳', 'confirmed': '20', 'died': '', 'crued': ''}, {'city': '信阳', 'confirmed': '49', 'died': '', 'crued': ''}, {'city': '周口', 'confirmed': '36', 'died': '', 'crued': ''}, {'city': '开封', 'confirmed': '6', 'died': '', 'crued': ''}, {'city': '许昌', 'confirmed': '8', 'died': '', 'crued': ''}, {'city': '濮阳', 'confirmed': '3', 'died': '', 'crued': ''}, {'city': '漯河', 'confirmed': '13', 'died': '', 'crued': ''}, {'city': '郑州', 'confirmed': '50', 'died': '', 'crued': '2'}, {'city': '三门峡', 'confirmed': '6', 'died': '', 'crued': ''}, {'city': '驻马店', 'confirmed': '30', 'died': '', 'crued': ''}, {'city': '长垣', 'confirmed': '2', 'died': '', 'crued': ''}, {'city': '南阳', 'confirmed': '61', 'died': '2', 'crued': ''}, {'city': '鹤壁', 'confirmed': '6', 'died': '', 'crued': ''}, {'city': '商丘', 'confirmed': '27', 'died': '', 'crued': ''}, {'city': '洛阳', 'confirmed': '3', 'died': '', 'crued': ''}, {'city': '新乡', 'confirmed': '15', 'died': '', 'crued': ''}, {'city': '滑县', 'confirmed': '1', 'died': '', 'crued': ''}, {'city': '焦作', 'confirmed': '2', 'died': '', 'crued': ''}, {'city': '平顶山', 'confirmed': '10', 'died': '', 'crued': ''}, {'city': '永城', 'confirmed': '4', 'died': '', 'crued': ''}, {'city': '待确认', 'confirmed': '', 'died': '', 'crued': '1'}]}, {'confirmed': '436', 'died': '', 'crued': '14', 'area': '广东', 'subList': [{'city': '肇庆', 'confirmed': '6', 'died': '', 'crued': '1'}, {'city': '珠海', 'confirmed': '34', 'died': '', 'crued': '1'}, {'city': '河源', 'confirmed': '1', 'died': '', 'crued': ''}, {'city': '佛山', 'confirmed': '33', 'died': '', 'crued': '1'}, {'city': '清远', 'confirmed': '6', 'died': '', 'crued': '1'}, {'city': '汕尾', 'confirmed': '3', 'died': '', 'crued': ''}, {'city': '茂名', 'confirmed': '3', 'died': '', 'crued': ''}, {'city': '阳江', 'confirmed': '10', 'died': '', 'crued': ''}, {'city': '湛江', 'confirmed': '11', 'died': '', 'crued': '1'}, {'city': '中山', 'confirmed': '18', 'died': '', 'crued': ''}, {'city': '惠州', 'confirmed': '18', 'died': '', 'crued': '1'}, {'city': '揭阳', 'confirmed': '6', 'died': '', 'crued': ''}, {'city': '梅州', 'confirmed': '5', 'died': '', 'crued': ''}, {'city': '深圳', 'confirmed': '134', 'died': '', 'crued': '4'}, {'city': '汕头', 'confirmed': '12', 'died': '', 'crued': '1'}, {'city': '江门', 'confirmed': '2', 'died': '', 'crued': ''}, {'city': '韶关', 'confirmed': '4', 'died': '', 'crued': ''}, {'city': '东莞', 'confirmed': '16', 'died': '', 'crued': ''}, {'city': '广州', 'confirmed': '112', 'died': '', 'crued': '3'}]}, {'confirmed': '537', 'died': '', 'crued': '12', 'area': '浙江', 'subList': [{'city': '台州', 'confirmed': '81', 'died': '', 'crued': '1'}, {'city': '嘉兴', 'confirmed': '16', 'died': '', 'crued': ''}, {'city': '湖州', 'confirmed': '6', 'died': '', 'crued': ''}, {'city': '舟山', 'confirmed': '7', 'died': '', 'crued': '1'}, {'city': '绍兴', 'confirmed': '23', 'died': '', 'crued': ''}, {'city': '宁波', 'confirmed': '46', 'died': '', 'crued': ''}, {'city': '杭州', 'confirmed': '85', 'died': '', 'crued': ''}, {'city': '金华', 'confirmed': '27', 'died': '', 'crued': '2'}, {'city': '丽水', 'confirmed': '7', 'died': '', 'crued': '1'}, {'city': '温州', 'confirmed': '227', 'died': '', 'crued': '7'}, {'city': '衢州', 'confirmed': '12', 'died': '', 'crued': ''}]}, {'confirmed': '5806', 'died': '204', 'crued': '117', 'area': '湖北', 'subList': [{'city': '仙桃', 'confirmed': '90', 'died': '1', 'crued': ''}, {'city': '天门', 'confirmed': '67', 'died': '6', 'crued': ''}, {'city': '随州', 'confirmed': '228', 'died': '', 'crued': ''}, {'city': '咸宁', 'confirmed': '166', 'died': '', 'crued': '1'}, {'city': '十堰', 'confirmed': '150', 'died': '', 'crued': ''}, {'city': '恩施', 'confirmed': '75', 'died': '', 'crued': ''}, {'city': '待确认', 'confirmed': '', 'died': '', 'crued': '116'}, {'city': '襄阳', 'confirmed': '286', 'died': '', 'crued': ''}, {'city': '荆州', 'confirmed': '221', 'died': '3', 'crued': ''}, {'city': '神农架地区', 'confirmed': '7', 'died': '', 'crued': ''}, {'city': '宜昌', 'confirmed': '167', 'died': '1', 'crued': ''}, {'city': '潜江', 'confirmed': '12', 'died': '1', 'crued': ''}, {'city': '武汉', 'confirmed': '2639', 'died': '159', 'crued': ''}, {'city': '黄冈', 'confirmed': '573', 'died': '12', 'crued': ''}, {'city': '孝感', 'confirmed': '541', 'died': '9', 'crued': ''}, {'city': '黄石', 'confirmed': '168', 'died': '1', 'crued': ''}, {'city': '荆门', 'confirmed': '227', 'died': '5', 'crued': ''}, {'city': '鄂州', 'confirmed': '189', 'died': '6', 'crued': ''}]}], 'caseOutsideList': [{'confirmed': '2', 'died': '', 'crued': '', 'area': '英国', 'subList': []}, {'confirmed': '2', 'died': '', 'crued': '', 'area': '意大利', 'subList': []}, {'crued': '', 'confirmed': '1', 'died': '', 'unconfirmed': '', 'area': '印度', 'subList': []}, {'crued': '', 'confirmed': '1', 'died': '', 'unconfirmed': '', 'area': '菲律宾', 'subList': []}, {'crued': '', 'confirmed': '1', 'died': '', 'unconfirmed': '', 'area': '安哥拉', 'subList': []}, {'crued': '', 'confirmed': '1', 'died': '', 'unconfirmed': '', 'area': '芬兰', 'subList': []}, {'confirmed': '4', 'died': '', 'crued': '', 'area': '阿联酋', 'subList': []}, {'crued': '', 'confirmed': '1', 'died': '', 'unconfirmed': '', 'area': '斯里兰卡', 'subList': []}, {'crued': '', 'confirmed': '1', 'died': '', 'unconfirmed': '', 'area': '柬埔寨', 'subList': []}, {'crued': '', 'confirmed': '1', 'died': '', 'unconfirmed': '', 'area': '尼泊尔', 'subList': []}, {'crued': '', 'confirmed': '3', 'died': '', 'unconfirmed': '', 'area': '加拿大', 'subList': []}, {'confirmed': '5', 'died': '', 'crued': '', 'area': '德国', 'subList': []}, {'crued': '', 'confirmed': '5', 'died': '', 'unconfirmed': '', 'area': '越南', 'subList': []}, {'confirmed': '6', 'died': '', 'crued': '', 'area': '法国', 'subList': []}, {'confirmed': '6', 'died': '', 'crued': '', 'area': '美国', 'subList': []}, {'confirmed': '11', 'died': '', 'crued': '', 'area': '韩国', 'subList': []}, {'confirmed': '9', 'died': '', 'crued': '2', 'area': '澳大利亚', 'subList': []}, {'crued': '', 'confirmed': '8', 'died': '', 'unconfirmed': '', 'area': '马来西亚', 'subList': []}, {'confirmed': '15', 'died': '', 'crued': '1', 'area': '日本', 'subList': []}, {'crued': '', 'confirmed': '13', 'died': '', 'unconfirmed': '92', 'area': '新加坡', 'subList': []}, {'confirmed': '19', 'died': '', 'crued': '7', 'area': '泰国', 'subList': []}], 'dataSource': '数据来自官方通报 全国与各省通报数据可能存在差异', 'hotwords': [{'type': '2', 'query': '新型肺炎实时动态', 'degree': '14078500', 'url': 'https://m.baidu.com/s?word=新型肺炎实时动态&sa=osari_hotword'}, {'type': '1', 'query': '湖北企业复工不早于2.13', 'degree': '2759575', 'url': 'https://m.baidu.com/s?word=湖北企业复工不早于2.13&sa=osari_hotword'}, {'type': '1', 'query': '钟南山远程会诊危重症患者', 'url': 'https://m.baidu.com/s?word=钟南山远程会诊危重症患者&sa=osari_hotword', 'degree': '2600350'}, {'type': '1', 'query': '病毒在毛质衣物上存活时间更短', 'url': 'https://m.baidu.com/s?word=病毒在毛质衣物上存活时间更短&sa=osari_hotword', 'degree': '2408700'}, {'type': '1', 'url': 'https://m.baidu.com/s?word=疫情拐点将出现&sa=osari_hotword', 'query': '疫情拐点将出现', 'degree': '2030900'}, {'type': '0', 'query': '湖北省长向医护人员鞠躬', 'degree': '562475', 'url': 'https://m.baidu.com/s?word=湖北省长向医护人员鞠躬&sa=osari_hotword'}, {'type': '0', 'query': '武汉伢 我的城市生病了', 'url': 'https://m.baidu.com/s?word=%e6%ad%a6%e6%b1%89%e4%bc%a2+%e6%88%91%e7%9a%84%e5%9f%8e%e5%b8%82%e7%94%9f%e7%97%85%e4%ba%86&sa=ovirus_rs_7', 'degree': '400500'}, {'type': '0', 'query': '顺丰回应截获口罩', 'url': 'https://m.baidu.com/s?word=顺丰回应截获口罩&sa=osari_hotword', 'degree': '57100'}], 'queryImg': 'https://mms-res.cdn.bcebos.com/mms-res/voicefe/captain/images/8ae57cc26ce169fb7e5f1552d401a77b.png?size=895*142', 'query': '上百度APP搜索 新型冠状病毒肺炎', 'queryLink': 'https://m.baidu.com/s?word=%E6%96%B0%E5%9E%8B%E5%86%A0%E7%8A%B6%E7%97%85%E6%AF%92%E8%82%BA%E7%82%8E&sa=ovirus_searchbox', 'type': 'Virus', 'id': '3f2cgxz', 'name': '肺炎2020-3f2cgxz', 'version': '1.1.28', 'children': [], 'top': 'NaN', 'left': 'NaN', 'summaryDataIn': {'confirmed': '9810', 'died': '213', 'cured': '196', 'unconfirmed': '15238'}, 'summaryDataOut': {'confirmed': '115', 'died': '0', 'cured': '10'}, 'externalButtons': [{'text': '紧急寻人', 'type': '0', 'url': 'https://u1qa5f.smartapps.cn/pages/epidemic/index'}, {'text': '全国发热门诊', 'type': '0', 'url': 'https://ugc.map.baidu.com/static/specialmap/index.html?spId=39&t=20200125'}, {'text': '肺炎权威解读', 'url': 'https://mr.baidu.com/z5z4qmy?f=cp&u=7b3f6c6d4360465e'}, {'text': '免费问医生', 'url': 'https://expert.baidu.com/med/template/#/pages/wz/antiepidemicpage/index?pd=med&openapi=1&from_sf=1&resource_id=5216&vn=med&atn=antiepidemicpage&sf_ref=search_feiyanditu_antiepidemic&lid=14901404375794124016&referlid=14901404375794124016'}], 'share': {'title': '实时更新：新型冠状病毒肺炎疫情地图', 'content': '全国新型冠状病毒肺炎实时地图', 'url': 'http://voice.baidu.com/act/newpneumonia/newpneumonia', 'type': 'url', 'icon': 'https://b.bdstatic.com/searchbox/image/cmsuploader/20161214/1481696369354077.png'}, 'hotwordsDuros': '疫情地图$2|武汉疫情$2|武汉新闻$1|武汉肺炎|新型冠状病毒|冠状病毒|武汉封城|蝙蝠|急诊科医生', 'subtitle': '新型冠状病毒肺炎', 'knowledges': [{'query': '新型肺炎自查手册', 'type': '0', 'degree': '3420900', 'url': 'https://m.baidu.com/s?word=新型肺炎自查手册&sa=osari_fangyi'}, {'query': '抗生素对病毒有用吗', 'type': '0', 'url': 'https://m.baidu.com/s?word=抗生素对病毒有用吗&sa=osari_fangyi', 'degree': '233200'}, {'query': '84消毒液对人体有害吗', 'type': '0', 'url': 'https://m.baidu.com/s?word=84消毒液对人体有害吗&sa=osari_fangyi', 'degree': '157375'}, {'query': '冠状病毒初期症状', 'type': '0', 'url': 'https://m.baidu.com/s?word=冠状病毒初期症状&sa=osari_fangyi', 'degree': '58775'}, {'query': '戴口罩眼镜不起雾技巧', 'type': '0', 'url': 'https://m.baidu.com/s?word=戴口罩眼镜不起雾技巧&sa=osari_fangyi', 'degree': '50533'}, {'query': '消毒灯关了多久能进屋', 'type': '0', 'url': 'https://m.baidu.com/s?word=消毒灯关了多久能进屋&sa=osari_fangyi', 'degree': '25050'}, {'query': '酒精退烧的正确方法', 'type': '0', 'url': 'https://m.baidu.com/s?word=酒精退烧的正确方法&sa=osari_fangyi', 'degree': '20550'}, {'query': '小儿肺炎5个常见症状', 'type': '0', 'url': 'https://m.baidu.com/s?word=小儿肺炎5个常见症状&sa=osari_fangyi', 'degree': '20500'}], 'gossips': [{'query': '纸币会传播冠状病毒', 'type': '7', 'url': 'https://m.baidu.com/s?word=纸币会传播冠状病毒&sa=osari_yaoyan', 'degree': '85560'}, {'query': '全身喷洒酒精可消毒', 'type': '7', 'url': 'https://m.baidu.com/s?word=全身喷洒酒精可消毒&sa=osari_yaoyan', 'degree': '68568'}, {'query': '武汉红十字会收取服务费', 'type': '7', 'url': 'https://m.baidu.com/s?word=武汉红十字会收取服务费&sa=osari_yaoyan', 'degree': '39528'}, {'query': '风油精涂人中防流感', 'type': '7', 'url': 'https://m.baidu.com/s?word=风油精涂人中防流感&sa=osari_yaoyan', 'degree': '37296'}, {'query': '超市买的东西必须消毒', 'type': '7', 'url': 'https://m.baidu.com/s?word=超市买的东西必须消毒&sa=osari_yaoyan', 'degree': '7224'}, {'query': '黑龙江高速大范围封闭', 'type': '7', 'url': 'https://m.baidu.com/s?word=黑龙江高速大范围封闭&sa=osari_yaoyan', 'degree': '6696'}, {'query': '香油滴鼻孔防传染', 'type': '7', 'degree': '4032', 'url': 'https://m.baidu.com/s?word=香油滴鼻孔防传染&sa=osari_yaoyan'}, {'query': '毛领绒线衣易吸附病毒', 'type': '7', 'url': 'https://m.baidu.com/s?word=毛领绒线衣易吸附病毒&sa=osari_yaoyan', 'degree': '3408'}], 'trend': {'updateDate': ['1.21', '1.22', '1.23', '1.24', '1.25', '1.26', '1.27', '1.28', '1.29', '1.30'], 'list': [{'name': '确诊', 'data': [440, 574, 835, 1297, 1985, 2761, 4535, 5997, 7736, 9720]}, {'name': '疑似', 'data': [37, 393, 1072, 1965, 2684, 5794, 6973, 9239, 12167, 15238]}, {'name': '治愈', 'data': [0, 0, 34, 38, 49, 51, 60, 103, 126, 171]}, {'name': '死亡', 'data': [0, 17, 25, 41, 56, 80, 106, 132, 170, 213]}]}, 'foreignLastUpdatedTime': '2020.01.31 18:25', 'mapSrc': 'https://mms-res.cdn.bcebos.com/mms-res/voicefe/captain/images/2f52e889c513dd37efb96ea6d11e3345.png?size=1050*803', 'trendChartSrc': 'https://mms-res.cdn.bcebos.com/mms-res/voicefe/captain/images/25f2183ac26ad934780329727093c622.png?size=1140*705'}], 'bundle': {'script': 'https://mms-res.cdn.bcebos.com/mms-res/voicefe/captain/bundles/105903b0.c495388b.js', 'style': 'https://mms-res.cdn.bcebos.com/mms-res/voicefe/captain/bundles/105903b0.ab549e5b.css'}}










