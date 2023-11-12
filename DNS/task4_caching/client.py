import socket
import time
from dnslib.dns import *



SERVER_PORT   = ("192.168.0.5", 20001)
BUFFER          = 1024

DNS_CACHE = {}


def create_query(domain_name):
    query = DNSRecord.question(domain_name)
    return query.pack()

def parse_response(message):
    message = DNSRecord.parse(message)
    r_record = str(message.get_a()).split()
    response,TYPE,ttl_ms = r_record[4],r_record[3],r_record[1]
    return response,TYPE,ttl_ms


def resolve_dns(UDPClientSocket, dns_query):
    byte_encode = create_query(dns_query)

    #send to server
    UDPClientSocket.sendto(byte_encode, SERVER_PORT)

    #receieve from server
    message,address = UDPClientSocket.recvfrom(BUFFER)

    response,res_type,ttl_ms = parse_response(message)


    init_time = int(time.perf_counter())
    if res_type == "A" or res_type == "AAAA":
        DNS_CACHE[dns_query] = (response,res_type,int(ttl_ms),init_time) 
        return response
    else:
        print(response, "<<< REDIRECTING")
        return resolve_dns(UDPClientSocket, response)


def handle_caches():
    for key in DNS_CACHE:
        if DNS_CACHE[key] == "DELETED":
            continue
        
        cur_time = int(time.perf_counter())
        elapsed_time = (cur_time - int(DNS_CACHE[key][3]))*1000
        if elapsed_time > DNS_CACHE[key][2]:
            
            DNS_CACHE[key] = "DELETED"

def main():
    UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    while True:

        handle_caches()

        dns_query = input("Enter DNS query(ENTER 'CACHE' TO VIEW CACHED DATA): ")
        

        if dns_query == 'CACHE':
            print("\nCACHE DATA\n__________________\n")
            for key in DNS_CACHE:
                print(key, " >>>> ",DNS_CACHE[key])
            print("___________________\n")    
            continue
        
        ip_address = ""

        try:
            ip_address = DNS_CACHE[dns_query]
            if ip_address == "DELETED":
                raise Exception
        except Exception as e:
            ip_address = resolve_dns(UDPClientSocket,dns_query)
        print("IP address:", ip_address)

if __name__ == "__main__":
    main()