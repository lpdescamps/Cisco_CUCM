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
from zeep.plugins import HistoryPlugin

from zeep import exceptions
import unicodedata
import csv

import requests
import xmltodict
import html
from time import sleep, strftime

import http.client as http_client
import logging

DRY_RUN = "disable"  # or "disable"

REGION = 'EO'
IPS = ['*']

DNS1 = '8.8.8.8'
DNS2 = '9.9.9.9'
DNS3 = ''

NAME = 'IT_Help'
JS_MACRO = r'macro\IT_Help.js'
XML_INROOM = r'ui\inroomV4.xml'
#CSV_FILE = r"C:\shared\codec\{} {}{}".format("Cisco Devices compatible with new support button", strftime("%Y%m%d-%H%M%S"), '.csv')
CSV_FILE = r"C:\shared\codec\{} {}{}".format("Cisco Devices compatible with new support button", strftime("%Y%m%d"), '.csv')

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

def confirm():
    reply = str(input("!!!THIS WILL MAKE CONFIGURATION CHANGE!!!" + " (Please write YES to continue or NO to abort then press enter): "))
    if reply == 'YES':
        return True
    if reply == 'NO':
        return False
    else:
        return confirm()

def csv_headers(csv_file):
    f = open(csv_file, 'w')
    headers = ['Region', ',', 'Status', ',', 'Room Name', ',', 'Model', ',', 'IP Address', '\n']
    for header in headers:
        f.write(header)
def csv_codec(csv_file, status, mydict):
    f = open(csv_file, 'a')
    rows = [REGION, ',', status, ',', mydict['Description'], ',', mydict['Model'], ',', mydict['Codec_IP'], '\n']
    for row in rows:
        f.write(row)
def sql_getmodel():
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

    sql_statement = \
        "SELECT " \
            "name, enum " \
        "FROM " \
            "typemodel "
    axl_resp = axl.executeSQLQuery(sql=sql_statement)
    table = [OrderedDict((element.tag, element.text) for element in row) for row in
            serialize_object(axl_resp)["return"]["row"]]
    locale = [(items['name'], items['enum']) for items in table]

    dict_variable = {enum: name for (name, enum) in locale}

    return dict_variable
def get_status(auth, ip):
    url = 'https://' + ip + '/status.xml'
    headers={'Content-Type': 'text/xml'}
    response = requests.request("GET", url=url, auth=auth, headers=headers, verify=False, timeout=30)
    text = response.text
    return text
def get_configuration(auth, ip):
    url = 'https://' + ip + '/configuration.xml'
    headers={'Content-Type': 'text/xml'}
    response = requests.request("GET", url=url, auth=auth, headers=headers, verify=False, timeout=30)
    text = response.text
    return text
def macro_editor(auth, ip, mode):
    payload = """<Configuration>\n\t\t<Macros>\n\t\t\t" \
              "<Mode>""" + mode + """</Mode>\n\t\t" \
              "</Macros>\n\t</Configuration>"""
    url = 'https://' + ip + '/putxml'
    headers={'Content-Type': 'text/xml'}
    response = requests.request("POST", url=url, data=payload, auth=auth, headers=headers, verify=False)
    return {'type': 'OK', 'result': xmltodict.parse(response.content)}
def upload_macro(auth, ip, name, macro):
    with open(macro, 'rb') as macrofile:
        raw = macrofile.read().decode("utf-8")
    code = html.escape(raw, quote=True)
    payload = """<Command>\n<Macros>\n<Macro>\n<Save>\n" \
              "<Name>""" + name + """</Name>\n" \
              "<Overwrite>True</Overwrite>\n" \
              "<body>""" + str(code) + """</body>\n" \
              "</Save>\n</Macro>\n</Macros>\n</Command>"""
    url = 'https://' + ip + '/putxml'
    headers={'Content-Type': 'text/xml'}
    response = requests.request("POST", url=url, data=payload, auth=auth, headers=headers, verify=False)

    return {'type': 'OK', 'result': xmltodict.parse(response.content)}
def enable_macro_file(auth, ip, name):
    payload = """<Command>\n<Macros>\n<Macro>\n<Activate>\n" \
            "<Name>""" + name + """</Name>\n" \
            "</Activate>\t\n</Macro>\n</Macros>\n</Command>"""
    url = 'https://' + ip + '/putxml'
    headers={'Content-Type': 'text/xml'}
    response = requests.request("POST", url=url, data=payload, auth=auth, headers=headers, verify=False)

    return {'type': 'OK', 'result': xmltodict.parse(response.content)}
def upload_inroom(auth, ip, inroom):
    with open(inroom, 'r') as inroomfile:
        raw = inroomfile.read()
    code = html.escape(raw, quote=True)

    payload = """<Command>\n\t\t<UserInterface>\n\t\t\t<Extensions>\n\t\t\t\t<Set>\n<ConfigId>1</ConfigId>\n\t\t\t\t\t" \
                 "<body>""" + str(code) + """</body>\n" \
                 "</Set>\n\t\t\t</Extensions>\n\t\t</UserInterface>\n\t</Command>"""
    url = 'https://' + ip + '/putxml'
    headers={'Content-Type': 'text/xml'}
    response = requests.request("POST", url=url, data=payload, auth=auth, headers=headers, verify=False)

    return {'type': 'OK', 'result': xmltodict.parse(response.content)}
def dns(auth, ip, dns1='', dns2='' , dns3=''):
    payload1 = '<Server item="1"><Address>' + dns1 + '</Address></Server>'
    payload2 = '<Server item="2"><Address>' + dns2 + '</Address></Server>'
    payload3 = '<Server item="3"><Address>' + dns3 + '</Address></Server>'

    payload = '<Configuration><Network><DNS>{}{}{}</DNS></Network></Configuration>'.format(payload1, payload2, payload3)

    url = 'https://' + ip + '/putxml'
    headers={'Content-Type': 'text/xml'}
    response = requests.request("POST", url=url, data=payload, auth=auth, headers=headers, verify=False)
    return {'type': 'OK', 'result': xmltodict.parse(response.content)}


def main():
    path = Path(r"C:\shared\API\credentials")
    wsdl = r"C:\shared\API\wsdl\{}_RISService70.wsdl".format(REGION)
    platform = 'CUCM'
    role = 'rx'
    urllib3.disable_warnings(InsecureRequestWarning)
    session = Session()
    session.verify = False
    session.auth = HTTPBasicAuth(read(file(path, platform, role)[0])[0], crypto(file(path, platform, role)[1], file(path, platform, role)[2]))
    transport = Transport(cache=SqliteCache(), session=session, timeout=60)
    client = Client(wsdl=wsdl, transport=transport)
    #http_client.HTTPConnection.debuglevel = 1
    #logger = logging.getLogger(__name__)
    factory = client.type_factory('ns0')

    try:
        read(CSV_FILE)
        print("File '{}' found, skipping the file creation".format(CSV_FILE))
    except FileNotFoundError:
        print("File '{}' not found, creating the file".format(CSV_FILE))
        csv_headers(CSV_FILE)

    codec_platform = 'codec'
    codec_role = 'rwx'
    codec_user = read(file(path, codec_platform, codec_role)[0])[0]
    codec_pwd = crypto(file(path, codec_platform, codec_role)[1], file(path, codec_platform, codec_role)[2])
    a = (codec_user, codec_pwd)

    item = []
    for ip in IPS:
        item.append(factory.SelectItem(Item=ip))
    Item = factory.ArrayOfSelectItem(item)
    stateInfo = ''
    criteria = factory.CmSelectionCriteria(
        MaxReturnedDevices=1000,
        DeviceClass='Phone',
        Model=255,
        Status='Registered',
        NodeName='',
        SelectBy='IPV4Address',
        SelectItems=Item,
        Protocol='SIP',
        DownloadStatus='Any'
    )
    rawresult = client.service.selectCmDevice(stateInfo, criteria)['SelectCmDeviceResult']['CmNodes']['item']


    models = sql_getmodel()

    if DRY_RUN == "disable":
        if confirm() is True:
            pass
        else:
            quit()
    else:
        pass

    for result in rawresult:
        if 'Ok' in result['ReturnCode']:
            for device in result['CmDevices']['item']:
                if 'TelePresence' in models[str(device['Model'])]:
                    mydict = {
                        'name': device['Name'],
                        'Model': models[str(device['Model'])],
                        'Description': device['Description'],
                        'Protocol': device['Protocol'],
                        'ActiveLoadID': device['ActiveLoadID'],
                        'DirectoryNumber': device['LinesStatus']['item'][0]['DirectoryNumber'],
                        'Codec_IP': device['IPAddress']['item'][0]['IP']
                    }
                    try:
                        codec_status = str(get_status(a, mydict['Codec_IP']))
                        codec_conf = str(get_configuration(a, mydict['Codec_IP']))

                        touch = 'Cisco TelePresence Touch' in codec_status
                        macros = '/Macros' in codec_conf

                        if DRY_RUN == "disable":
                            print("!!!!!!!! DRY RUN IS {}. CONFIGURATION CHANGES ARE TAKING PLACE. STOP THE SCRIPT IF NOT WANTED!!!!!!!!!!!!!".format(DRY_RUN))
                            if touch and macros is True:
                                print("Compatible for button on {} {} model {}. Adding the button".format(mydict['Description'], mydict['Codec_IP'], mydict['Model']))
                                csv_codec(CSV_FILE, "Button Added", mydict)
                                print("Enabling Macro")
                                macro_editor(a, mydict['Codec_IP'], 'On')
                                sleep(3)
                                print("Uploading Macro")
                                upload_macro(a, mydict['Codec_IP'], NAME, JS_MACRO)
                                sleep(3)
                                enable_macro_file(a, mydict['Codec_IP'], NAME)
                                sleep(3)
                                macro_editor(a, mydict['Codec_IP'], 'Off')
                                sleep(3)
                                macro_editor(a, mydict['Codec_IP'], 'On')
                                sleep(3)
                                print("Uploading UserInterface")
                                upload_inroom(a, mydict['Codec_IP'], XML_INROOM)
                                print("Adding DNS {}, {}, {} for codec {} {}".format(DNS1, DNS2, DNS3, mydict['Description'], mydict['Codec_IP']))
                                dns(a, mydict['Codec_IP'], dns1=DNS1, dns2=DNS2, dns3=DNS3)

                            else:
                                print("Not compatible for button on {} {} model {}. Skipping the button".format(mydict['Description'], mydict['Codec_IP'], mydict['Model']))
                                csv_codec(CSV_FILE, "Not compatible", mydict)

                        else:
                            print("!!!!!!!! DRY RUN IS {}. NO CONFIGURATION CHANGES ARE TAKING PLACE. AUDITING ONLY!!!!!!!!!!!!!".format(DRY_RUN))
                            if touch and macros is True:
                                print("Compatible for button on {} {} model {}.".format(mydict['Description'], mydict['Codec_IP'], mydict['Model']))
                                csv_codec(CSV_FILE, "Button Added", mydict)
                                print("Writing the csv entries")

                            else:
                                print("Not compatible for button on {} {} model {}.".format(mydict['Description'], mydict['Codec_IP'], mydict['Model']))
                                csv_codec(CSV_FILE, "Not compatible", mydict)
                                print("Writing the csv entries")
                        print("Completed \n")

                    except:
                        print("Codec with IP " + mydict['Codec_IP'] + " is offline")
                        pass

if __name__ == '__main__':
    main()