import socket
import threading
from dnslib.dns import *
import random

IP     = "192.168.0.5"
PORT   = 20001
BUFFER  = 1024
THREAD_NO = 0

DNS_RECORDS = {}

def get_queryType(qtype,value):
    if qtype == 'A':
        return QTYPE.A,A(value)
    if qtype == 'AAAA':
        return QTYPE.AAAA,AAAA(value)
    if qtype == 'MX':
        return QTYPE.MX,MX(value)
    if qtype == 'CNAME':
        return QTYPE.CNAME,CNAME(value)
    if qtype == 'NS':
        return QTYPE.NS,NS(value)


def create_response(domain_name,r_record):
    qtype,value = get_queryType(r_record[1],r_record[0])
    return DNSRecord(
        DNSHeader(qr=1,aa=1,ra=0),
        q=DNSQuestion(domain_name),
        a=RR(domain_name,qtype,rdata=value,ttl=int(r_record[2]))
    ).pack()


def parse_query(message):
    domain_name = str(message.get_q()).strip(';').split()[0]
    record_list = []
    try:
        record_list = DNS_RECORDS[domain_name]
    except Exception as e:
        return "SYS_EXIT"

    return domain_name,record_list


def server_start(UDPServerSocket):  
    while(True):
        #receiving from client
        message,address = UDPServerSocket.recvfrom(BUFFER)
        print("\n\nRECEIVED DATA(BYTEARRAY)\n____________________\nBYTEARRY : ",message)
        message = DNSRecord.parse(message)

        print("\n\nRECEIVED QUERY(PARSED)\n____________________\nBYTEARRY : ",message)

        domain_name,record_list = parse_query(message)

        if record_list == "SYS_EXIT":
            UDPServerSocket.sendto("Incorrect Query".encode(),address)
            
    
        resource_record = record_list[random.randrange(max(1,len(record_list) - 1))]
        response = create_response(domain_name,resource_record)
        UDPServerSocket.sendto(response,address)


def main():
    #load dns records to list
    
    file_in = open("dns_records.txt","r")
    lines = file_in.readlines()
    for record in lines:
        temp = record.split()
        DNS_RECORDS[temp[0]] = []

    for record in lines:
        temp = record.split()
        DNS_RECORDS[temp[0]].append((temp[1],temp[2],temp[3]))


    print("STARTING SERVER")
    UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    UDPServerSocket.bind((IP, PORT))
    print("SERVER IS LISTENING : ")
    while True:
        server_thread = threading.Thread(target=server_start(UDPServerSocket,))
        server_thread.start()


if __name__ == "__main__":
    main()