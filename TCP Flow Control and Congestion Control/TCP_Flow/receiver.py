import random as rnd
import socket
import time

clientSocket = socket.socket()

HOST = '127.0.0.1'
PORT = 869

print('Waiting for connection response')
try:
    clientSocket.connect((HOST, PORT))
except socket.error as e:
    print(str(e))
res = clientSocket.recv(1024)
print(res.decode())

def create_header(
                src_port = 88,  #2 bytes
                dest_port = 88, #2 bytes
                seq = 0,   #4 bytes 
                ack = 0,   #4 bytes
                if_ack = 0, #ack = 1 -> if acknowledgement, 0 otherwise
                syn = 0, #syn = 1-> if synch req
                window_size = 0, #2 bytes
                checksum = 0, #2 bytes
                urgent_pointer = 0, #2 bytes
                ):
            return src_port.to_bytes(2) + \
                   dest_port.to_bytes(2) + \
                   seq.to_bytes(4) + \
                   ack.to_bytes(4) + \
                   if_ack.to_bytes(1) + \
                   syn.to_bytes(1) + \
                   window_size.to_bytes(2) + \
                   checksum.to_bytes(2) + \
                   urgent_pointer.to_bytes(2)
    


#will return a tuple - > (seq_number, ack_number, if_ack, syn, window_size)

def retrieve_header(header):
    return \
        int.from_bytes(header[4:8]),\
        int.from_bytes(header[8:12]),\
        int.from_bytes(header[12:13]),\
        int.from_bytes(header[13:14]),\
        int.from_bytes(header[14:16])


def time_ms():
    return int(time.perf_counter() * 1000)

MSS = 200
HEADER_SIZE = 20



def main():
    file_in = open("__INPUT.txt","wb")
    len_file = 6090 #this is to terminate after file tranfer
    # file_end = 0   # ideally it would be done through the 
                    # FIN flag in the header

    CONST_rwnd = 1000
    TIMEOUT = 500 #ms
    EST_STATE = False
    RECV_DATA = b''

    expected_seq = 0
    rwnd = CONST_rwnd


    clientSocket.settimeout(1)
    while True:
        #send/receive here
        if not EST_STATE:
            #connection establishment phase

            clientSocket.send(create_header(
                seq=9000,
                if_ack=0,
                syn=1,
                window_size = rwnd
            ))

            header = clientSocket.recv(HEADER_SIZE)
            seq,ack,if_ack,syn,window_size = retrieve_header(header)

            expected_seq = seq

            print("EST STATE : ",
            "SEQ:",seq,"ACK_NO:",ack,"ACK:",
            if_ack,"SYN:",syn,"WINDOW SIZE:",window_size)
            
            clientSocket.send(create_header(
                seq=9000,
                ack=0,
                if_ack=1,
                syn = 0,
                window_size=rwnd
            ))   

            EST_STATE = True
        else: 
            #data transfer phase
            seq,ack,data = 0,0,b''
            st_time = time_ms()
            while (time_ms() - st_time) < TIMEOUT:
                try:
                    #revieve data
                    seq,ack,if_ack,syn,window_size = \
                    retrieve_header(clientSocket.recv(HEADER_SIZE))
                    data=clientSocket.recv(MSS)
                    # RECV_DATA += data
                    file_in.write(data)

                    print("seq:",seq)
                    
                    rwnd -= MSS
                    expected_seq += MSS

                    #check recieve window
                    if rwnd < MSS:
                        break
                    
                except Exception as e:
                    continue


            #check if data transfer is over
            if expected_seq+MSS >= len_file:
                clientSocket.close()
                file_in.close()
                # print(RECV_DATA)
                break
            

            #randomly emptying the buuffer buffer -> application
            if rwnd < MSS:
                rwnd += rnd.randint(1,4) * MSS
                rwnd = min(rwnd,CONST_rwnd)


            #cummilitive acknowledgement
            clientSocket.send(create_header(
                seq=ack,
                ack=expected_seq + MSS,
                window_size=rwnd
            ))

    print("DATA RECIEVED")
            
            

if __name__ == "__main__":
    main()