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
from zeep import exceptions
import unicodedata
import csv

REGION = 'EO'
FILE = r"C:\shared\ac\cucm\py\colt_udp.csv"


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

def readCSV(csvfile):

    with open(FILE, 'r') as csvfile_header:
        reader = csv.reader(csvfile_header)
        headers = next(reader, None)

    csvdict = dict()

    for key in headers:
        csvdict[key] = [row[key] for row in csv.DictReader(open(csvfile, encoding="utf-8-sig"))]

    thedict = [{key: csvdict[key][value] for key in [key for key in csvdict]} for value in range(len(csvdict[headers[0]]))]

    return thedict

def getUser(client, user):
    return client.getUser(userid=user)
def delLine(client, dirn, dnpt):

    try:
        print("Deleting DN for {}".format(dirn))

        return client.removeLine(**{
        'pattern': dirn,
        'routePartitionName': dnpt
        })

    except exceptions.Fault:
        print("!!!!!!!!DN {} doesn't exists".format(dirn))
def addLine(client, dirn, desc, use, dnpt, llabel):

    try:
        print("Creating base DN for {} in pt {}".format(dirn, dnpt))
        client.addLine(line=
                        {
                            'pattern': dirn,
                            'description': desc,
                            'usage': use,
                            'routePartitionName': dnpt,
                            'alertingName': llabel,
                            'asciiAlertingName': llabel
                        }
                        )

    except exceptions.Fault:
        print('!!!!!!!!DN {} already exists'.format(dirn))
def addUDP(client, udp, model, desc, ptn, local, dirn, dnpt, llabel, ldisplay):

    try:
        print("Creating UDP for {}".format(desc))
        client.addDeviceProfile(deviceProfile=
            {
            'name': udp,
            'product': model,
            'description': desc,
            'class': 'Device Profile',
            'protocol': 'SIP',
            'protocolSide': 'User',
            'phoneTemplateName': ptn,
            'userLocale': local,
            'softkeyTemplateName': 'QBE Standard User',
            'services': {
                'service':
                    [
                        {
                            'telecasterServiceName': 'Service Desk',
                            'name': 'Service Desk',
                            'urlButtonIndex': '1',
                            'urlLabel': 'Service Desk',
                            'serviceNameAscii': 'Service Desk',
                        },
                        {
                            'telecasterServiceName': 'Extension Mobility Logout',
                            'name': 'Extension Mobility Logout',
                            'urlButtonIndex': '2',
                            'urlLabel': 'Extension Mobility Logout',
                            'serviceNameAscii': 'Extension Mobility Logout',
                        }
                    ],
            },
            'lines': {
                'line': [
                    {
                        'index': 1,
                        'label': llabel,
                        'display': ldisplay,
                        'displayAscii': ldisplay,
                        'dirn': {
                            'pattern': dirn,
                            'routePartitionName': {
                                '_value_1': dnpt,
                            },
                        },
                    }
                ],
            },
        })

    except exceptions.Fault:
        print('!!!!!!!!UDP {} already exists'.format(udp))
def sql_getlocale(service):

    sql_statement = \
        "SELECT " \
            "name, languagelocalecode " \
        "FROM " \
            "typeuserlocale "
    axl_resp = service.executeSQLQuery(sql=sql_statement)
    table = [OrderedDict((element.tag, element.text) for element in row) for row in
            serialize_object(axl_resp)["return"]["row"]]
    locale = [(items['name'], items['languagelocalecode'].split('_')[1]) for items in table]

    dict_variable = {languagelocalecode: name for (name, languagelocalecode) in locale}

    return dict_variable
def mylocale(client):
    return sql_getlocale(client)
def updateUser(client, user, local, *args):

    try:
        print("Updating End User {}".format(user))
        return client.updateUser(**{
        'userid': user,
        'userLocale': local,
        'phoneProfiles': {
            'profileName':
                args[0]
            }
        })

    except exceptions.Fault:
        print('!!!!!!!!USER {} not found'.format(user))
def myvariables(client, userid, ):
    try:
        udplist = [items['_value_1'] for items in getUser(client, userid)['return']['user']['phoneProfiles']['profileName']]
    except:
        udplist = 'no_udplist'

    myvariables_dict = {
        'udplist': udplist,
    }

    return myvariables_dict



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

    language = mylocale(axl)

    for para in readCSV(FILE):
        udplist = myvariables(axl, para['user'])
        udplist['udplist'].append(para['udp'])

        delLine(axl,
                para['dirn'],
                para['dnpt'],
                )

        addLine(axl,
                para['dirn'],
                para['desc'],
                'Device',
                para['dnpt'],
                para['llabel'],
                )

        addUDP(axl,
               para['udp'],
               para['model'],
               para['desc'],
               para['ptn'],
               para['local'],
               para['dirn'],
               para['dnpt'],
               para['llabel'],
               para['ldisplay']
               )

        updateUser(axl,
                   para['user'],
                   language[para['language'].upper()],
                   udplist['udplist'])

        print("\n")


if __name__ == '__main__':
    main()