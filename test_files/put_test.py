import requests
import threading
import time
import sys 

n= int(sys.argv[2])
port = sys.argv[1]
print(port)
my_obj = {'key':'value', 'new':'hi'}

def PUT_REQUEST(url,n):
	print(n)
	try: 
		r = requests.put(url, data = my_obj)
		print(r.status_code)
		print(r.text)
		print(r.headers)
	except:
		print('Unsuccessful')
	return 

if __name__=='__main__':
	list_threads=[]
	while(n):
		client_thread = threading.Thread(target = PUT_REQUEST, args = ['http://127.0.0.1:' +port + '/newnew/newfile.txt',n])
		client_thread.start()
		print('in main')
		list_threads.append(client_thread)
		n = n-1

	for threads in list_threads:
		threads.join()
