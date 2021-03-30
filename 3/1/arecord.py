import dns.resolver

def resolveDNS():
    domain = "google.com"
    resolver = dns.resolver.Resolver(); 
    answer = resolver.query(domain , "A")
    return answer


if __name__ == "__main__":
    resultDNS = resolveDNS()
    answer = ''
    for item in resultDNS:
        resultant_str = ','.join([str(item), answer])
    print('-')
    print(resultant_str)
    print('-')
