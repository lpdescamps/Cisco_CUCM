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

REGION = 'eo'
CSS = 'EO_TP_ACSBC-css'
PT = 'EO_TP_ACSBC-pt'
FILE = r"C:\shared\ac\py\pilot_TP_20191210_dirty2.csv"
USERPT = 'EU_Internal'

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

    dn = [row['DN'] for row in csv.DictReader(open(file))]
    name = [row['Name'] for row in csv.DictReader(open(file))]

    print(dn, name)

def rmTP(client, pattern, pt):
    try:
        print("Removing TP for {}".format(pattern))
        return client.removeTransPattern(**{
            'pattern': pattern,
            'routePartitionName': pt,
        })
    except exceptions.Fault:
        print("!!!!!!!!TP doesn't exists for {}".format(pattern))

def updateLine(client, pattern, pt):
    try:

        return client.updateLine(**{
            'pattern': pattern,
            'routePartitionName': pt,
            'callForwardNotRegistered': {'forwardToVoiceMail': 'true'},
            'callForwardNotRegisteredInt': {'forwardToVoiceMail': 'true'}
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

    for row in csv.DictReader(open(FILE, encoding="utf-8-sig")):
        ddi = row['DN'].replace(" ", "")
        print(row)
        rmTP(axl, ddi, PT)
        updateLine(axl, ddi, USERPT)


if __name__ == '__main__':
    main()