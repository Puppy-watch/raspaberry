import socket
import pickle
# =============================================================================
# server
# =============================================================================
def run_server(port,do_work_server,s_count=1):
    # 1. init
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # 2. bind
    server.bind(('',port))
    
    # 3. listen
    server.listen(1)
    
    # 4. accept
    while s_count > 0:
        print('waiting for client connet')
        client,addr = server.accept()
        
        do_work_server(client, addr)
        client.close()
        s_count-=1
        
    server.close()


# =============================================================================
# client
# =============================================================================
def run_client(ip,port,do_work_client):
    # 1. init
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # 2. connect
    print('conneting!')
    client.connect((ip,port))
    print('success connet!')
    do_work_client(client)
    
    client.close()
    print('disconnet *^^*')
  
  
# =============================================================================
# common code
# =============================================================================

def my_recv(B_SIZE,client):
    data = client.recv(B_SIZE)
    if not data:
        return data
    cmd = pickle.loads(data)
    return cmd

def my_send(cmd, client):
    data = pickle.dumps(cmd) # 직렬화
    client.sendall(data)
    
    return 0