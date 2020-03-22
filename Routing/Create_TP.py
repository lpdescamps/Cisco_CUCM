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
from time import sleep

REGION = 'eu'
CSS = 'eu_TP_ACSBC-css'
PT = 'eu_TP_ACSBC-pt'
FILE = r"C:\shared\ac\py\lidt.csv"
USERPT = 'AU_INTERNAL_pt'

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
def addTP(client, dn, desc, pt, css):
    try:
        client.addTransPattern(transPattern=
            {
            'pattern': dn,
            'description': desc,
            'usage': 'Translation',
            'routePartitionName': pt,
            'callingSearchSpaceName': css,
            'provideOutsideDialtone': 'true',
            'patternUrgency': 'true'
        })

    except exceptions.Fault:
        print('!!!!!!!!TP {} already exists for {}'.format(dn, desc))

def getcss(client, item, pt):

     try:
        result = client.getLine(pattern=item, routePartitionName=pt)['return']['line']

        thedict = {
            'call1st': result['callForwardAll']['callingSearchSpaceName']['_value_1'],
            'call2nd': result['callForwardAll']['secondaryCallingSearchSpaceName']['_value_1'],
            'cfur': result['callForwardNotRegistered']['callingSearchSpaceName']['_value_1'],
            'cfurint': result['callForwardNotRegisteredInt']['callingSearchSpaceName']['_value_1']

        }

        return thedict

     except:
         print('getcss failed')
         pass

def updateLine(client, pattern, pt, call1st, call2nd, cfur, cfurint):
    try:
        return client.updateLine(**{
            'pattern': pattern,
            'routePartitionName': pt,
            'callForwardAll': {'forwardToVoiceMail': 'false', 'callingSearchSpaceName': call1st, 'secondaryCallingSearchSpaceName': call2nd, 'destination': ''},
            'callForwardNotRegistered': {'forwardToVoiceMail': 'false', 'callingSearchSpaceName': cfur, 'destination': ''},
            'callForwardNotRegisteredInt': {'forwardToVoiceMail': 'false', 'callingSearchSpaceName': cfurint, 'destination': ''}
        })
    except exceptions.Fault:
        print("!!!!!!!!DN doesn't exists for {}".format(pattern))

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
    wait = 1

    # for row in csv.DictReader(open(FILE, encoding="utf-8-sig")):
    for row in csv.DictReader(open(FILE)):

        ddi = row['DN'].replace(" ", "")
        print(row)
        print("DN: " + ddi + " Name:", row['Name'])
        addTP(axl, ddi, row['Name'] + "_MT", PT, CSS)
        print("DN: " + ddi)
        fcss = getcss(axl, ddi, USERPT)

        try:
            updateLine(axl, ddi, USERPT, fcss['call1st'], fcss['call2nd'], fcss['cfur'], fcss['cfurint'])
        except:
            print('updateLine failed')
            pass
        print("One more Gin&Tonic for Louis! wait for {} seconds".format(wait))
        sleep(wait)

if __name__ == '__main__':
    main()