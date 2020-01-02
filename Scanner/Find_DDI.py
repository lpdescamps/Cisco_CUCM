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
import csv
from zeep import exceptions
import time
import unicodedata

REGION = 'EO'
USER = '%'

FILE = r"C:\shared\ac\py\pilot_TP_20191210_dirty_NODDI.csv"
NEWFILE = r"C:\shared\ac\py\pilot_TP_" + time.strftime("%Y%m%d-%H%M%S") + '.csv'

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

def csv_headers(newfile):
    f = open(newfile, 'w')
    f.write('DN')
    f.write(',')
    f.write('Name')
    f.write(',')
    f.write('email')
    f.write('\n')
def csv_user(newfile, ddi, name, email):
    f = open(newfile, 'a')
    f.write(str(ddi))
    f.write(',')
    f.write(str(name))
    f.write(',')
    f.write(str(email))
    f.write('\n')
def listUser(client, item):
    return client.listUser(**{
        'searchCriteria': {
            'userid': item,
        },
        'returnedTags': {
            'userid': '',
            'mailid':''
        }
    })
def getUser(client, username):
    return client.getUser(userid=username)
def getUDP(client, udp):
    return client.getDeviceProfile(name=udp)


def myvariables(client, userid):
    firstname = (getUser(client, userid)['return']['user']['firstName'])
    lastname = (getUser(client, userid)['return']['user']['lastName'])

    try:
        extension = (getUser(client, userid)['return']['user']['telephoneNumber'])
        extlast4 = str(extension[-4:])
        udplist = [udp['_value_1'] for udp in getUser(client, userid)['return']['user']['phoneProfiles']['profileName']]
        for udp in udplist:
            laaplist = [laap for laap in getUser(client, userid)['return']['user']['lineAppearanceAssociationForPresences'][
                'lineAppearanceAssociationForPresence']
                     if laap['laapDeviceName'] in udp]
            theudp = [laap['laapDeviceName'] for laap in laaplist if extlast4 in laap['laapDirectory']][0]
            dirn = [str(laap['laapDirectory']).replace('\\', '') for laap in laaplist if extlast4 in laap['laapDirectory']][0]
            pt = [laap['laapPartition'] for laap in laaplist if extlast4 in laap['laapDirectory']][0]

    except:
        try:
            #print("Couln't find ext in Telephone Number from AD for user: " + userid)
            theudp = [udp['_value_1'] for udp in getUser(client, userid)['return']['user']['phoneProfiles']['profileName']][0]
            dirn = [str(items['dirn']['pattern']).replace('\\', '') for items in getUDP(client, theudp)['return']['deviceProfile']['lines']['line']][0]
            pt = [items['dirn']['routePartitionName']['_value_1'] for items in getUDP(client, theudp)['return']['deviceProfile']['lines']['line']][0]
        except:
           # print("Couln't find Telephone Number for user: " + userid)
            theudp = 'None'
            dirn = 'None'
            pt = 'None'

    myvariables_dict = {
        'firstname': firstname,
        'lastname': lastname,
        'DDI': dirn,
        'pt': pt,
        'udp': theudp
    }

    return myvariables_dict

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

    email = [row['email'] for row in csv.DictReader(open(FILE)) if row['DN'] == 'not known']
    emailuser = [item for item in listUser(axl, USER)['return']['user']]
    csv_headers(NEWFILE)

    for item1 in emailuser:
        csv_email = unicodedata.normalize('NFD', str(email)).encode('ascii', 'ignore').decode("utf-8").casefold()
        cisco_email = unicodedata.normalize('NFD', str(item1['mailid'])).encode('ascii', 'ignore').decode("utf-8").casefold()
        if cisco_email in csv_email:
            if myvariables(axl, item1['userid'])['udp'] != 'None':
                print(myvariables(axl, item1['userid']))
                ddi = myvariables(axl, item1['userid'])['DDI']
                firstname = myvariables(axl, item1['userid'])['firstname']
                lastname = myvariables(axl, item1['userid'])['lastname']
                csv_user(NEWFILE, ("\\" + ddi), (firstname + " " + lastname), item1['mailid'])
            else:
                print(myvariables(axl, item1['userid']))
                ddi = 'No DDI found in Cisco'
                firstname = myvariables(axl, item1['userid'])['firstname']
                lastname = myvariables(axl, item1['userid'])['lastname']
                csv_user(NEWFILE, ddi, (firstname + " " + lastname), item1['mailid'])

if __name__ == '__main__':
    main()