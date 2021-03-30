import dns.resolver

def resolveDNS():
    domain = "google.com"
    resolver = dns.resolver.Resolver(); 
    answer = resolver.query(domain , "A")
    return answer

resultDNS = resolveDNS()
answer = ''

for item in resultDNS:
    resultant_str = ','.join([str(item), answer])

print(resultant_str)