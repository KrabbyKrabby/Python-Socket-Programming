import socket
from dnslib.dns import *


SERVER_PORT   = ("192.168.0.5", 20001)
BUFFER          = 1024

def create_query(domain_name):
    query = DNSRecord.question(domain_name)
    return query.pack()

def parse_response(message):
    message = DNSRecord.parse(message)
    r_record = str(message.get_a()).split()
    response,TYPE = r_record[4],r_record[3]
    return response,TYPE


def resolve_dns(UDPClientSocket, dns_query):
    byte_encode = create_query(dns_query)

    #send to server
    UDPClientSocket.sendto(byte_encode, SERVER_PORT)

    #receieve from server
    message,address = UDPClientSocket.recvfrom(BUFFER)

    response,res_type = parse_response(message)

    if res_type == "A" or res_type == "AAAA":
        return response
    else:
        print(response, "<<< REDIRECTING")
        return resolve_dns(UDPClientSocket, response)


def main():
    UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    while True:
        dns_query = input("Enter DNS query: ")
        ip_address = resolve_dns(UDPClientSocket, dns_query)
        print("IP address:", ip_address)

if __name__ == "__main__":
    main()