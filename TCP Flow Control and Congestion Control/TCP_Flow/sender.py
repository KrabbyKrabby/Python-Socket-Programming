import socket
import os
from _thread import *



HOST = '127.0.0.1'
PORT = 869

ServerSideSocket = socket.socket()



#connection establishment
#____________________________
try:
    ServerSideSocket.bind((HOST, PORT))
except socket.error as e:
    print(e)


print('Socket is listening..')
ServerSideSocket.listen(5)
#____________________________




def create_header(
                src_port = 88,  #2 bytes
                dest_port = 88, #2 bytes
                seq = 0,   #4 bytes 
                ack = 0,   #4 bytes
                if_ack = 0, #ack = 1 -> if acknowledgement, 0 otherwise
                syn = 0, #syn = 1-> if synch req
                rwnd = 0, #2 bytes
                checksum = 0, #2 bytes
                urgent_pointer = 0, #2 bytes
                ):
            return src_port.to_bytes(2) + \
                   dest_port.to_bytes(2) + \
                   seq.to_bytes(4) + \
                   ack.to_bytes(4) + \
                   if_ack.to_bytes(1) + \
                   syn.to_bytes(1) + \
                   rwnd.to_bytes(2) + \
                   checksum.to_bytes(2) + \
                   urgent_pointer.to_bytes(2)
#will return a tuple - > (seq_number, ack_number, if_ack, syn, rwnd)
def retrieve_header(header):
    return \
        int.from_bytes(header[4:8]),\
        int.from_bytes(header[8:12]),\
        int.from_bytes(header[12:13]),\
        int.from_bytes(header[13:14]),\
        int.from_bytes(header[14:16])



#test file data
# file_data = b'In view, a humble vaudevillian veteran, cast vicariously as \
# both victim and villain by the vicissitudes of Fate. This visage, \
# no mere veneer of vanity, is a vestige of the vox populi, now vacant, vanished'

file_data = open("sample.txt","rb")

# print(len(file_data))

FILE_END = 6090
MSS = 200
HEADER_SIZE = 20

print("FILE END : ",FILE_END)

def server_thread(connection):
    connection.send('Server Is Connected'.encode())
    connection.settimeout(1)
    #start
    EST_STATE = False
    file_pointer = 0
    cur_seq = 0
    
    while True:
        #send/receive here
        if not EST_STATE:
            #connection establishment phase

            header = connection.recv(HEADER_SIZE)
            seq,ack,if_ack,syn,rwnd = retrieve_header(header)

            print("EST STATE : ",
            "SEQ:",seq,"ACK_NO:",ack,"ACK:",
            if_ack,"SYN:",syn,"WINDOW SIZE:",rwnd)

            if syn == 0:
                cur_seq = ack
                EST_STATE = True
            else:
                connection.send(create_header(
                    seq = cur_seq,
                    ack = seq + MSS,
                    if_ack = 1,
                    syn = 1
                ))
        else:
            #data tranfer phase
            while rwnd >= MSS:
                try:
                    # to_send = file_data[cur_seq : (cur_seq+MSS)]
                    to_send = file_data.read(MSS)
                    connection.send(
                        create_header(
                            seq=cur_seq,
                        ) + to_send
                    )
                    file_pointer += MSS
                    rwnd -= MSS
                    cur_seq += MSS
                    
                except Exception as e:
                    break
            

            if cur_seq >= FILE_END:
                break
            

            seq,ack,if_ack,syn,rwnd = retrieve_header(connection.recv(HEADER_SIZE))
            cur_seq = ack
            print("ack:" ,ack,"rwnd:",rwnd)

            

    # connection.close()
    print("DATA SENT")



#threading for multi client
#____________________________
def main():
    ThreadCount = 0 
    while True:
        Client, address = ServerSideSocket.accept()
        print('Connected to: ' + address[0] + ':' + str(address[1]))
        
        try:
            start_new_thread(server_thread, (Client, ))
        except Exception as e:
            continue
        ThreadCount += 1
        print('Thread Number: ' + str(ThreadCount))
    ServerSideSocket.close()

if __name__ == "__main__":
    main()

#____________________________