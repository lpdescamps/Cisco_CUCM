# -*- coding: utf-8 -*-

from zeep import Client
from zeep.cache import SqliteCache
from zeep.transports import Transport
from requests import Session
from requests.auth import HTTPBasicAuth
import urllib3
from urllib3.exceptions import InsecureRequestWarning
from cryptography.fernet import Fernet
from pathlib import Path

REGION = 'AO'


def file(path, platform, role):
    username = path / REGION / platform / ('user_' + role + '.txt')
    keyhash = path / REGION / platform / ('key_' + role + '.txt')
    hash = path / REGION / platform / ('hash_' + role + '.txt')

    return username, keyhash, hash
def crypto(keyhash, hash):
    with open(keyhash, 'rb') as file_key:
        for line_key in file_key:
            key = line_key
            cipher_suite = Fernet(key)
            with open(hash, 'rb') as file_hash:
                for line_hash in file_hash:
                    encryptedpwd = line_hash
                    uncipher_text = (cipher_suite.decrypt(encryptedpwd))
                    pwd = bytes(uncipher_text).decode("utf-8")
                    return pwd
def read(file):
    datalist = []
    for line in open(file):
        data = line.strip('\n')
        datalist.append(data)
    return datalist
def listUDP(client, udp):
    return client.listDeviceProfile(**{
        'searchCriteria': {
            'name': udp,
        },
        'returnedTags': {
            'name': ''
        }
    })
def listUser(client, user):
    return client.listUser(**{
        'searchCriteria': {
            'userid': user,
        },
        'returnedTags': {
            'userid': ''
        }
    })
def getUser(client, user):
    return client.getUser(userid=user)

def main():
    path = Path('C:\\shared\\API\\credentials')
    wsdl = 'file://C://shared//API//axlsqltoolkit//schema//11.5//AXLAPI.wsdl'
    platform = 'CUCM'
    role = 'r'
    urllib3.disable_warnings(InsecureRequestWarning)
    server = path / REGION / platform / ('fqdn' + '.txt')
    binding_name = '{http://www.cisco.com/AXLAPIService/}AXLAPIBinding'
    address = 'https://{fqdn}:8443/axl/'.format(fqdn=read(server)[0])
    session = Session()
    session.verify = False
    session.auth = HTTPBasicAuth(read(file(path,platform,role)[0])[0], crypto(file(path,platform,role)[1], file(path, platform, role)[2]))
    transport = Transport(cache=SqliteCache(), session=session, timeout=60)
    client = Client(wsdl=wsdl, transport=transport)
    axl = client.create_service(binding_name, address)

    users = [items['userid'] for items in listUser(axl, '%')['return']['user']]

    for user in users:
        udp_to_user = getUser(axl, user)['return']['user']['phoneProfiles']
        if udp_to_user is None:
            try:
                udp = [item['name'] for item in listUDP(axl, user)['return']['deviceProfile']][0]
                print('No UDP associated to End User ' + user + '. However, ' + udp + ' could be assigned to that user')
            except:
                print('No UDP associated to End User ' + user + '. The user has left or is on CIC (we could check TP)')
        else:
            pass
            #print('UDP: ' + udp_to_user['profileName'][0]['_value_1'] + ' is assigned to End User ' + user + '. No more action required')

if __name__ == '__main__':
    main()
