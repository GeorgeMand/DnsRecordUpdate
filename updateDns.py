import requests
import json
from CloudflareToken import token, zoneIdentifier, domainName

api_url = f"https://api.cloudflare.com/client/v4/zones/{zoneIdentifier}/dns_records"
verify_url = "https://api.cloudflare.com/client/v4/user/tokens/verify"
ip_url = "http://icanhazip.com"

ipResponse = requests.get(ip_url)
if (ipResponse.status_code != 200):
    print('External Ip URL unreachable')
    exit

external_ip = ipResponse.text

cloudflareHeaders = {
    "ContentType":"application/json",
    "Authorization":f"Bearer {token}"
}

verifyTokenResponse = requests.get(verify_url, headers=cloudflareHeaders)

if (verifyTokenResponse.status_code != 200):
    print('Invalid token')
    exit


#get DNS records
dnsRecordsResponse = requests.get(api_url, headers=cloudflareHeaders)
if (dnsRecordsResponse.status_code != 200):
    print('cannot get DNS records')
    exit

dnsRecords = dnsRecordsResponse.json()
cloudflareIp = ''
dnsRecordId = ''
print(dnsRecords)
for i in dnsRecords['result']:
    if i['type'] == 'A':
        cloudflareIp = i['content']
        dnsRecordId = i['id']
        break

if cloudflareIp != '' and dnsRecordId != '' and external_ip != cloudflareIp:
    update_dns_url = f"https://api.cloudflare.com/client/v4/zones/{zoneIdentifier}/dns_records/{dnsRecordId}"
    content = {
        'content':external_ip, 
        'type':'A',
        'proxied':True,
        'name':domainName,
        'comment':'updated via script',
        'ttl':1
        }
    updateRecordsResponse = requests.put(update_dns_url,json=content, headers=cloudflareHeaders)
    if updateRecordsResponse.status_code != 200:
        print('Cannot update A record')
