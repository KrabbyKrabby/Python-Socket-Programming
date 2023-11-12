import socket
import threading
import time
import random

PORT = 2001
ASN = 2

preference = {
    1 : 100,
    2 : 100,
    3 : 100,
    4 : 100
}
ASpaths = {

}

eNode = [1001,3001]
iNode = []

edgelist = {
    2001: [1001,3001]
}


#bfs code 
def bfs(source,start_num):
    global edgelist
    visited = []
    queue = []
    queue.append([source])
    while queue:
        path = queue.pop(0)
        node = path[-1]
        if node not in visited:
            neighbours = edgelist[node]
            for neighbour in neighbours:
                new_path = list(path)
                new_path.append(neighbour)
                queue.append(new_path)
                if int(str(neighbour)[0]) == start_num:
                    return len(new_path)
            visited.append(node)

def isBetter(newPath,oldPath):
    old = oldPath[1]
    new = newPath[1]
    old_next_ASN = int(int(oldPath[2])/1000)
    new_next_ASN= int(int(newPath[2])/1000)

    flag = int(0)

    if preference[new_next_ASN] > preference[old_next_ASN] : 
        flag = 1
    elif preference[new_next_ASN] < preference[old_next_ASN]: 
        flag = 0
    else:
        if len(new) < len(old) :
            flag = 1
        elif len(new) > len(old) : 
            flag = 0
        else:
            if bfs(PORT,new_next_ASN) < bfs(PORT,old_next_ASN):
                flag = 1
            else:
                flag = 0
    print(flag)
    return flag




def process_path(st):
    print(st)
    global eNode
    global iNode
    source = st[0]
    path = st[1]
    nexthop = int(st[2])
    nextASN = int(nexthop/1000)

    temp = str(ASN) + " " + path

    if source in ASpaths.keys():
        oldPath = ASpaths[source]
        newPath = st
        newPath[1] = str(ASN) + " " + newPath[1]
        if isBetter(newPath,oldPath) == 1:
            send(source,temp,str(PORT),eNode)
            send(source,path,nexthop,iNode)
            ASpaths[source] = newPath
        else:
            send(source,temp,str(PORT),eNode)
            send(source,path,nexthop,iNode)
    else:
        send(source,temp,str(PORT),eNode)
        send(source,path,nexthop,iNode)
        st[1] = str(ASN) + " " + st[1]
        ASpaths[source] = st





def send(source,path,nexthop,edge_list ):
    to_send = str(source) + "\n" + str(path) + "\n" + str(nexthop)
    for v in edge_list:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            client.connect(('127.0.0.1',int(v)))
            client.send(to_send.encode())
            client.close()
        except:
            client.close()


def receive(conn,addr):
    global ASN
    data = conn.recv(1024).decode()
    st = data.splitlines()
    #print(st)
    if str(ASN) in st[1]:
        return 
    
    process_path(st)

def recvt():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('127.0.0.1', PORT))
    sock.listen()
    print(f"Node {PORT}")
    while True:
        conn, addr = sock.accept()
        thread = threading.Thread(target=receive, args=(conn, addr))
        thread.start()

recThread = threading.Thread(target=recvt, args=())
recThread.start()
time.sleep(10)
print("hello")
send(str(ASN), str(ASN), str(PORT), eNode)
send(str(ASN), "", str(PORT), iNode)
time.sleep(15)
print(f"server at {PORT}")
print(ASpaths)
while True:
    inp = input("->")