import socket
from queue import PriorityQueue
import threading
import time
import random

IP     = "127.0.0.1"
PORT   = 1205
INF    = 2441139
SERVER_NO = PORT

edgelist = [
]

distance = [
    (1201,INF),
    (1202,INF),
    (1203,INF),
    (1204,INF),
    (1205,0)
]

def dijkstra():
    print("Distance before update")
    print(distance)
    adj_list = [[],[],[],[],[]]
    visited = []
    for i in edgelist:
        adj_list[i[0]-1201].append((i[1]-1201,i[2]))

    node = PriorityQueue()
    #node -> (dist,v)
    node.put((0,SERVER_NO-1201))
    visited.append(SERVER_NO-1201)
    while not node.empty():
        u = node.get()[1]
        for vv in adj_list[u]:
            v = vv[0]
            cost = vv[1]
            if v not in visited:
                visited.append(v)
                if distance[v][1] >= distance[u][1] + cost:
                    distance[v] = (v+1201,distance[u][1] + cost)
                    node.put((distance[v][1],v))

    print("Distance after update")
    print(distance)

def update_edge(u, v, w):
    global edgelist
    edg_flag,up_flag = False,False
    t_edgelist = []
    for i in edgelist:
        if (i[0] == u and i[1] == v) or \
            (i[0] == v and i[1] == u):
            edg_flag = True
            if i[2] != w:
                up_flag = True
        else:
            t_edgelist.append(i)

    
    t_edgelist.append((u,v,w))
    t_edgelist.append((v,u,w))
    
    edgelist = t_edgelist

    if not edg_flag or up_flag:
        dijkstra()

def send():

    to_send = ''
    for i in edgelist:
        u,v,w = i
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

def receive(conn, addr):
    line = conn.recv(1024).decode()
    lst = line.splitlines()
    for info in lst:
        u, v, w = info.strip().split(',')
        u = int(u)
        v = int(v)
        w = int(w)
        print("received edge")
        print(u,v,w)
        update_edge(int(u), int(v), int(w))


def sent():
    while True:
        send()
        time.sleep(5)

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
    print(edgelist)
    f_in = open("graph.txt","r")
    for line in f_in.readlines():
        u,v,w = line.strip().split()
        u = int(u);v = int(v);w = int(w)
        if u == PORT or v == PORT:
            edgelist.append((u,v,w))

    f_in.close()
    print(edgelist)



create_edgelist()
# sock.settimeout(5)
recThread = threading.Thread(target=recvt, args=())
recThread.start()
time.sleep(5)
senThread = threading.Thread(target=sent, args=())
senThread.start()

startTim = time.time()

while True:
    
    currTim = time.time()
    if (currTim - startTim > 15):
        print("edge updated(main)")
        rankey = random.randint(0, len(edgelist)-1)
        ranWt = random.randint(10, 100)
        startTim = time.time()
        u,v,w = edgelist[rankey]
        
        w = ranWt

        for i in range(len(edgelist)):
            if edgelist[i][0] == v and edgelist[i][1] == u:
                edgelist[i] = (v,u,w)
                break
        print((u,v,w))
        send()