import socket
from dnslib.dns import *


SERVER_PORT   = ("192.168.0.5", 20001)
BUFFER          = 1024

def create_query(domain_name):
    # print("\n\nQUERY (FORMATTED)\n____________________\nBYTEARRY : ",DNSRecord.question(domain_name))
    # print("\n\nBYTEARRY\n____________________\n",DNSRecord.question(domain_name).pack())
    return DNSRecord.question(domain_name).pack()

def parse_response(message):
    message = DNSRecord.parse(message)
    r_record = str(message.get_a()).split()
    response,TYPE = r_record[4],r_record[3]
    return response,TYPE


def send_request(UDPClientSocket):
    while True:
        dns_query       = input("Enter DNS query : ")
        byte_encode     = create_query(dns_query)
        flag = False
        while not flag:
            #send to server
            UDPClientSocket.sendto(byte_encode, SERVER_PORT)

            #receieve from server
            message,address = UDPClientSocket.recvfrom(BUFFER)


            # print("\n\nRECEIVED MESSAGE\n____________________\nBYTEARRY : ",message)
            # print("\n\nPARSED MESSAGE\n____________________\n",DNSRecord.parse(message))
            

            response,res_type = parse_response(message)
            

            if res_type == "A" or res_type == "AAAA":
                print("IP ADDRESS >> ",response)
                flag = True
            else:

                print(response," <<< REDIRECTING")


                byte_encode = create_query(response)
                
def main():
    UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    send_request(UDPClientSocket)

if __name__ == "__main__":
    main()