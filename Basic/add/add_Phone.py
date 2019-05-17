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
from lxml import etree as ET

REGION = 'what cluster'
NAME = 'SEPC67C4EB65F92'
MODEL = 'Cisco 8845'
DP = 'Default'
CPP = 'Standard Common Phone Profile'
LOC = 'Hub_None'
UTRP = 'Default'
PTN = 'Standard 8845 SIP'
PPN = ''
BIBS = 'Default'
PCM = 'None'
CO = 'No Pending Operation'
DMM = 'Default'
DN = '96943'
DNPT = ''

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


def addPhone(client, name, model, dp, cpp, loc, utrp, ptn, ppn, bibs, pcm, co, dmm, dn, dnpt):
    xmlstring = '<items>' \
            '<webAccess>2</webAccess>' \
            '</items>'
    tree = ET.fromstring(xmlstring)

    client.addPhone(phone=
        {
        'name': name,
        'product': model,
        'class': 'Phone',
        'protocol': 'SIP',
        'protocolSide': 'User',
        'devicePoolName': dp,
        'commonPhoneConfigName': cpp,
        'locationName': loc,
        'useTrustedRelayPoint': utrp,
        'phoneTemplateName': ptn,
        'primaryPhoneName': ppn,
        'builtInBridgeStatus': bibs,
        'packetCaptureMode': pcm,
        'certificateOperation': co,
        'deviceMobilityMode': dmm,
        'lines': {
            'line':
            [
            {
            'index': '1',
            'dirn': {
                'pattern': dn,
                'routePartitionName': dnpt
                },
            'callInfoDisplay': {
                'callerName': 'true',
                'callerNumber': 'false',
                'redirectedNumber': 'false',
                'dialedNumber': 'true'
                }

            }
            ],
        },
        'vendorConfig': tree
    })

def main():
    path = Path('C:\\shared\\API\\credentials')
    wsdl = 'file://C://shared//API//axlsqltoolkit//schema//11.5//AXLAPI.wsdl'
    platform = 'CUCM_DEV'
    role = 'rwx'
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

    addPhone(axl,NAME, MODEL, DP, CPP, LOC, UTRP, PTN, PPN, BIBS, PCM, CO, DMM, DN, DNPT)


if __name__ == '__main__':
    main()
