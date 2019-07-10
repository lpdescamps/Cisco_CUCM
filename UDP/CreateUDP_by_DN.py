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

REGION = 'eo'
#UDP = '8175005_UDP'
UDP = 'ESMA_%'
RANGEDN = '\+3491789'
PREFIX = '817'
SITE = 'EOESMAD'
NEWMODEL = 'Cisco 8845'
PTN = 'GL_UUID_1LSD2URISDs_SIP-pbtc'

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
def listUDP(client, udp):
    return client.listDeviceProfile(**{
        'searchCriteria': {
            'name': udp,
        },
        'returnedTags': {
            'name': ''
        }
    })
def getUDP(client, udp):
    return client.getDeviceProfile(name=udp)
def getLine(client, dn, dnpt):
    return client.getLine(pattern=dn,routePartitionName=dnpt)
def getUser(client, user):
    return client.getUser(userid=user)
def sql_get_user_items(service, udp, dn):

    sql_statement = \
        "SELECT " \
            "E.firstname, E.lastname, E.userid " \
        "FROM " \
            "enduserdevicemap EDM " \
        "JOIN device D " \
            "ON EDM.fkdevice = D.pkid " \
        "JOIN enduser E " \
            "ON EDM.fkenduser = E.pkid " \
        "WHERE D.name = '"+udp+"'"
    axl_resp = service.executeSQLQuery(sql=sql_statement)
    table = [OrderedDict((element.tag, element.text) for element in row) for row in
            serialize_object(axl_resp)["return"]["row"]]
    firstname = [items['firstname'] for items in table][0]
    lastname = [items['lastname'] for items in table][0]
    userid = [items['userid'] for items in table][0]

    newudp = userid + '_' + str(NEWMODEL[-4:]) + '-udp'
    desc = SITE + '_' + firstname + ' ' + lastname + '_' + PREFIX + str(dn[-4:])
    ldisplay = firstname + ' ' + lastname
    llabel = firstname + ' ' + lastname + ' - ' + PREFIX + str(dn[-4:])

    return newudp, desc, ldisplay, llabel, userid
def addUDP(client, name, model, desc, ptn, local, dirn, dnpt, llabel, ldisplay):
    client.addDeviceProfile(deviceProfile=
        {
        'name': name,
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
def updateLine(client, dn, pt, desc, ldisplay):
    return client.updateLine(**{
    'pattern': dn,
    'routePartitionName': pt,
    'description': desc,
    'alertingName': ldisplay,
    'asciiAlertingName': ldisplay
    })
def updateUser(client, user, *args):
    return client.updateUser(**{
    'userid': user,
    'phoneProfiles': {
        'profileName':
            args[0]
        }
    })
def myvariables(client, udps):
    udp = getUDP(client, udps)['return']['deviceProfile']['name']
    dn = [items['dirn']['pattern'] for items in getUDP(client, udps)['return']['deviceProfile']['lines']['line']][0]
    dnpt = [items['dirn']['routePartitionName']['_value_1'] for items in getUDP(client, udps)['return']['deviceProfile']['lines']['line']][0]
    local = getUDP(client, udps)['return']['deviceProfile']['userLocale']
    rightudps = [items for items in getLine(client, dn, dnpt)['return']['line']['associatedDevices']['device']]
    models = [getUDP(client, items)['return']['deviceProfile']['model'] for items in rightudps]
    modeltuple = tuple(zip(models, rightudps))
    newmodelcheck = [items for items in modeltuple if NEWMODEL in items]

    try:
        newudp = sql_get_user_items(client, rightudps[0], dn)[0]
        desc = sql_get_user_items(client, rightudps[0], dn)[1]
        ldisplay = sql_get_user_items(client, rightudps[0], dn)[2]
        llabel = sql_get_user_items(client, rightudps[0], dn)[3]
        userid = sql_get_user_items(client, rightudps[0], dn)[4]
        udplist = [items['_value_1'] for items in getUser(client, userid)['return']['user']['phoneProfiles']['profileName']]
    except:
        newudp = PREFIX + str(dn[-4:]) + '_' + str(NEWMODEL[-4:]) + '-udp'
        desc = 'FREE ' + SITE + '_firstname lastname_' + PREFIX + str(dn[-4:])
        ldisplay = 'firstname lastname'
        llabel = 'firstname lastname - ' + PREFIX + str(dn[-4:])
        userid = 'no_userid'
        udplist = 'no_udplist'

    myvariables_dict = {
        'udp': udp,
        'dn': dn,
        'dnpt': dnpt,
        'local': local,
        'rightudps': rightudps[0],
        'models': models,
        'modeltuple': modeltuple,
        'newmodelcheck': newmodelcheck,
        'newudp': newudp,
        'desc': desc,
        'ldisplay': ldisplay,
        'llabel': llabel,
        'userid': userid,
        'udplist': udplist
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

    for udps in listUDP(axl, UDP)['return']['deviceProfile']:
        if getUDP(axl, udps)['return']['deviceProfile']['lines'] is None:
            print(udps['name'], 'has no Directory Number')
            print('#####The End#########The End#########The End#########The End####')
            pass
        else:
            dn = [items['dirn']['pattern'] for items in getUDP(axl, udps)['return']['deviceProfile']['lines']['line']][0]
            if dn.startswith(RANGEDN) is True:
                mystuff = myvariables(axl, udps['name'])
                print(mystuff)
                for udp in mystuff['newmodelcheck']:
                    print('UDP ' + udp[1] + ' on directory number ' + mystuff['dn'] + ' already exist for model ' + NEWMODEL)
                    print('#####The End#########The End#########The End#########The End####')
                if not mystuff['newmodelcheck']:
                    if not mystuff['newmodelcheck'] and mystuff['userid'] == 'no_userid':
                        print("Looks like a free UDP to me! Didnt find an enduser! Let's create the FREE UDP: " + mystuff['newudp'] + ' with description: ' + mystuff['desc'])
                        addUDP(axl,
                               mystuff['newudp'],
                               NEWMODEL, mystuff['desc'],
                               PTN, mystuff['local'],
                               mystuff['dn'],
                               mystuff['dnpt'],
                               mystuff['llabel'],
                               mystuff['ldisplay'])
                        updateLine(axl,
                                   mystuff['dn'],
                                   mystuff['dnpt'],
                                   mystuff['desc'],
                                   mystuff['ldisplay'])
                        print('#####The End#########The End#########The End#########The End####')
                    else:
                        print("Cool! I found an enduser! Let's create the UDP: " + mystuff['newudp'] + ' with description: ' + mystuff['desc'])
                        addUDP(axl,
                               mystuff['newudp'],
                               NEWMODEL,
                               mystuff['desc'],
                               PTN,
                               mystuff['local'],
                               mystuff['dn'],
                               mystuff['dnpt'],
                               mystuff['llabel'],
                               mystuff['ldisplay'])
                        updateLine(axl,
                                   mystuff['dn'],
                                   mystuff['dnpt'],
                                   mystuff['desc'],
                                   mystuff['ldisplay'])
                        mystuff['udplist'].append(mystuff['newudp'])
                        updateUser(axl,
                                   mystuff['userid'],
                                   mystuff['udplist'])
                        print('#####The End#########The End#########The End#########The End####')
            else:
                pass

if __name__ == '__main__':
    main()