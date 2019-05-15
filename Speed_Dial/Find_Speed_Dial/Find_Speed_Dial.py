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

REGION = 'what cluster'
UDP = '%'
RMSD = '123456'
PHONE = 'SEP%'

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
def listudp(client, udp):
    return client.listDeviceProfile(**{
        'searchCriteria': {
            'name': udp,
        },
        'returnedTags': {
            'name': '',
        }
    })
def getudp(client, udp):
    return client.getDeviceProfile(name=udp)
def listphone(client, phone):
    return client.listPhone(**{
        'searchCriteria': {
            'name': phone,
        },
        'returnedTags': {
            'name': '',
            'devicePoolName': '',
            'phoneTemplateName': '',
            'protocol': ''
        }
    })
def getphone(client, name):
    return client.getPhone(name=name)


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
    udps = [udps['name'] for udps in listudp(axl,UDP)['return']['deviceProfile']]
    phones = [phones['name'] for phones in listphone(axl, PHONE)['return']['phone']]


    for udp in udps:
        if getudp(axl, udp)['return']['deviceProfile']['speeddials'] is None:
            pass
        else:
            sddirn = [sddirn['dirn'] for sddirn
                      in getudp(axl,udp)['return']['deviceProfile']['speeddials']['speeddial']]
            upddesc = getudp(axl, udp)['return']['deviceProfile']['description']
            for sd in sddirn:
                if sd == RMSD:
                    print('User Profile Name: ' + udp + ' with description ' + upddesc + ' has the speed dial ' + RMSD)

                else:
                    pass

    for phone in phones:
        if getphone(axl, phone)['return']['phone']['speeddials'] is None:
            pass
        else:
            sddirn = [sddirn['dirn'] for sddirn in getphone(axl, phone)['return']['phone']['speeddials']['speeddial']]
            phonedesc = getphone(axl, phone)['return']['phone']['description']
            for sd in sddirn:
                if sd == RMSD:
                    print('Phone Name: ' + phone + ' with description ' + phonedesc + ' has the speed dial ' + RMSD)
                    break
                else:
                    pass


if __name__ == '__main__':
    main()
