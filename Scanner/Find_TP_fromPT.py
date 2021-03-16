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
from zeep import exceptions
import csv
import time

REGION = 'eo'
PTLEG = 'EU_Internal'
PTCIC = 'EO_TP_GEN-pt'
FILE = 'C://local//tp_' + time.strftime("%Y%m%d-%H%M%S") + '.csv'

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
def read(item):
    datalist = []
    for line in open(item):
        data = line.strip('\n')
        datalist.append(data)
    return datalist

def readCSV(file):

    dn = [row['DN'] for row in csv.DictReader(open(file, encoding="utf-8-sig"))]
    name = [row['Name'] for row in csv.DictReader(open(file, encoding="utf-8-sig"))]

    print(dn, name)

def listTransPattern(client, pt):
    return client.listTransPattern(**{
        'searchCriteria': {
            'routePartitionName': pt,
        },
        'returnedTags': {
            'pattern': '',
            'description': '',
            'calledPartyTransformationMask': '',
            'callingPartyTransformationMask': '',
            'callingPartyPrefixDigits': '',
            'prefixDigitsOut': '',
            'routePartitionName': '',
            'callingSearchSpaceName': ''
        }
    })

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
    session.auth = HTTPBasicAuth(read(file(path, platform, role)[0])[0], crypto(file(path, platform, role)[1], file(path, platform, role)[2]))
    transport = Transport(cache=SqliteCache(), session=session, timeout=60)
    client = Client(wsdl=wsdl, transport=transport)
    axl = client.create_service(binding_name, address)
    f = open(FILE, 'w')
    f.write('Type')
    f.write(', ')
    f.write('Pattern')
    f.write(', ')
    f.write('Partition')
    f.write(', ')
    f.write('CSS')
    f.write(', ')
    f.write('Description')
    f.write(', ')
    f.write('CalledX')
    f.write(', ')
    f.write('CalledPrefix')
    f.write(', ')
    f.write('CallingX')
    f.write(', ')
    f.write('CallingPrefix')
    f.write('\n')

    #print(listTransPattern(axl,PTLEG))

    raws = listTransPattern(axl,PTLEG)['return']['transPattern']
    #raws = listTransPattern(axl, PTCIC)['return']['transPattern']


    for raw in raws:
        print('DN: ' + (str(raw['pattern'])))
        print('Partition: ' + (str(raw['routePartitionName']['_value_1'])))
        print('CSS: ' + (str(raw['callingSearchSpaceName']['_value_1'])))
        print('Description: ' + (str(raw['description'])))
        print('CalledX: ' + (str(raw['calledPartyTransformationMask'])))
        print('CalledPrefix: ' + (str(raw['prefixDigitsOut'])))
        print('CallingX: ' + (str(raw['callingPartyTransformationMask'])))
        print('CallingPrefix: ' + (str(raw['callingPartyPrefixDigits'])))
        print("\n######\n")

        f = open(FILE, 'a')
        f.write('TranslationPattern')
        f.write(', ')
        f.write(str(raw['pattern']))
        f.write(', ')
        f.write(str(raw['routePartitionName']['_value_1']))
        f.write(', ')
        f.write(str(raw['callingSearchSpaceName']['_value_1']))
        f.write(', ')
        f.write(str(raw['description']))
        f.write(', ')
        f.write(str(raw['calledPartyTransformationMask']))
        f.write(', ')
        f.write(str(raw['prefixDigitsOut']))
        f.write(', ')
        f.write(str(raw['callingPartyTransformationMask']))
        f.write(', ')
        f.write(str(raw['callingPartyPrefixDigits']))
        f.write('\n')
        f.close()



if __name__ == '__main__':
    main()