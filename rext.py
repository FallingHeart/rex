__version__ = '0.1.23'

import re
import pymongo
import pandas as pd
import os
import csv
import json
import pytz
import datetime
import dateutil
import random
import requests
import time


class mos():

    def check_dir_and_create(path):
        data_dir = "/".join(path.split("/")[0:-1])
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)

    def get_file_list(path):
        for root, dirs, files in os.walk(path):
            pass
        return files


class mtime():
    def get_iso_time():
        utc_tz = pytz.timezone('Asia/Shanghai')
        datetime_now = datetime.datetime.now(tz=utc_tz)
        datestr = datetime_now.isoformat()
        mydatetime = dateutil.parser.parse(datestr)
        return mydatetime

    def get_iso_time_from_now(days):
        utc_tz = pytz.timezone('Asia/Shanghai')
        datetime_now = datetime.datetime.now(tz=utc_tz)
        datetime_delta = datetime.timedelta(days=days)
        datetime_end = datetime_now + datetime_delta
        datestr = datetime_end.isoformat()
        mydatetime = dateutil.parser.parse(datestr)
        return mydatetime


class mstring():

    # 空白符种类

    # ' '空格
    # '\t'水平制表符
    # '\n'换行
    # '\r'回车
    # '\f'换页
    # '\v'垂直制表符

    # 除去两端空格

    def remove_space_twoends(s):
        return s.strip()

    # 删除所有空格

    def remove_space_all(s):
        return s.replace(" ", "")

    # 利用翻译删除指定空白字符

    def remove_white_type(s, sign=' \t\n\r\f\v'):
        return s.translate(None, sign)

    # 删除所有空白符

    def remove_white_all(s):
        return ''.join(s.split())

    # 空白字符替换成空格

    def white2space(s, sign=' \t\n\r\f\v'):
        return s.translate(' ', sign)

    # 多个空格保留一个

    def muti2single_space(s):
        return ' '.join(s.split())

    # 对于来自钉钉云文档的csv下载 务必过滤\xa0
    def nbsp2space(s):
        return s.replace('\xa0', ' ')

    def get_random_36(n):
        randomStr = ""
        for i in range(n):
            temp = random.randrange(0, 3)
            if temp == 0:
                ch = chr(random.randrange(ord('A'), ord('Z') + 1))
                randomStr += ch
            elif temp == 1:
                ch = chr(random.randrange(ord('a'), ord('z') + 1))
                randomStr += ch
            else:
                ch = str((random.randrange(0, 10)))
                randomStr += ch
        return randomStr

    def may_equal_item(s):
        return mstring.remove_white_all(s.upper()).replace('-', '')
    
    def may_equal(a, b):
        return a == mstring.may_equal_item(b)
    
    def may_equal_conf(a, b):
        for i in [a,b]:
            # a b都要是对象
            if type(i) is not type({}):
                raise TypeError
            # a b都要有item和keys两个键
            if 'item' in i.keys() and 'keys' in i.keys() :
                pass
            else:
                raise KeyError
            # a b的item值都要是对象
            if type(i['item']) is not type({}) :
                raise TypeError
            # a b的keys值都要是数组
            if type(i['keys']) is not type([]):
                raise TypeError
            # a b的keys值都要是非空数组
            if len(i['keys']) == 0 :
                raise TypeError
        flag = False
        for a_key in a['keys']:
            if a_key in a['item'].keys() and a['item'][a_key] != "" and a['item'][a_key] != None:
                # a 有值
                for b_key in b['keys']:
                    if b_key in b['item'].keys() and b['item'][b_key] != "" and b['item'][b_key] != None:
                        # b 有值
                        flag = mstring.may_equal_item(a['item'][a_key]) == mstring.may_equal_item(b['item'][b_key])
                        if flag:
                            return flag
                    else:
                        # b 无值
                        continue
            else:
                # a 无值
                continue
        return flag


class mlist():

    def get_cols(data_list):
        columns = []
        if len(data_list) > 0:
            first = data_list[0]
            columns = list(first.keys())
        return columns

    def from_csv(path, options):
        with open(path, 'r', encoding='utf-8-sig')as f:
            reader = csv.DictReader(f)
            data_list = []
            for each in reader:
                temp = each
                if temp[options["important_key"]]:
                    for key in temp.keys():
                        temp[key] = mstring.muti2single_space(mstring.remove_space_twoends(mstring.nbsp2space(temp[key])))
                    data_list.append(temp)
            return data_list

    def to_csv(data_list, columns, path):
        mos.check_dir_and_create(path)
        result_list = pd.DataFrame(columns=columns, data=data_list)
        result_list.to_csv(path, encoding='utf-8-sig', index=False)

    def from_excel(path, sheet_name):
        temp_df = pd.read_excel(path, sheet_name=sheet_name, dtype=str)
        data_list = list(temp_df.to_dict('records'))
        return data_list

    def to_excel(data_list, columns, path):
        result_list = pd.DataFrame(columns=columns, data=data_list)
        result_list.to_excel(path, encoding='utf-8-sig', index=False)

    def from_json(path):
        with open(path, 'r', encoding='utf-8-sig') as f:
            pre_data_list = json.load(f)
            data_list = []
            for item in pre_data_list:
                data_list.append(item)
            return data_list

    def to_json(data_list, columns, path):
        mos.check_dir_and_create(path)
        result_list = pd.DataFrame(columns=columns, data=data_list)
        out = result_list.to_json(indent=4, orient='records', force_ascii=False).replace(r"\/", "/")
        with open(path, 'w', encoding='utf-8-sig')as jsonfile:
            jsonfile.write(out)

    def from_mongodb(db, col, filter):

        mycol = db[col]
        dataCursor = mycol.find(filter)
        return list(dataCursor)

    def to_map(list, key):
        temp_map = {}
        for i, item in enumerate(list):
            if key == "":
                temp_map[i] = item
            elif key in item.keys():
                temp_map[item[key]] = item
            else:
                temp_map[key(item)] = item
        return temp_map

    def header_handler(data, options):
        result_data = []
        for row in data:
            temp = {}
            for key in row.keys():
                if key != "":
                    if key in options.keys():
                        temp[options[key]] = row[key]
                    else:
                        temp[key] = row[key]
            result_data.append(temp)
        return result_data

    def field_handler(data, options):
        result_data = []
        for row in data:
            temp = row
            for key in options.keys():
                if type(options[key]) == str:
                    temp[key] = options[key]
                else:
                    temp[key] = options[key](row)
            result_data.append(temp)
        return result_data

    def field_makeup(data, options):
        if len(data) == 0 or len(options) == 0:
            return data
        temp_map = {}
        for i in options:
            temp_map[i] = ""
        for j in data:
            for k in temp_map.keys():
                if k in j.keys() and j[k] != "":
                    temp_map[k] = j[k]
                else:
                    j[k] = temp_map[k]
        return data


class mdict():

    def to_list(map):
        temp_list = []
        for i in map:
            temp_list.append(map[i])
        return temp_list


class mdb():

    def connect_mongodb(options, db):
        DB_HOST = options['DB_HOST']
        DB_PORT = options['DB_PORT']
        DB_USER = options['DB_USER']
        DB_PASS = options['DB_PASS']
        DB_DB = db

        if DB_USER == "":
            myclient = pymongo.MongoClient("mongodb://%s:%s/" % (DB_HOST, DB_PORT))
        else:
            if DB_DB == "admin":
                myclient = pymongo.MongoClient("mongodb://%s:%s@%s:%s/" % (DB_USER, DB_PASS, DB_HOST, DB_PORT))
            else:
                myclient = pymongo.MongoClient("mongodb://%s:%s@%s:%s/%s" % (DB_USER, DB_PASS, DB_HOST, DB_PORT, DB_DB))

        return myclient[DB_DB]


class mcol():
    def __init__(self, data_list):
        self.data_list = data_list

    def find_one(self, options):
        for i in self.data_list:
            for j in options.keys():
                if (j in i.keys()) and (i[j] == options[j]):
                    return i
        return {}

    def find(self, options):
        result = []
        for i in self.data_list:
            bool_array = []
            for j in options.keys():
                if j in i.keys():
                    bool_array.append(i[j] == options[j])
            if (len(bool_array) > 0) and (not False in bool_array):
                result.append(i)
        return result


class mchem():
    def is_cas(cas):
        cas = str(cas).strip()
        if not re.match('^\d{2,12}-\d{2}-\d$', cas):
            return False
        strArr = cas.split('-')
        if len(strArr) != 3:
            return False
        tmpS = strArr[0] + strArr[1]
        lenofstr = len(tmpS)
        crcTotal = 0
        for i in range(0, lenofstr):
            crcTotal += int(tmpS[i]) * (lenofstr - i)
        return int(strArr[2]) == (crcTotal % 10)

class mip():

    def remove_invalid_ip(some_db, some_col_name):
        mycol = some_db[some_col_name]
        fail_ip_list = mlist.from_mongodb(some_db, some_col_name, {"status": "fail"})
        for ip in fail_ip_list:
            if ip['status'] == "fail":
                mycol.delete_one({'_id': ip['_id']})


    def get_ip_from(ip, sleep_time,api_name):
        if api_name == "ip-api.com":
            res = requests.get('http://ip-api.com/json/%s' % ip)
            if res.status_code == 200:
                ipInfo = res.json()
                return ipInfo
            elif res.status_code == 429:
                print("mip.get_ip_from:X-Rl", res.headers['X-Rl'], "X-Ttl", res.headers['X-Ttl'])
                if res.headers['X-Rl'] == 0:
                    sleep_time = res.headers['X-Ttl']
                else:
                    sleep_time = 0
                # 这个接口最高每分钟45次，多了要收费，详见https://members.ip-api.com/#pricing
                time.sleep(sleep_time)
                return mip.get_ip_from(ip, sleep_time,api_name)
        else:
            return {
                'status':"fail"
            }


    def ip_to_db(some_list, ip_key, some_col):
        len_of_list = len(some_list)
        print("mip.ip_to_db:len_of_list", len_of_list)
        for i, item in enumerate(some_list):
            print(i + 1, len_of_list, end="\r")
            if type(item) == type(""):
                ip = item
            if type(item) == type({}):
                ip = item[ip_key]
            if ip == '127.0.0.1':
                print('mip.ip_to_db:ip localhost')
                continue
            existIp = some_col.find_one({'query': ip})  # "ip-api.com"接口的返回中，ip字段为query
            if not existIp:
                ipInfo = mip.get_ip_from(ip, 0, "ip-api.com")
                if ipInfo['status'] == 'success':
                    insertResult = some_col.insert_one(ipInfo)
                    if insertResult:
                        print('mip.ip_to_db:ip %s inserted' % ip)
                    else:
                        print('mip.ip_to_db:ip %s insert err' % ip)
                else:
                    print('mip.ip_to_db: ',ipInfo)
    

def main():
    pass


if __name__ == '__main__':
    main()
