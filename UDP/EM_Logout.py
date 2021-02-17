# -*- coding: utf-8 -*-
from collections import OrderedDict
from zeep import Client
from zeep.cache import SqliteCache
from zeep.transports import Transport
from zeep.helpers import serialize_object
from requests import Session
from requests.auth import HTTPBasicAuth
import urllib3
from urllib3.exceptions import InsecureRequestWarning
from cryptography.fernet import Fernet
from pathlib import Path
import time

REGION = 'eo'
UDP = '%'
FILE = 'C://local//EMloggedin_' + time.strftime("%Y%m%d-%H%M%S") + '.csv'


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

def listUDP(client, udpname):

    return client.listDeviceProfile(**{
        'searchCriteria': {
        'name': udpname
    },
        'returnedTags': {
            'name': '',
            'phoneTemplateName': '',
            'protocol': ''
        }
    })
def sql_get_em_items(service, udp):
    sql_statement = \
        "SELECT " \
            "D2.name phone, " \
            "E.userid " \
        "FROM " \
            "device D1 " \
        "JOIN extensionmobilitydynamic EMD " \
            "ON EMD.fkdevice_currentloginprofile = D1.pkid " \
        "JOIN device D2 " \
            "ON D2.pkid = EMD.fkdevice " \
        "JOIN enduser E " \
            "ON E.pkid = EMD.fkEnduser " \
        "WHERE D1.name = '"+udp+"'"
    axl_resp = service.executeSQLQuery(sql=sql_statement)
    return [OrderedDict((element.tag, element.text) for element in row) for row in serialize_object(axl_resp)["return"]["row"]]
def em_logout(client, phone):
    print('logging out')
    return client.doDeviceLogout(**{
        'deviceName': phone
     })
def em_login(client, udp, phone, userid):
    print('logging in')
    return client.doDeviceLogin(**{
        'deviceName': phone,
        'loginDuration': '0',
        'profileName': udp,
        'userId': userid
     })

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
    session.auth = HTTPBasicAuth(read(file(path,platform,role)[0])[0], crypto(file(path,platform,role)[1], file(path, platform, role)[2]))
    transport = Transport(cache=SqliteCache(), session=session, timeout=60)
    client = Client(wsdl=wsdl, transport=transport)
    axl = client.create_service(binding_name, address)
    f = open(FILE, 'w')
    f.write('Phone')
    f.write(',')
    f.write('UserID')
    f.write('\n')


    #Search logged in user and log them out
    for udpitem in listUDP(axl, UDP)['return']['deviceProfile']:
            try:
                for em_items in sql_get_em_items(axl, udpitem['name']):
                    print(em_items['phone'])
                    print(em_items['userid'])
                    f = open(FILE, 'a')
                    f.write(str(em_items['phone']))
                    f.write(',')
                    f.write(str(em_items['userid']))
                    f.write('\n')
                    #em_logout(axl, em_items['phone'])
                    #em_login(axl, udpitem['name'], em_items['phone'], em_items['userid'])
                    print('#####The End#########The End#########The End#########The End####')
            except TypeError:
                pass


if __name__ == '__main__':
    main()