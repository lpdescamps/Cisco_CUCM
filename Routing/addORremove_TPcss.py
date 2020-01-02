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
from collections import OrderedDict
from zeep.helpers import serialize_object
import unicodedata
from zeep import exceptions

REGION = 'eo'
CSS = '%_Trunk_Inbound_SIP'
PT = 'EO_TP_ACSBC-pt'

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

def listCSS(client, item):
    return client.listCss(**{
        'searchCriteria': {
            'name': item,
        },
        'returnedTags': {
            'name': ''
        }
    })
def getCSS(client, item):
    return client.getCss(name=item)
def addptCSS(client, css, pt, index):
    try:
        return client.updateCss(**{
        'name': css,
        'addMembers': {
            'member': {
                'routePartitionName': pt,
                'index': index
            }
        }})
    except exceptions.Fault:
        print('!!!!!!!!partition {} already assigned to css {}'.format(pt,css))
def rmptCSS(client, css, pt, index):
    try:
        return client.updateCss(**{
        'name': css,
        'removeMembers': {
            'member': {
                'routePartitionName': pt,
                'index': index
            }
        }})
    except exceptions.Fault:
        print('!!!!!!!!partition {} is not assigned to css {}'.format(pt,css))

def main():
    path = Path('C:\\shared\\API\\credentials')
    wsdl = 'file://C://shared//API//axlsqltoolkit//schema//11.5//AXLAPI.wsdl'
    platform = 'CUCM'
    role = 'rwx'
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

    for items in listCSS(axl,CSS)['return']['css']:
        print('\n####################Before adding the partition')
        print(getCSS(axl,items['name'])['return']['css']['name'])
        print(getCSS(axl,items['name'])['return']['css']['clause'])
        print('Adding the partition {}'.format(PT))
        #addptCSS(axl, items['name'], PT, '0')
        #rmptCSS(axl, items['name'], PT, '0')
        print('********************After adding the partition {}'.format(PT))
        print(getCSS(axl,items['name'])['return']['css']['name'])
        print(getCSS(axl,items['name'])['return']['css']['clause'])


if __name__ == '__main__':
    main()