import requests
import threading
import time
import sys 

n= int(sys.argv[2])
port = sys.argv[1]
print(port)

def GET_REQUEST(url,n):
	print(n)
	try: 
		r = requests.get(url,headers={'If-Modified-Since':'Wed, 04 Nov 2020 19:12:34 GMT'})
		print(type(r.status_code))
		print(r.text)
		print(r.headers)
	except:
		print('Unsuccessful')
	return 

if __name__=='__main__':
	list_threads=[]
	while(n):
		client_thread = threading.Thread(target = GET_REQUEST, args = ['http://127.0.0.1:'+port+'/index.html',n])
		client_thread.start()
		print('in main')
		list_threads.append(client_thread)
		n = n-1

	for threads in list_threads:
		threads.join()
