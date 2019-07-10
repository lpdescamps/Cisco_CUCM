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


REGION = 'EO'
VMFWD = 'false' # true or false
CSSFWD = 'UK_LD_Call_FWD_SIP'
FILE = 'C://shared//API//udp.txt'
SITE = 'EOGBLDS_CIC'
CFWUR_CSS = 'APP_CIC_FWD'

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
def data_from_file():
    ourlist = []
    for line in open(FILE):
        sep = line.strip('\n')
        ourlist.append(sep)
    return ourlist

def getUser(client, username):
    return client.getUser(userid=username)
def updateLine(client, pattern, pt, site, firstname, lastname, extension, cfwd, cic_cfwd):
    print(pattern)
    return client.updateLine(**{
        'pattern': pattern,
        'routePartitionName': pt,
        'description': site + ' - ' + firstname + ' ' + lastname + ' - ' + extension,
        'voiceMailProfileName': {'_value_1': 'NoVoiceMail'},
        'callForwardAll':{  'forwardToVoiceMail': VMFWD,
                            'callingSearchSpaceName': {'_value_1': CSSFWD},
                            'secondaryCallingSearchSpaceName': {'_value_1': CSSFWD},
                            'destination': None},
        'callForwardBusy': cfwd,
        'callForwardBusyInt': cfwd,
        'callForwardNoAnswer': cfwd,
        'callForwardNoAnswerInt': cfwd,
        'callForwardNoCoverage': cfwd,
        'callForwardNoCoverageInt': cfwd,
        'callForwardOnFailure': cfwd,
        'callForwardNotRegistered': cic_cfwd,
        'callForwardNotRegisteredInt': cic_cfwd
    })
def updateUDP(client, udp, site, firstname, lastname, extension):
    return client.updateDeviceProfile(**{
        'name': udp,
        'description': site + ' - ' + firstname + ' ' + lastname + ' - ' + extension
    })

def myvariables(client, userid):
    firstname = (getUser(client, userid)['return']['user']['firstName'])
    lastname = (getUser(client, userid)['return']['user']['lastName'])
    extension = (getUser(client, userid)['return']['user']['telephoneNumber'])
    extlast4 = str(extension[-4:])
    udplist = [udp['_value_1'] for udp in getUser(client, userid)['return']['user']['phoneProfiles']['profileName']]

    for udp in udplist:
        laaplist = [laap for laap in getUser(client, userid)['return']['user']['lineAppearanceAssociationForPresences'][
            'lineAppearanceAssociationForPresence']
                 if laap['laapDeviceName'] in udp]
        theudp = [laap['laapDeviceName'] for laap in laaplist if extlast4 in laap['laapDirectory']][0]
        dn = [str(laap['laapDirectory']).replace('\\', '') for laap in laaplist if extlast4 in laap['laapDirectory']][0]
        pt = [laap['laapPartition'] for laap in laaplist if extlast4 in laap['laapDirectory']][0]

        myvariables_dict = {
            'firstname': firstname,
            'lastname': lastname,
            'ext': extension,
            'fwddn': dn,
            'pt': pt,
            'udp': theudp
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

    for userid in data_from_file():
        print(myvariables(axl, userid))

        cfwd = {'forwardToVoiceMail': VMFWD,
                'callingSearchSpaceName': {'_value_1': CSSFWD},
                'destination': None}

        cfwur = {'forwardToVoiceMail': VMFWD,
                    'callingSearchSpaceName': {'_value_1': CFWUR_CSS},
                    'destination': myvariables(axl, userid)['fwddn']}

        updateLine(axl,
                   '\\' + str(myvariables(axl, userid)['fwddn']),
                   myvariables(axl, userid)['pt'],
                   SITE,
                   myvariables(axl, userid)['firstname'],
                   myvariables(axl, userid)['lastname'],
                   myvariables(axl, userid)['ext'],
                   cfwd,
                   cfwur,
                   )
        updateUDP(axl,
                  myvariables(axl, userid)['udp'],
                  SITE,
                  myvariables(axl, userid)['firstname'],
                  myvariables(axl, userid)['lastname'],
                  myvariables(axl, userid)['ext']
                  )

if __name__ == '__main__':
    main()