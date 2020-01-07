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
import itertools

REGION = 'eo'
CSS = 'acsbc'

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

def combination(string):
    s = string
    cases = map(''.join, itertools.product(*zip(s.upper(), s.lower())))
    case = ["%" + str(case) + "%" for case in cases]

    return case

def listCSS(client, item):
    result = client.listCss(**{
        'searchCriteria': {
            'name': item,
        },
        'returnedTags': {
            'name': ''
        }
    })

    if result['return']:
        name = [field['name'] for field in result['return']['css']]
        return name
    else:
        pass
def getCSS(client, item):
    return client.getCss(name=item)

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

    for css_comb in combination(CSS):
        if listCSS(axl, css_comb):
            for css in listCSS(axl, css_comb):
                print(css + "= " + getCSS(axl,css)['return']['css']['clause'])


if __name__ == '__main__':
    main()