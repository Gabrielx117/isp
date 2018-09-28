#!/usr/bin/env python3
# coding=utf-8
import time
import urllib.request
import sys
import json
import re
import pickle
import smtplib
import ssl
# from collections import Iterable
from email import encoders
from email.header import Header
from email.mime.text import MIMEText
from email.utils import parseaddr, formataddr


DEBUG = 0
unicom = {'cname':'中国联通','url':'http://ispip.clang.cn/unicom_cnc_cidr.txt','file':'%s/unicom.txt' % sys.path[0]}
telecom = {'cname':'中国电信','url':'https://ispip.clang.cn/chinatelecom_cidr.txt','file':'%s/telecom.txt' % sys.path[0]}
cmcc = {'cname':'中国移动','url':'https://ispip.clang.cn/cmcc_cidr.txt','file':'%s/cmcc.txt' % sys.path[0]}


date = time.strftime("%Y%m%d", time.localtime())

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

def get(isp):
    with urllib.request.urlopen(isp['url'], context=ctx) as i:
        ip=i.readlines()

    new = set(ip)

    try:
        with open(isp['file'], 'rb') as i:
            old = set(pickle.load(i))
    except:
        IndexError
        old = set()

    with open(isp['file'], 'wb') as i:
        pickle.dump(ip, i)

    add    = new - old or None# 新增差量
    remove = old - new or None
    return format(isp['cname'],add,remove)

def format(cname,add,remove):
    if add and remove:
        add=str(b''.join(sorted(add)),encoding = "utf-8")
        remove=str(b''.join(sorted(remove)),encoding = "utf-8")
        context='%s\n新增\n%s\n\n删除\n%s' %(cname,add,remove)
    elif not add and remove:
        remove=str(b''.join(sorted(remove)),encoding = "utf-8")
        context='%s\n删除\n%s' %(cname,remove)
    elif add and not remove:
        add=str(b''.join(sorted(add)),encoding = "utf-8")
        context='%s\n新增\n%s' %(cname,add)
    else:
        context = None
    return context

def _format_addr(s):
    name, addr = parseaddr(s)
    return formataddr((Header(name).encode(), addr))

def let_them_know(context):
    print (context)
    email = '%s/email.json' % sys.path[0]
    with open(email, 'r', encoding='utf-8') as f:
        email_info = json.load(f)
    to_addr = email_info.get('to_addr')
    # 生成收件人列表
    email_list = ','.join( _format_addr('%s <%s>' % (k,v)) for k,v in to_addr.items())
    # 填写邮件内容
    msg = MIMEText(context, 'plain', 'utf-8')
    msg['From'] = _format_addr('天津网管监控 <%s>' % email_info['from_addr'])
    msg['To'] = email_list
    msg['Subject'] = Header('ISP地址段更新').encode()
    # 发送邮件
    server = smtplib.SMTP(email_info['smtp_server'], 25)
    server.login(email_info['from_addr'],email_info['passwd'])
    server.sendmail(email_info['from_addr'], to_addr.values(), msg.as_string())
    server.quit()

if DEBUG == 1:
    import io
    #sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    #server.set_debuglevel(1)
    print('add')
    print(len(add))
    print('remove')
    print(len(remove))

# result={}
result_unicom=get(unicom)
result_telecom=get(telecom)
result_cmcc=get(cmcc)
# print (result)
if result_cmcc or result_unicom or result_telecom:
    result='\n'.join(filter(None,[result_cmcc,result_unicom,result_telecom]))
    let_them_know(result)
else:
    print ('meiyoiu')
    exit(0)


#
# if add is '暂无' and remove is '暂无':
#     exit(0)
# else:
# get(unicom)

# let_them_know(get(unicom))
