#!/usr/bin/ipython
# -*- coding: utf-8 -*-
# Code to be run using python3

import threading
import sys
from socket import *
import time
import calendar
import os
import hashlib
import zlib
import uuid
import gzip

global statuscodes,get_headers,type_field, cont_type_list
statuscodes = {
    '200': 'OK',
    '404': 'Not Found',
    '304': 'Not Modified',
    '400': 'Bad Request',
    '403': 'Forbidden',
    '204': 'No Content',
    '201': 'Created',
    '412': 'Precondition Failed'
    }

get_headers = {
    1: 'Content-Type',
    2: 'Content-Length',
    3: 'Date',
    4: 'Server',
    5: 'Connection',
    6: 'Last-Modified',
    7: 'Keep-Alive',
    8: 'Location',
    9: 'Content-Location',
    10: 'ETag',
    11: 'Content-Encoding'
    }

type_field = {
    'html': 'text/html',
    'jpg': 'application/jpg',
    'png': 'application/png',
    'mp4': 'application/mp4',
    'mp3': 'application/mp3',
    'pdf': 'application/pdf',
    'txt': 'text/text'
    }

cont_type_list = [
        'image/jpg',
        'image/png',
        'image/jpeg'
        ]

def mydatetime(now):
    (
        yy,
        mm,
        dd,
        hh,
        mn,
        ss,
        a,
        b,
        c,
        ) = time.localtime(now)
    daynum = calendar.weekday(yy, mm, dd)
    days = [
        'Mon',
        'Tue',
        'Wed',
        'Thu',
        'Fri',
        'Sat',
        'Sun',
        ]
    months = [
        'Jan',
        'Feb',
        'Mar',
        'Apr',
        'May',
        'Jun',
        'Jul',
        'Aug',
        'Sep',
        'Oct',
        'Nov',
        'Dec',
        ]
    s = '%03s, %2d %03s %04d %02d:%02d:%02d GMT' % (
        days[daynum],
        dd,
        months[mm - 1],
        yy,
        hh,
        mn,
        ss,
        )
    return s

def get_cksm(body):
    checksum = hashlib.md5(body).hexdigest()
    return checksum

def compare_modtime(if_mod, last_mod) :
    if_mod_sec = time.mktime(time.strptime(if_mod,'%a, %d %b %Y %H:%M:%S %Z'))
    if if_mod_sec < last_mod or if_mod_sec > time.time() :
        return True
    else :
        return False

def compare_unmodtime(if_unmod, last_mod) :
    if_unmod_sec = time.mktime(time.strptime(if_unmod,'%a, %d %b %Y %H:%M:%S %Z'))
    if if_unmod_sec > last_mod :
        return True
    else :
        return False

def set_para() :
    with open('httpserver.conf', 'r') as f :
        con = f.read()
    con = con.split('\n')
    global myDocRoot, myPostLog, myAccessLog, myErrorFiles
    #print(con)
    for x in con:
        if x != '':
            x = x.split('=')
            x[0] = x[0].strip()
            x[1] = x[1].strip()
            if x[0] == 'DocumentRoot' :
                myDocRoot = x[1]
            elif x[0] == 'LogDir':
                myPostLog = x[1]
                myAccessLog = x[1]
            elif x[0] == 'ErrorDir':
                myErrorFiles = x[1]

def access_log(head_list, meth_list, giv_date, giv_status, giv_length):
    str1 = '127.0.0.1 - - [' + giv_date + ' ] '
    str1 += head_list[0]
    str1 += ' ' +  giv_status + ' '
    str1 += giv_length + ' '
    str1 += 'http://' + host.split(': ')[1] + meth_list[1] + ' '
    str1 += user
    with open(myAccessLog + '/access.log' , 'a') as f:
        f.write(str1)
        f.write('\n')

def extract(sentence):
    head_list = sentence.split(b'\r\n')
    i = head_list.index(b'')
    for j in range(0,i+1):
        head_list[j] = head_list[j].decode()
    meth_list = head_list[0].split()
    #print(head_list)
    #print(meth_list)
    set_para()
    global modif,unmodif,user,host, cont_type,got_cookie
    host = None
    user = None
    modif = None
    unmodif = None
    got_cookie = None
    cont_type = None
    for i in range(0,i) :
        x = (head_list[i].split(':'))[0]
        if x == 'User-Agent':
            user = head_list[i]
        elif x == 'Host':
            host = head_list[i]
        elif x ==  'If-Modified-Since':
            modif = head_list[i]
        elif x == 'If-Unmodified-Since':
            unmodif = head_list[i]
        elif x == 'Content-Type':
            cont_type = head_list[i]
        elif x == 'Cookie':
            got_cookie = head_list[i]
    #Method extracted
    if meth_list[0] == 'GET':
        head_list[len(head_list)-1] = head_list[len(head_list)-1].decode()
        formed = get_message(head_list, meth_list)
    elif meth_list[0] == 'HEAD':
        head_list[len(head_list)-1] = head_list[len(head_list)-1].decode()
        formed = get_message(head_list, meth_list)
    elif meth_list[0] =='DELETE':
        head_list[len(head_list)-1] = head_list[len(head_list)-1].decode()
        formed = del_message (head_list, meth_list)
    elif meth_list[0] =='POST':
        formed = post_message(head_list, meth_list)
    elif meth_list[0] =='PUT':
        formed = put_message(head_list, meth_list)
    return formed

def get_message(head_list, meth_list):
    lastmodif = None
    if meth_list[1] == '/':
        f_name = myDocRoot + '/index.html'
        giv_status = '200'
        status = '200 ' + str(statuscodes['200']) + '\r\n'
        type_enc = 'text/html'
    elif meth_list[1][0] != '/':
        giv_status = '400'
        status = '400' + str(statuscodes['400']) + '\r\n'
        f_name = myErrorFiles + '/error400.html'
        type_enc = 'text/html'
    elif os.path.exists(myDocRoot + meth_list[1]) == False:
        f_name = myErrorFiles + '/error404.html'
        giv_status = '404'
        status = '404 ' + str(statuscodes['404']) + '\r\n'
        type_enc = 'text/html'
    elif os.path.exists(myDocRoot + meth_list[1]) == True and len(meth_list[1].split('.')) == 1:
        f_name = myErrorFiles + '/error404.html'
        giv_status = '404'
        status = '404 ' + str(statuscodes['404']) + '\r\n'
        type_enc = 'text/html'
    elif os.path.exists(myDocRoot + meth_list[1]) == True:
        f_name = myDocRoot + meth_list[1]
        giv_status = '200'
        status = '200 ' + str(statuscodes['200']) + '\r\n'
        type_enc = type_field[(meth_list[1].split('.'))[1]]
        lastmodif = f_name
    res1 = True
    res2 = True
    if modif != None and unmodif == None and giv_status != '404' and giv_status != '400':
        last_mod = os.path.getmtime(f_name)
        res1 = compare_modtime(modif[19:], last_mod)
        if res1 == False:
            giv_status = '304'
            status = '304 ' + str(statuscodes['304']) + '\r\n'
    body = ''
    if unmodif != None and modif == None and giv_status != '404' and giv_status != '400':
        last_mod = os.path.getmtime(f_name)
        res2 = compare_unmodtime(unmodif[21:], last_mod)
        if res2 == False:
            giv_status = '412'
            status = '412 ' + str(statuscodes['412']) + '\r\n'
            type_enc = 'text/html'
            with open(myErrorFiles + '/error412.html', 'rb') as f :
                body = f.read()
            lastmodif = None
    if meth_list[0] != 'HEAD' and res1 != False and res2 != False :        
        with open(f_name, 'rb') as f :
            body = f.read()
    res_message = 'HTTP/1.1 ' + status
    res_message += get_headers[4] + ': Project Server HTTP\r\n'
    giv_date = mydatetime(time.time())
    res_message += get_headers[3] + ': ' + str(giv_date) + '\r\n'
    if got_cookie != None and giv_status != '404' and giv_status != '412': 
        res_message += got_cookie + '\r\n'
    elif got_cookie == None and giv_status != '404' and giv_status != '412':
        myuuid = str(uuid.uuid1())
        res_message += 'Set-Cookie: ' + myuuid + '\r\n'
    giv_length = '0'
    if meth_list[0] != 'HEAD' and res1 != False :
        giv_length = str(len(body))
        res_message += get_headers[2] + ': ' + giv_length + '\r\n'
        res_message += get_headers[1] + ': ' + type_enc + '\r\n'
        cksm = get_cksm(body)
        res_message += get_headers[10] + ': ' + cksm + '\r\n'
    if lastmodif != None :
        res_message += get_headers[6] + ': ' + str(mydatetime(os.path.getmtime(f_name))) + '\r\n'
    res_message += get_headers[5] + ': ' + 'Close\r\n\r\n'
    res_message = bytes(res_message, 'utf-8')
    if meth_list[0] != 'HEAD' and res1 != False :
        res_message += body
    access_log(head_list, meth_list, giv_date, giv_status, giv_length)
    return res_message

def del_message(head_list, meth_list):
    if os.path.exists(myDocRoot + meth_list[1]) == True:
        giv_status = '204'
        status = '204 ' + str(statuscodes['204']) + '\r\n'
    else:
        giv_status = '404'
        status = '404 ' + str(statuscodes['404']) + '\r\n'
    res_message = 'HTTP/1.1 ' + status 
    res_message += get_headers[4] + ': Project Server HTTP\r\n'
    giv_date = str(mydatetime(time.time()))
    res_message += get_headers[3] + ': ' + giv_date + '\r\n'
    giv_length = '0'
    if os.path.exists(myDocRoot + meth_list[1]) == False:
        with open(myErrorFiles + '/error404.html','rb') as f:
            body=f.read()
        giv_length = str(len(body))
        res_message += get_headers[2] + ': ' + giv_length + '\r\n'
        res_message += get_headers[1] + ': ' + 'text/html\r\n'
    if got_cookie != None and giv_status != '404' :
        res_message += got_cookie + '\r\n'
    elif got_cookie == None and giv_status != '404' :
        myuuid = str(uuid.uuid1())
        res_message += 'Set-Cookie: ' + myuuid + '\r\n'
    res_message += get_headers[5] + ': ' + 'Close\r\n\r\n'
    res_message = bytes(res_message, 'utf-8')
    if os.path.exists(myDocRoot + meth_list[1]) == False:
        res_message += body
    try :
        os.remove(myDocRoot + meth_list[1])
    except :
        pass
    access_log(head_list, meth_list, giv_date, giv_status, giv_length)
    return res_message

def post_message(head_list,meth_list):
    f_name = myPostLog + '/post.log'
    i = head_list.index('')
    x = b''
    for j in range(i+1,len(head_list)):
        x += head_list[j]
    status = '204 ' + str(statuscodes['204']) + '\r\n'
    res_message = 'HTTP/1.1 ' + status
    res_message += get_headers[4] + ': Project Server HTTP\r\n'
    giv_date = str(mydatetime(time.time()))
    res_message += get_headers[3] + ': ' + giv_date + '\r\n'
    if got_cookie != None:
        res_message += got_cookie + '\r\n'
    else:
        myuuid = str(uuid.uuid1())
        res_message += 'Set-Cookie: ' + myuuid + '\r\n'
    res_message += get_headers[5] + ': ' + 'Closer\r\n\r\n'
    res_message = bytes(res_message, 'utf-8')
    data = user + '\n' + giv_date + '\n'
    data1 = bytes(data, 'utf-8')
    data1 = data1 + x + b'\n'
    with open(f_name, 'ab') as f :
        f.write(data1)
    access_log(head_list, meth_list, giv_date, '204', '0')
    return res_message

def put_message(head_list, meth_list):
    mypath = myDocRoot + meth_list[1]
    x = len(mypath)-1
    while(x>0):
        if(mypath[x] != '/'):
            x = x-1
        else:
            break
    check_path = os.path.exists(mypath[0:x])
    var = mypath[0:x]
    f_name = myDocRoot + meth_list[1]
    i = head_list.index('')
    x = b''
    for j in range(i+1,len(head_list)-1):
        x = x + head_list[j] + b'\r\n'
    data = x + head_list[len(head_list)-1]
    print(data)
    print(f_name)
    body = ''
    if meth_list[1] == '/' or len(meth_list[1].split('.')) == 1:
        giv_status = '400'
        status = '400 ' + str(statuscodes['400']) + '\r\n'
        with open(myErrorFiles + '/error400.html', 'rb') as f :
            body = f.read()
    elif os.path.exists(f_name) == True:
        giv_status = '204'
        status = '204 ' +  str(statuscodes['204']) + '\r\n'
        with open(f_name, 'wb') as f:
            f.write(data)
    elif(check_path and os.path.exists(f_name) == False):
        giv_status = '201'
        status = '201 ' + str(statuscodes['201']) + '\r\n'
        with open(f_name, 'wb') as f:
            f.write(data)
    elif(check_path==False):
        giv_status = '201'
        status = '201 ' + str(statuscodes['201']) + '\r\n'
        os.makedirs(var)
        with open(f_name, 'wb') as f :
            f.write(data)
    giv_length = '0'
    res_message = 'HTTP/1.1 ' + status
    res_message += get_headers[4] + ': Project Server HTTP\r\n'
    giv_date = str(mydatetime(time.time()))
    res_message += get_headers[3] + ': ' + giv_date + '\r\n'
    if got_cookie != None and giv_status != '400':
        res_message += got_cookie + '\r\n'
    elif got_cookie == None and giv_status != '400':
        myuuid = str(uuid.uuid1())
        res_message += 'Set-Cookie: ' + myuuid + '\r\n'
    if body != '':
        giv_length = str(len(body))
        res_message += get_headers[2] + ': ' + giv_length + '\n'
        res_message += get_headers[1] + ': ' + 'text/html\n'
    res_message += get_headers[5] + ': ' + 'Close\r\n\r\n'
    res_message = bytes(res_message, 'utf-8')
    if body != '':
        res_message += body
    access_log(head_list, meth_list, giv_date, giv_status, giv_length)
    return res_message 

def message(connection_socket):
    while True:
       #sentence = connection_socket.recv(1024).decode()
        #print(sentence)
        sentence = connection_socket.recv(10485760)
        if(sentence != b''):
            print(sentence)
            response = extract(sentence)
            connection_socket.send(response)        # So, user cannot use stop as a message string
            break
    connection_socket.close()

server_port = int(sys.argv[1])  # port no as command line arguement
server_socket = socket(AF_INET, SOCK_STREAM)
server_socket.bind(('', server_port))  # binds port number to socket
server_socket.listen(1)
print('The server is ready\n')

while True:
    (connect_socket, address) = server_socket.accept()
    print(address)
    print(connect_socket)
    t1 = threading.Thread(target = message, args = (connect_socket,))       #creates a thread for every newly connected client
    t1.start()
