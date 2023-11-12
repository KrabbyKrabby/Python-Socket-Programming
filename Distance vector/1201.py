import socket
from queue import PriorityQueue
import threading
import time
import random

IP     = "127.0.0.1"
PORT   = 1201
INF    = 2441139
SERVER_NO = PORT
CONVERGE_FLAG = True
edgelist = [
]

distance = [
    [1201,0],
    [1202,INF],
    [1203,INF],
    [1204,INF],
    [1205,INF]
]

distance_vector = {}
changed = 0

def d(j,node):
    for i in distance_vector[j]:
        if i[0] == node:
            return i[1]

def c(u,v):
    for i in edgelist:
        if i[0] == u and i[1] == v:
            return i[2]

def bellman_ford():
    global changed
    for i in range(len(distance)):
        node = distance[i][0]
        if node == PORT:
            continue
        mn = INF
        for j in edgelist:
            val = c(PORT,j[1]) + d(j[1],node)
            mn = min(mn,val)

        if mn != distance[i][1]:
            distance[i][1] = mn
            changed = 1

        

#update this to send distance- done
def send():
    to_send = ''
    for i in distance:
        u,v,w = PORT,i[0],i[1]
        to_send += f'{u},{v},{w}\n'
    for i in edgelist:
        u,v,w = i
        if u == PORT:
            client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                client.connect(('127.0.0.1',int(v)))
                client.send(to_send.encode())
                client.close()
            except:
                client.close()

#update this to recieve vector
def receive(conn, addr): 
    global changed
    print("before distance ",distance)
    line = conn.recv(1024).decode()
    lst = line.splitlines()
    idx = 0
    flag = 0
    changed = 0
    for info in lst:
        u, v, w = info.strip().split(',')
        flag = int(u)
        u = int(u)
        v = int(v)
        w = int(w)
        distance_vector[u][idx] = [v,w]
        idx = idx+1

    print("received DV from ",flag)
    bellman_ford()
    print("after distance ",distance)
    print("\n")

    if changed == 1 :
        send()

def recvt():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('127.0.0.1', PORT))
    sock.listen()
    print(f"Node {PORT}")
    while True:
        conn, addr = sock.accept()
        thread = threading.Thread(target=receive, args=(conn, addr))
        thread.start()

def create_edgelist():
    f_in = open("graph.txt","r")
    for line in f_in.readlines():
        u,v,w = line.strip().split()
        u = int(u);v = int(v);w = int(w)
        if u == PORT:
            distance_vector[v] = [ [1201,INF],[1202,INF],[1203,INF],[1204,INF],[1205,INF] ]
            edgelist.append((u,v,w))
    f_in.close()

def main():
    create_edgelist()
    recThread = threading.Thread(target=recvt, args=())
    recThread.start()
    time.sleep(15)
    send()

    startTim = time.time()

    while True:
    
        currTim = time.time()
        if (currTim - startTim > 30):
            print("edge updated(main)")
            rankey = random.randint(0, len(edgelist)-1)
            ranWt = random.randint(10, 100)
            startTim = time.time()
            u,v,w = edgelist[rankey]
            print("before update ",edgelist[rankey])
            w = ranWt

            edgelist[rankey] = u,v,w

            print("after update ",edgelist[rankey])
            bellman_ford()
            send()

if __name__ == '__main__':
    main()

