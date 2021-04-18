
import binascii
from os import name
import socket
import sys
from collections import OrderedDict, namedtuple
import csv
import pandas as pd
import json

from pandas.io.stata import PossiblePrecisionLoss

def build_message(type, address):
    ID = 65535
    QR = 0
    OPCODE = 0
    AA = 0
    TC = 0
    RD = 1
    RA = 0
    Z = 0 
    RCODE = 0

    query_params = str(QR)
    query_params += str(OPCODE).zfill(4)
    query_params += str(AA) + str(TC) + str(RD) + str(RA)
    query_params += str(Z).zfill(3)
    query_params += str(RCODE).zfill(4)
    query_params = "{:04x}".format(int(query_params, 2))

    QDCOUNT = 1
    ANCOUNT = 0
    NSCOUNT = 0
    ARCOUNT = 0

    message = ""
    message += "{:04x}".format(ID)
    message += query_params
    message += "{:04x}".format(QDCOUNT)
    message += "{:04x}".format(ANCOUNT)
    message += "{:04x}".format(NSCOUNT)
    message += "{:04x}".format(ARCOUNT)

    addr_parts = address.split(".")
    for part in addr_parts:
        addr_len = "{:02x}".format(len(part))
        addr_part = binascii.hexlify(part.encode())
        message += addr_len
        message += addr_part.decode()

    message += "00"

    QTYPE = get_type(type)
    message += QTYPE

    QCLASS = 1
    message += "{:04x}".format(QCLASS)

    return message


def decode_message(message):    
    res = []

    QDCOUNT = message[8:12]
    ANCOUNT = message[12:16]  
    NSCOUNT = message[16:20]
    ARCOUNT = message[20:24]


    # Question section
    QUESTION_SECTION_STARTS = 24
    question_parts = parse_parts(message, QUESTION_SECTION_STARTS, [])
    

    QTYPE_STARTS = QUESTION_SECTION_STARTS + (len("".join(question_parts))) + (len(question_parts) * 2) + 2
    QCLASS_STARTS = QTYPE_STARTS + 4


    # Answer section
    ANSWER_SECTION_STARTS = QCLASS_STARTS + 4
    respo = []
    NUM_ANSWERS = max([int(ANCOUNT, 16), int(NSCOUNT, 16), int(ARCOUNT, 16)])
    if NUM_ANSWERS > 0:
        
        for ANSWER_COUNT in range(NUM_ANSWERS):
            if (ANSWER_SECTION_STARTS < len(message)):
                ANAME = message[ANSWER_SECTION_STARTS:ANSWER_SECTION_STARTS + 4]
                ATYPE = message[ANSWER_SECTION_STARTS + 4:ANSWER_SECTION_STARTS + 8]
                ACLASS = message[ANSWER_SECTION_STARTS + 8:ANSWER_SECTION_STARTS + 12]
                TTL = int(message[ANSWER_SECTION_STARTS + 12:ANSWER_SECTION_STARTS + 20], 16)
                RDLENGTH = int(message[ANSWER_SECTION_STARTS + 20:ANSWER_SECTION_STARTS + 24], 16)
                RDDATA = message[ANSWER_SECTION_STARTS + 24:ANSWER_SECTION_STARTS + 24 + (RDLENGTH * 2)]

                if ATYPE == get_type("A"):
                    octets = [RDDATA[i:i+2] for i in range(0, len(RDDATA), 2)]
                    RDDATA_decoded = ".".join(list(map(lambda x: str(int(x, 16)), octets)))
                else:
                    RDDATA_decoded = ".".join(map(lambda p: binascii.unhexlify(p).decode('iso8859-1'), parse_parts(RDDATA, 0, [])))
                    
                ANSWER_SECTION_STARTS = ANSWER_SECTION_STARTS + 24 + (RDLENGTH * 2)

            try: ATYPE
            except NameError: None
            else:  
                respo.extend([str(ANSWER_COUNT + 1), str(int(QDCOUNT, 16)), str(int(ANCOUNT, 16)), str(int(NSCOUNT, 16)), str(int(ARCOUNT, 16)),
                                ANAME, ATYPE + " (\"" + get_type(int(ATYPE, 16)) + "\")", ACLASS, str(TTL), str(RDLENGTH), RDDATA, RDDATA_decoded])
                
    return "\n".join(res), respo


def send_udp_message(message, address, port):

    message = message.replace(" ", "").replace("\n", "")
    server_address = (address, port)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.sendto(binascii.unhexlify(message), server_address)
        data, _ = sock.recvfrom(4096)
    finally:
        sock.close()
    return binascii.hexlify(data).decode("utf-8")


def get_type(type):
    types = [
        "ERROR", "A", "NS", "MD", "MF", "CNAME", "SOA", "MB", "MG", "MR", "NULL", "WKS", "PTS", "HINFO", "MINFO", "MX", "TXT"]
    try:
        return "{:04x}".format(types.index(type)) if isinstance(type, str) else types[type]
    except ValueError:
        print("Enter valid type!")
        sys.exit()

def parse_parts(message, start, parts):
    part_start = start + 2
    part_len = message[start:part_start]
    
    if len(part_len) == 0:
        return parts
    
    part_end = part_start + (int(part_len, 16) * 2)
    parts.append(message[part_start:part_end])

    if message[part_end:part_end + 2] == "00" or part_end > len(message):
        return parts
    else:
        return parse_parts(message, part_end, parts)

if __name__ == "__main__":

    while True:
        choose = input("Please enter 1 to enter your name address and 2 for exit: ")
        if choose == "1":
            jsonArray = []
            name_address = input("Enter name address: ")
            with open('cache.csv', encoding='utf-8') as csvf: 
                csvReader = csv.DictReader(csvf) 
                cind = 0
                for row in csvReader: 
                    jsonArray.append(row)
                    cind += 1
            find = 0
            for i in jsonArray:

                if i['name address'] == name_address:
                    find = 1

                    if int(i['count']) >= 3:
                        print('Use cache!')
                        print(f"ip is: {i['ip']}")

                    else:
                        message = build_message("A", name_address) 
                        response = send_udp_message(message, "1.1.1.1", 53)
                        respo = decode_message(response)[1]
                        for j in range(int(len(respo) / 12)):
                            ip = respo[j * 12 + 11]
                        print(f'ip is (in cache): {ip}')
                        num = int(i['count']) + 1
                        i['count'] = str(num)

                    df = pd.read_json(json.dumps(jsonArray))
                    df.to_csv('cache.csv', index=False)

            if find == 0:
                csvf.close()
                message = build_message("A", name_address) 
                response = send_udp_message(message, "1.1.1.1", 53)
                respo = decode_message(response)[1]
                for j in range(int(len(respo) / 12)):
                    ip = respo[j * 12 + 11]
                print(f'ip with request: {ip}')
                with open('cache.csv', 'a') as cache_file:
                    writer1 = csv.writer(cache_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                    writer1.writerow([name_address, ip, 1])

        elif choose == "2":
            print("Bye!")
            exit()
        else:
            print(f"Enter 1 or 2 not {choose}")
