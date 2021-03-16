# -*- coding: utf-8 -*-
from zeep import Client
from zeep.cache import SqliteCache
from zeep.transports import Transport
from zeep.helpers import serialize_object
from requests import Session
from requests.auth import HTTPBasicAuth
import urllib3
from urllib3.exceptions import InsecureRequestWarning
from collections import OrderedDict
import time
from cryptography.fernet import Fernet
from pathlib import Path


REGION = 'AP'
PATTERN = '%'
FILE = 'C://shared//API//' + REGION + '-Numbers_' + time.strftime("%Y%m%d-%H%M%S") + '.csv'
NBS = {'222433', '222434', '222435', '222436', '222437', '222438', '222440', '255445', '255319', }

# NBS = {'{}'.format(nb) for nb in range(4900000, 5000000)}


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

def csv_headers(file):
    f = open(file, 'w')
    f.write('Type')
    f.write(',')
    f.write('Pattern')
    f.write(',')
    f.write('Partition')
    f.write(',')
    f.write('Description')
    f.write(',')
    f.write('CalledX')
    f.write(',')
    f.write('CalledPrefix')
    f.write(',')
    f.write('CallingX')
    f.write(',')
    f.write('CallingPrefix')
    f.write(',')
    f.write('FwdAll')
    f.write(',')
    f.write('FwdBusyInt')
    f.write(',')
    f.write('FwdBusyExt')
    f.write(',')
    f.write('FwdNAnsInt')
    f.write(',')
    f.write('FwdNAnsExt')
    f.write(',')
    f.write('FwdNCovInt')
    f.write(',')
    f.write('FwdNCovExt')
    f.write(',')
    f.write('FwdCTIFail')
    f.write(',')
    f.write('FwdURegInt')
    f.write(',')
    f.write('FwdURegExt')
    f.write(',')
    f.write('ExtPNMask')
    f.write(',')
    f.write('Device')
    f.write('\n')
def csv_dn(client, file, dn):
    f = open(file, 'a')
    f.write('DirectoryNumber')
    f.write(',')
    f.write(str(dn['dnorpattern']))
    f.write(',')
    f.write(str(dn['routepartitionname']))
    f.write(',')
    f.write(str(dn['description']))
    f.write(',')
    f.write('N/A')
    f.write(',')
    f.write('N/A')
    f.write(',')
    f.write('N/A')
    f.write(',')
    f.write('N/A')
    f.write(',')
    f.write(str(dn['cfadestination']))
    f.write(',')
    f.write(str(dn['cfbintdestination']))
    f.write(',')
    f.write(str(dn['cfbdestination']))
    f.write(',')
    f.write(str(dn['cfnaintdestination']))
    f.write(',')
    f.write(str(dn['cfnadestination']))
    f.write(',')
    f.write(str(dn['pffintdestination']))
    f.write(',')
    f.write(str(dn['pffdestination']))
    f.write(',')
    f.write(str(dn['devicefailuredn']))
    f.write(',')
    f.write(str(dn['cfurintdestination']))
    f.write(',')
    f.write(str(dn['cfurdestination']))
    f.write(',')
    f.write(str(ExtPNMask(client, dn)[0]))
    f.write(',')
    f.write(str(ExtPNMask(client, dn)[1]))
    f.write('\n')
def csv_tp(file, tp):
    f = open(file, 'a')
    f.write('TranslationPattern')
    f.write(',')
    f.write(str(tp['pattern']))
    f.write(',')
    f.write(str(tp['routePartitionName']['_value_1']))
    f.write(',')
    f.write(str(tp['description']))
    f.write(',')
    f.write(str(tp['calledPartyTransformationMask']))
    f.write(',')
    f.write(str(tp['prefixDigitsOut']))
    f.write(',')
    f.write(str(tp['callingPartyTransformationMask']))
    f.write(',')
    f.write(str(tp['callingPartyPrefixDigits']))
    f.write(',')
    f.write('N/A')
    f.write(',')
    f.write('N/A')
    f.write(',')
    f.write('N/A')
    f.write(',')
    f.write('N/A')
    f.write(',')
    f.write('N/A')
    f.write(',')
    f.write('N/A')
    f.write(',')
    f.write('N/A')
    f.write(',')
    f.write('N/A')
    f.write(',')
    f.write('N/A')
    f.write(',')
    f.write('N/A')
    f.write(',')
    f.write('N/A')
    f.write(',')
    f.write('N/A')
    f.write('\n')
def csv_rp(file, rp):
    f = open(file, 'a')
    f.write('RoutePattern')
    f.write(',')
    f.write(str(rp['pattern']))
    f.write(',')
    f.write(str(rp['routePartitionName']['_value_1']))
    f.write(',')
    f.write(str(rp['description']))
    f.write(',')
    f.write(str(rp['calledPartyTransformationMask']))
    f.write(',')
    f.write(str(rp['prefixDigitsOut']))
    f.write(',')
    f.write(str(rp['callingPartyTransformationMask']))
    f.write(',')
    f.write(str(rp['callingPartyPrefixDigits']))
    f.write(',')
    f.write('N/A')
    f.write(',')
    f.write('N/A')
    f.write(',')
    f.write('N/A')
    f.write(',')
    f.write('N/A')
    f.write(',')
    f.write('N/A')
    f.write(',')
    f.write('N/A')
    f.write(',')
    f.write('N/A')
    f.write(',')
    f.write('N/A')
    f.write(',')
    f.write('N/A')
    f.write(',')
    f.write('N/A')
    f.write(',')
    f.write('N/A')
    f.write(',')
    f.write('N/A')
    f.write('\n')
def csv_hp(file, hp):
    f = open(file, 'a')
    f.write('HuntPilot')
    f.write(',')
    f.write(str(hp['pattern']))
    f.write(',')
    f.write(str(hp['routePartitionName']['_value_1']))
    f.write(',')
    f.write(str(hp['description']))
    f.write(',')
    f.write(str(hp['calledPartyTransformationMask']))
    f.write(',')
    f.write(str(hp['prefixDigitsOut']))
    f.write(',')
    f.write(str(hp['callingPartyTransformationMask']))
    f.write(',')
    f.write(str(hp['callingPartyPrefixDigits']))
    f.write(',')
    f.write('N/A')
    f.write(',')
    f.write('N/A')
    f.write(',')
    f.write('N/A')
    f.write(',')
    f.write('N/A')
    f.write(',')
    f.write('N/A')
    f.write(',')
    f.write('N/A')
    f.write(',')
    f.write('N/A')
    f.write(',')
    f.write('N/A')
    f.write(',')
    f.write('N/A')
    f.write(',')
    f.write('N/A')
    f.write(',')
    f.write('N/A')
    f.write(',')
    f.write('N/A')
    f.write('\n')
def csv_cingp(file,cingp):
    f = open(file, 'a')
    f.write('CingPartyX')
    f.write(',')
    f.write(str(cingp['pattern']))
    f.write(',')
    f.write(str(cingp['routePartitionName']['_value_1']))
    f.write(',')
    f.write(str(cingp['description']))
    f.write(',')
    f.write('N/A')
    f.write(',')
    f.write('N/A')
    f.write(',')
    f.write(str(cingp['callingPartyTransformationMask']))
    f.write(',')
    f.write(str(cingp['callingPartyPrefixDigits']))
    f.write(',')
    f.write('N/A')
    f.write(',')
    f.write('N/A')
    f.write(',')
    f.write('N/A')
    f.write(',')
    f.write('N/A')
    f.write(',')
    f.write('N/A')
    f.write(',')
    f.write('N/A')
    f.write(',')
    f.write('N/A')
    f.write(',')
    f.write('N/A')
    f.write(',')
    f.write('N/A')
    f.write(',')
    f.write('N/A')
    f.write(',')
    f.write('N/A')
    f.write(',')
    f.write('N/A')
    f.write('\n')
def csv_cedp(file,cedp):
    f = open(file, 'a')
    f.write('CedPartyX')
    f.write(',')
    f.write(str(cedp['pattern']))
    f.write(',')
    f.write(str(cedp['routePartitionName']['_value_1']))
    f.write(',')
    f.write(str(cedp['description']))
    f.write(',')
    f.write('N/A')
    f.write(',')
    f.write('N/A')
    f.write(',')
    f.write(str(cedp['calledPartyTransformationMask']))
    f.write(',')
    f.write(str(cedp['calledPartyPrefixDigits']))
    f.write(',')
    f.write('N/A')
    f.write(',')
    f.write('N/A')
    f.write(',')
    f.write('N/A')
    f.write(',')
    f.write('N/A')
    f.write(',')
    f.write('N/A')
    f.write(',')
    f.write('N/A')
    f.write(',')
    f.write('N/A')
    f.write(',')
    f.write('N/A')
    f.write(',')
    f.write('N/A')
    f.write(',')
    f.write('N/A')
    f.write(',')
    f.write('N/A')
    f.write(',')
    f.write('N/A')
    f.write('\n')
def print_dn(client, dn):
    print('Type: DirectoryNumber')
    print('DN: ' + (str(dn['dnorpattern'])))
    print('Partition: ' + (str(dn['routepartitionname'])))
    print('Description: ' + (str(dn['description'])))
    print('FwdAll: ' + (str(dn['cfadestination'])))
    print('FwdBusyInt: ' + (str(dn['cfbintdestination'])))
    print('FwdBusyExt: ' + (str(dn['cfbdestination'])))
    print('FwdNAnsInt: ' + (str(dn['cfnaintdestination'])))
    print('FwdNAnsExt: ' + (str(dn['cfnadestination'])))
    print('FwdNCovInt: ' + (str(dn['pffintdestination'])))
    print('FwdNCovExt: ' + (str(dn['pffdestination'])))
    print('FwdCTIFail: ' + (str(dn['devicefailuredn'])))
    print('FwdURegInt: ' + (str(dn['cfurintdestination'])))
    print('FwdURegExt: ' + (str(dn['cfurdestination'])))
    print('ExtPNMask: ' + (str(ExtPNMask(client, dn)[0])) + ' on ' + (str(ExtPNMask(client, dn)[1])))
    print('#####The End#########The End#########The End#########The End####')
def print_tp(tp):
    print('Type: TranslationPattern')
    print('DN: ' + (str(tp['pattern'])))
    print('Partition: ' + (str(tp['routePartitionName']['_value_1'])))
    print('Description: ' + (str(tp['description'])))
    print('CalledX: ' + (str(tp['calledPartyTransformationMask'])))
    print('CalledPrefix: ' + (str(tp['prefixDigitsOut'])))
    print('CallingX: ' + (str(tp['callingPartyTransformationMask'])))
    print('CallingPrefix: ' + (str(tp['callingPartyPrefixDigits'])))
    print('#####The End#########The End#########The End#########The End####')
def print_rp(rp):
    print('Type: RoutePattern')
    print('DN: ' + (str(rp['pattern'])))
    print('Partition: ' + (str(rp['routePartitionName']['_value_1'])))
    print('Description: ' + (str(rp['description'])))
    print('CalledX: ' + (str(rp['calledPartyTransformationMask'])))
    print('CalledPrefix: ' + (str(rp['prefixDigitsOut'])))
    print('CallingX: ' + (str(rp['callingPartyTransformationMask'])))
    print('CallingPrefix: ' + (str(rp['callingPartyPrefixDigits'])))
    print('#####The End#########The End#########The End#########The End####')
def print_hp(hp):
    print('Type: HuntPilot')
    print('DN: ' + (str(hp['pattern'])))
    print('Partition: ' + (str(hp['routePartitionName']['_value_1'])))
    print('Description: ' + (str(hp['description'])))
    print('CalledX: ' + (str(hp['calledPartyTransformationMask'])))
    print('CalledPrefix: ' + (str(hp['prefixDigitsOut'])))
    print('CallingX: ' + (str(hp['callingPartyTransformationMask'])))
    print('CallingPrefix: ' + (str(hp['callingPartyPrefixDigits'])))
    print('#####The End#########The End#########The End#########The End####')
def print_cingp(cingp):
    print('Type: CingPartyX')
    print('DN: ' + (str(cingp['pattern'])))
    print('Partition: ' + (str(cingp['routePartitionName']['_value_1'])))
    print('Description: ' + (str(cingp['description'])))
    print('CallingX: ' + (str(cingp['callingPartyTransformationMask'])))
    print('CallingPrefix: ' + (str(cingp['callingPartyPrefixDigits'])))
    print('#####The End#########The End#########The End#########The End####')
def print_cedp(cedp):
    print('Type: CedPartyX')
    print('DN: ' + (str(cedp['pattern'])))
    print('Partition: ' + (str(cedp['routePartitionName']['_value_1'])))
    print('Description: ' + (str(cedp['description'])))
    print('CallingX: ' + (str(cedp['calledPartyTransformationMask'])))
    print('CallingPrefix: ' + (str(cedp['calledPartyPrefixDigits'])))
    print('#####The End#########The End#########The End#########The End####')
def listTransPattern(client, pattern):
    return client.listTransPattern(**{
        'searchCriteria': {
            'pattern': pattern,
        },
        'returnedTags': {
            'pattern': '',
            'description': '',
            'calledPartyTransformationMask': '',
            'callingPartyTransformationMask': '',
            'callingPartyPrefixDigits': '',
            'prefixDigitsOut': '',
            'routePartitionName': ''
        }
    })
def listRoutePattern(client, pattern):
    return client.listRoutePattern(**{
        'searchCriteria': {
            'pattern': pattern,
        },
        'returnedTags': {
            'pattern': '',
            'description': '',
            'calledPartyTransformationMask': '',
            'callingPartyTransformationMask': '',
            'callingPartyPrefixDigits': '',
            'prefixDigitsOut': '',
            'routePartitionName': ''
        }
    })
def listHuntPilot(client, pattern):
    return client.listHuntPilot(**{
        'searchCriteria': {
            'pattern': pattern,
        },
        'returnedTags': {
            'pattern': '',
            'description': '',
            'calledPartyTransformationMask': '',
            'callingPartyTransformationMask': '',
            'callingPartyPrefixDigits': '',
            'prefixDigitsOut': '',
            'routePartitionName': ''
        }
    })
def listCallingPartyTransformationPattern(client, pattern):
    return client.listCallingPartyTransformationPattern(**{
        'searchCriteria': {
            'pattern': pattern,
        },
        'returnedTags': {
            'pattern': '',
            'description': '',
            'routePartitionName': '',
            'callingPartyTransformationMask': '',
            'callingPartyPrefixDigits': '',
        }
    })
def listCalledPartyTransformationPattern(client, pattern):
    return client.listCalledPartyTransformationPattern(**{
        'searchCriteria': {
            'pattern': pattern,
        },
        'returnedTags': {
            'pattern': '',
            'description': '',
            'routePartitionName': '',
            'calledPartyTransformationMask': '',
            'calledPartyPrefixDigits': '',
        }
    })
def sql_dn(service, pattern):
    sql_statement = "SELECT dnorpattern,numplan.description,cfadestination,cfbdestination,cfnadestination,cfbintdestination," \
            "cfnaintdestination,pffdestination,pffintdestination,cfurdestination,devicefailuredn, cfadestination,cfurintdestination," \
            "routepartition.name as routepartitionname " \
            "FROM numplan JOIN callforwarddynamic ON " \
            "numplan.pkid=callforwarddynamic.fknumplan JOIN routepartition ON numplan.fkroutepartition=routepartition.pkid " \
            "where dnorpattern like '"+pattern+"' "
    axl_resp = service.executeSQLQuery(sql=sql_statement)
    return [OrderedDict((element.tag, element.text) for element in row) for row in serialize_object(axl_resp)["return"]["row"]]
def sql_device(service, dn):
    sql_statement = "select d.name from device as d, numplan as n, devicenumplanmap as dnpm " \
                    "where dnpm.fkdevice = d.pkid and dnpm.fknumplan = n.pkid and d.tkclass IN (1, 254) and n.DNOrPattern='"+dn+"' "
    axl_resp = service.executeSQLQuery(sql=sql_statement)
    if not axl_resp["return"]:
        pass
    else:
        return [OrderedDict((element.tag, element.text) for element in row) for row in serialize_object(axl_resp)["return"]["row"]]
def getPhone(client, name):
    return client.getPhone(name=name)
def ExtPNMask(client, pattern):
    if not sql_device(client, str(pattern['dnorpattern'])):
        return 'N/A', 'N/A'
    else:
        for device in sql_device(client, str(pattern['dnorpattern'])):
            for mask in getPhone(client, device['name'])['return']['phone']['lines']['line']:
                return mask['e164Mask'], device['name']

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
    csv_headers(FILE)
    fields_route = {'pattern', 'calledPartyTransformationMask', 'prefixDigitsOut', 'callingPartyTransformationMask',
              'callingPartyPrefixDigits'}
    try:

##Searching for Directory Number
        for dn in sql_dn(axl, PATTERN):
            for nb in NBS:
                fields = {'dnorpattern', 'routepartitionname', 'cfadestination', 'cfbintdestination', 'cfbdestination', 'cfnaintdestination',
                          'cfnadestination', 'pffintdestination', 'pffdestination', 'devicefailuredn', 'cfurintdestination', 'cfurdestination'}
                for field in fields:
                    if nb in (str(dn[field])):
                        print_dn(axl,dn)
                        csv_dn(axl,FILE,dn)

##Searching for Translation Pattern
        if not listTransPattern(axl, PATTERN)['return']:
            ##No item found
            pass
        else:
            for tp in listTransPattern(axl, PATTERN)['return']['transPattern']:
                for nb in NBS:
                    for field in fields_route:
                        if nb in (str(tp[field])):
                            print_tp(tp)
                            csv_tp(FILE,tp)

##Searching for Route Pattern
        if not listRoutePattern(axl, PATTERN)['return']:
            ##No item found
            pass
        else:
            for rp in listRoutePattern(axl, PATTERN)['return']['routePattern']:
                for nb in NBS:
                    for field in fields_route:
                        if nb in (str(rp[field])):
                            print_rp(rp)
                            csv_rp(FILE,rp)

##Searching for Hunt Pilot
        if not listHuntPilot(axl, PATTERN)['return']:
            ##No item found
            pass
        else:
            for hp in listHuntPilot(axl, PATTERN)['return']['huntPilot']:
                for nb in NBS:
                    for field in fields_route:
                        if nb in (str(hp[field])):
                            print_hp(hp)
                            csv_hp(FILE,hp)

##Searching for Calling Party Transformation Pattern
        if not listCallingPartyTransformationPattern(axl, PATTERN)['return']:
            ##No item found
            pass
        else:
            for cingp in listCallingPartyTransformationPattern(axl, PATTERN)['return']['callingPartyTransformationPattern']:
                for nb in NBS:
                    fields = {'pattern', 'callingPartyTransformationMask', 'callingPartyPrefixDigits'}
                    for field in fields:
                        if nb in (str(cingp[field])):
                            print_cingp(cingp)
                            csv_cingp(FILE,cingp)

##Searching for Called Party Transformation Pattern
        if not listCalledPartyTransformationPattern(axl, PATTERN)['return']:
            ##No item found
            pass
        else:
            for cedp in listCalledPartyTransformationPattern(axl, PATTERN)['return']['calledPartyTransformationPattern']:
                for nb in NBS:
                    fields = {'pattern', 'calledPartyTransformationMask', 'calledPartyPrefixDigits'}
                    for field in fields:
                        if nb in (str(cedp[field])):
                            print_cedp(cedp)
                            csv_cedp(FILE,cedp)

    except:
        print('Except ERROR')
        pass

if __name__ == '__main__':
    main()