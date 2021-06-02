import time

import dns.message
import dns.name
import dns.query
import dns.rdata
import dns.rdataclass
import dns.rdatatype
from dnslib import RR, QTYPE, A, AAAA
from dnslib.server import DNSServer, BaseResolver

ROOT_SERVERS = ("198.41.0.4",
                "199.9.14.201",
                "192.33.4.12",
                "199.7.91.13",
                "192.203.230.10",
                "192.5.5.241",
                "192.112.36.4",
                "198.97.190.53",
                "192.36.148.17",
                "192.58.128.30",
                "193.0.14.129",
                "199.7.83.42",
                "202.12.27.33",
)

cache = {}

def make_request(target, ip):
    query = dns.message.make_query(target, 255)
    response = dns.query.udp(query, ip)
    return response

def find(target):
    if target in cache:
        return cache[target]
    
    for server in ROOT_SERVERS:
        response = find_recursive(target, server)
        if(response):
            cache[target] = response
            return response
    return None


def find_recursive(target, ip):
    response = make_request(target, ip)
    if response:
        if response.answer:
            for answer in response.answer:
                if answer.rdtype == 5:
                    target = dns.name.from_text(str(answer[0]))
                    return find(target)
            return response
        elif response.additional:
            for additional in response.additional:
                if additional.rdtype != 1:
                    continue
                for add in additional:
                    new_response = find_recursive(target, str(add))
                    if new_response:
                        return new_response
    return None


class DNSResolver(BaseResolver):
    def resolve(self, request, handler):
        reply = request.reply()
        qname = str(request.q.qname)
        print(qname)
        result = find(dns.name.from_text(qname))
        if(result):
            for answers in result.answer:
                name = answers.name
                for answer in answers:
                    if answer.rdtype == 1:
                        reply.add_answer(RR(qname, rtype=answer.rdtype, rdata=A(str(answer))))
                    if answer.rdtype == 28:
                        reply.add_answer(RR(qname, rtype=answer.rdtype, rdata=AAAA(str(answer))))
        return reply


def main():
    server = DNSServer(DNSResolver(), address="localhost")
    server.start_thread()

    while(True):
        time.sleep(5)

if __name__ == "__main__":
    main()
