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
    e = str(e)
    print(">>>>>",e)

res = clientSocket.recv(1024)
#print(res.decode())

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
CONST_rwnd = 1000


def main():
    file_in = open("__INPUT.txt","wb")
    len_file = 6190 #this is to terminate after file tranfer
    file_end = 0   # ideally it would be done through the 
                    # FIN flag in the header

    EST_STATE = False
    RECV_DATA,buffer_len,data = b'',0,b''
    
    expected_seq = 0
    rwnd = CONST_rwnd
    seq_rec = 0
    ack_toSend = 0
    clientSocket.settimeout(0.1)

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

            expected_seq = 0

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
            try:
                seq_rec,ack,if_ack,syn,window_size = retrieve_header(clientSocket.recv(HEADER_SIZE))
                data = clientSocket.recv(MSS)
                ack_toSend = seq_rec
                
                
                print("SEQ:",seq_rec,"EXP SEQ:",expected_seq,
                      "File Len:",file_end,"buffer_len:",buffer_len)

                if file_end >= len_file:
                    # RECV_DATA += data
                    break

            except Exception as e:

                if file_end >= len_file:
                    # RECV_DATA += data
                    print("END OF FILE")
                    break


                rwnd = CONST_rwnd - buffer_len
                clientSocket.sendall(create_header(
                     ack=expected_seq,
                     if_ack=1,
                     window_size=rwnd
                )) 

                print(">>>>>",str(e))

        
            if seq_rec == expected_seq:
                # RECV_DATA  += data
                file_in.write(data)
                file_end += MSS

                ack_toSend += MSS
                expected_seq += MSS

                buffer_len += len(data)

                #empty buffer
                if buffer_len >= CONST_rwnd:
                    buffer_len = 0
                    print("Cummilitive ACK")
                    try:
                        clientSocket.sendall(create_header(
                            ack=ack_toSend+MSS,
                            if_ack=1,
                            window_size=rwnd
                        ))
                    except Exception as e:
                        continue
            elif rnd.randint(0,1) == 0:
                for i in range(3):
                    clientSocket.sendall(create_header(
                        ack=expected_seq+MSS,
                        if_ack=1,
                        window_size=rwnd
                    ))

    # clientSocket.close()

    file_in.close()
    # print(RECV_DATA)   
    # print(all_data)              
    print("DATA RECIEVED")
            
            

if __name__ == "__main__":
    main()