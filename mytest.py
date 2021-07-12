import requests
import time
import sys

port = sys.argv[1]
my_obj = {'key1':'value1', 'key2':'value2', 'key3':'value3'}

def myextract(r,exp_status,ifbody) :
    print('Expected status code :',exp_status,' recieved status code :',r.status_code)
    if exp_status == r.status_code :
        print('Successsful status code')
    else : 
        print('Unsuccessful status code')
    if r.text == '' and ifbody == True :
        print('Body was expected but not recieved')
    elif r.text != '' and ifbody == False :
        print('Body was not expected but recieved')
    elif r.text != '' and ifbody == True:
        print('Body was expected and body is recieved')
    else : print('Body was not expected and is not recieved')
    print(r.headers)
    print(r.text)
    print('\n')

#Normal basic GET requests for index file.
r = requests.get('http://127.0.0.1:'+port)
myextract(r,200,True)

r = requests.get('http://127.0.0.1:'+port+'/')
myextract(r,200,True)

r = requests.get('http://127.0.0.1:'+port+'/index.html')
myextract(r,200,True)

r = requests.get('http://127.0.0.1:'+port+'/withimage.html')
myextract(r,200,True)

#Conditional GET requests
#Manually checked that this file was modified after requested date. 
r = requests.get('http://127.0.0.1:'+port+'/index.html',headers = {'If-Modified-Since':'Wed, 04 Nov 2020 10:32:50 GMT'})
myextract(r,200,True)

#Manually checked that this file was not modified after requested date.
r = requests.get('http://127.0.0.1:'+port+'/withimage.html',headers = {'If-Modified-Since':'Wed, 04 Nov 2020 10:32:50 GMT'})
myextract(r,304,False)

#Last modified for invalid date
r = requests.get('http://127.0.0.1:'+port+'/withimage.html',headers = {'If-Modified-Since':'Wed, 04 Nov 2020 10:32:50 GMT'})
myextract(r,304,False)

#Manually checked that this file was modified after requested date.
r = requests.get('http://127.0.0.1:'+port+'/index.html',headers = {'If-Unmodified-Since':'Wed, 04 Nov 2020 10:32:50 GMT'})
myextract(r,412,True)

#Manually checked that this file was not modified after requested date. 
r = requests.get('http://127.0.0.1:'+port+'/withimage.html',headers = {'If-Unmodified-Since':'Wed, 04 Nov 2020 10:32:50 GMT'})
myextract(r,200,True)

#These GET requests are for files which DO NOT exist.
r = requests.get('http://127.0.0.1:'+port+'/hello.html')
myextract(r,404,True)

r = requests.get('http://127.0.0.1:'+port+'/hello')
myextract(r,404,True)

r = requests.get('http://127.0.0.1:'+port+'/hello.html',headers = {'If-Unmodified-Since':'Wed, 04 Nov 2020 10:32:50 GMT'})
myextract(r,404,True)

r = requests.get('http://127.0.0.1:'+port+'/hello.html',headers = {'If-Modified-Since':'Wed, 04 Nov 2020 10:32:50 GMT'})
myextract(r,404,True)

#Normal basic HEAD requests for index file.
r = requests.head('http://127.0.0.1:'+port)
myextract(r,200,False)

r = requests.head('http://127.0.0.1:'+port+'/')
myextract(r,200,False)

r = requests.head('http://127.0.0.1:'+port+'/index.html')
myextract(r,200,False)

#Responses for HEAD method with conditional requests
#Manually checked that this file was modified after requested date. 
r = requests.head('http://127.0.0.1:'+port+'/index.html',headers = {'If-Modified-Since':'Wed, 04 Nov 2020 10:32:50 GMT'})
myextract(r,200,False)

#Manually checked that this file was not modified after requested date.
r = requests.head('http://127.0.0.1:'+port+'/withimage.html',headers = {'If-Modified-Since':'Wed, 04 Nov 2020 10:32:50 GMT'})
myextract(r,304,False)

#Manually checked that this file was modified after requested date.
r = requests.head('http://127.0.0.1:'+port+'/index.html',headers = {'If-Unmodified-Since':'Wed, 04 Nov 2020 10:32:50 GMT'})
myextract(r,412,False)

#Manually checked that this file was not modified after requested date. 
r = requests.head('http://127.0.0.1:'+port+'/withimage.html',headers = {'If-Unmodified-Since':'Wed, 04 Nov 2020 10:32:50 GMT'})
myextract(r,200,False)

r = requests.head('http://127.0.0.1:'+port+'/withimage.html')
myextract(r,200,False)

#These HEAD requests are for files which DO NOT exist.
r = requests.head('http://127.0.0.1:'+port+'/hello.html')
myextract(r,404,False)

r = requests.head('http://127.0.0.1:'+port+'/hello')
myextract(r,404,False)

r = requests.head('http://127.0.0.1:'+port+'/hello.html',headers = {'If-Unmodified-Since':'Wed, 04 Nov 2020 10:32:50 GMT'})
myextract(r,404,False)

r = requests.head('http://127.0.0.1:'+port+'/hello.html',headers = {'If-Modified-Since':'Wed, 04 Nov 2020 10:32:50 GMT'})
myextract(r,404,False)

#Request for POST method with simple form data.
r = requests.post('http://127.0.0.1:'+port,data=my_obj)
myextract(r,204,False)

#Requests for PUT method
#For creating resource.
r = requests.put('http://127.0.0.1:'+port+'/hello/new.txt', data=my_obj)
myextract(r,201,False)

#For modifying existing resource.
r = requests.put('http://127.0.0.1:'+port+'/hello/new.txt', data=my_obj)
myextract(r,204,False)

#For bad request when file is not specified in request.
r = requests.put('http://127.0.0.1:'+port+'/good', data=my_obj)
myextract(r,400,True)

r = requests.put('http://127.0.0.1:'+port,data=my_obj)
myextract(r,400,True)

#Requests for DELETE method
#respose for resource deleted successfully.
r = requests.delete('http://127.0.0.1:'+port+'/hello/new.txt')
myextract(r,204,False)

#response for resource not found so cannot be deleted.
r = requests.delete('http://127.0.0.1:'+port+'/hello/new.txt')
myextract(r,404,True)

