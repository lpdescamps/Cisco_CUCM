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
import unicodedata
from zeep import exceptions
import socket

# Dynamic Variables - Do change
REGION = 'EO'
COUNTRY = 'UK'
CMG = 'S3_S4_S2_CMG'
SIPtr_SBCT_InACSBCAInt_pt = "partition1:partition2"

# Static Variables - Do not change
SBC_IP = socket.gethostbyname_ex('hasbc.{}.lpdne.eu'.format(COUNTRY.lower()))
STSP = '{}{}CL_ACSBC-stsp'.format(REGION, COUNTRY)
SPI = '{}{}CL_Tr_ACSBC-spi'.format(REGION, COUNTRY)
PT = [
    {"name": "{}_TP_ACSBC-pt",
    "desc": "Route calls to AudioCodes SBC"},
    {"name": "{}_RP_ACSBC-pt",
    "desc": "Route calls to AudioCodes SBC"},
    ]
CSS = [
    {"name": "{}_TP_ACSBC-css",
    "desc": "Route calls to AudioCodes SBC",
     "pt": "{}_RP_ACSBC-pt"},
    {"name": "{}_SBCT_InACSBCAInt-css",
    "desc": "Inbound Calls From AudioCodes SBC",
     "pt": SIPtr_SBCT_InACSBCAInt_pt},
    ]
REG = "{}{}CL_ACSBC-reg".format(REGION, COUNTRY)
DTG = "GMT-UTC_24H-dtg"
DP = "{}{}CL_ACSBC-dp".format(REGION, COUNTRY)
RP = [
    {"pattern": "\+!",
    "desc": "Route to AC SBC",
     "pt": "{}_RP_ACSBC-pt"},
    {"pattern": "!",
    "desc": "Route to AC SBC",
     "pt": "{}_RP_ACSBC-pt"},
    ]


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

def listCSS(client, item):
    return client.listCss(**{
        'searchCriteria': {
            'name': item,
        },
        'returnedTags': {
            'name': ''
        }
    })
def getCSS(client, item):
    return client.getCss(name=item)
def addptCSS(client, css, pt, index):
    try:
        return client.updateCss(**{
        'name': css,
        'addMembers': {
            'member': {
                'routePartitionName': pt,
                'index': index
            }
        }})
    except exceptions.Fault:
        print('!!!!!!!!partition {} already assigned to css {}'.format(pt,css))
def rmptCSS(client, css, pt, index):
    try:
        return client.updateCss(**{
        'name': css,
        'removeMembers': {
            'member': {
                'routePartitionName': pt,
                'index': index
            }
        }})
    except exceptions.Fault:
        print('!!!!!!!!partition {} is not assigned to css {}'.format(pt,css))

def addstsp(client, item):
    client.addSipTrunkSecurityProfile(sipTrunkSecurityProfile=
                    {
                        'name': item,
                        'description': 'Secured Profile for AudioCodes SBC',
                        'securityMode': 'Encrypted',
                        'incomingTransport': 'TLS',
                        'outgoingTransport': 'TLS',
                        'digestAuthentication': 'false',
                        'noncePolicyTime': 600,
                        'x509SubjectName': 'hasbc.{}.qbe.com'.format(COUNTRY.lower()),
                        'incomingPort': 5061,
                        'applLevelAuthentication': 'false',
                        'acceptPresenceSubscription': 'false',
                        'acceptOutOfDialogRefer': 'false',
                        'acceptUnsolicitedNotification': 'true',
                        'allowReplaceHeader': 'true',
                        'transmitSecurityStatus': 'false',
                        'sipV150OutboundSdpOfferFiltering': 'Use Default Filter',
                        'allowChargingHeader': 'false'
                    }
                    )
def addspi(client, item):
    client.addSipProfile(sipProfile=
                    {
                        'name': item,
                        'description': 'Standard SIP Profile - For AudioCodes SBC',
                        'defaultTelephonyEventPayloadType': 101,
                        'redirectByApplication': 'true',
                        'ringing180': 'false',
                        'timerInvite': 180,
                        'timerRegisterDelta': 5,
                        'timerRegister': 3600,
                        'timerT1': 500,
                        'timerT2': 4000,
                        'retryInvite': 6,
                        'retryNotInvite': 10,
                        'startMediaPort': 16385,
                        'stopMediaPort': 32764,
                        'startVideoPort': 0,
                        'stopVideoPort': 0,
                        'dscpForAudioCalls': None,
                        'dscpForVideoCalls': None,
                        'dscpForAudioPortionOfVideoCalls': None,
                        'dscpForTelePresenceCalls': None,
                        'dscpForAudioPortionOfTelePresenceCalls': None,
                        'callpickupListUri': 'x-cisco-serviceuri-opickup',
                        'callpickupGroupUri': 'x-cisco-serviceuri-gpickup',
                        'meetmeServiceUrl': 'x-cisco-serviceuri-meetme',
                        'userInfo': 'None',
                        'dtmfDbLevel': 'Nominal',
                        'callHoldRingback': 'Off',
                        'anonymousCallBlock': 'Off',
                        'callerIdBlock': 'Off',
                        'dndControl': 'User',
                        'telnetLevel': 'Disabled',
                        'timerKeepAlive': 120,
                        'timerSubscribe': 120,
                        'timerSubscribeDelta': 5,
                        'maxRedirects': 70,
                        'timerOffHookToFirstDigit': 15000,
                        'callForwardUri': 'x-cisco-serviceuri-cfwdall',
                        'abbreviatedDialUri': 'x-cisco-serviceuri-abbrdial',
                        'confJointEnable': 'true',
                        'rfc2543Hold': 'false',
                        'semiAttendedTransfer': 'true',
                        'enableVad': 'false',
                        'stutterMsgWaiting': 'false',
                        'callStats': 'false',
                        't38Invite': 'false',
                        'faxInvite': 'false',
                        'rerouteIncomingRequest': 'Never',
                        'resourcePriorityNamespaceListName': {
                            '_value_1': None,
                            'uuid': None
                        },
                        'enableAnatForEarlyOfferCalls': 'false',
                        'rsvpOverSip': 'Local RSVP',
                        'fallbackToLocalRsvp': 'true',
                        'sipRe11XxEnabled': 'Disabled',
                        'gClear': 'Disabled',
                        'sendRecvSDPInMidCallInvite': 'false',
                        'enableOutboundOptionsPing': 'true',
                        'optionsPingIntervalWhenStatusOK': 60,
                        'optionsPingIntervalWhenStatusNotOK': 120,
                        'deliverConferenceBridgeIdentifier': 'false',
                        'sipOptionsRetryCount': 6,
                        'sipOptionsRetryTimer': 500,
                        'sipBandwidthModifier': 'TIAS and AS',
                        'enableUriOutdialSupport': 'f',
                        'userAgentServerHeaderInfo': 'Send Unified CM Version Information as User-Agent Header',
                        'allowPresentationSharingUsingBfcp': 'false',
                        'scriptParameters': None,
                        'isScriptTraceEnabled': 'false',
                        'sipNormalizationScript': {
                            '_value_1': None,
                            'uuid': None
                        },
                        'allowiXApplicationMedia': 'false',
                        'dialStringInterpretation': 'Phone number consists of characters 0-9, *, #, and + (others treated as URI addresses)',
                        'acceptAudioCodecPreferences': 'On',
                        'mlppUserAuthorization': 'false',
                        'isAssuredSipServiceEnabled': 'false',
                        'enableExternalQoS': 'false',
                        'resourcePriorityNamespace': {
                            '_value_1': None,
                            'uuid': None
                        },
                        'useCallerIdCallerNameinUriOutgoingRequest': 'false',
                        'callerIdDn': None,
                        'callerName': None,
                        'callingLineIdentification': 'Default',
                        'rejectAnonymousIncomingCall': 'false',
                        'callpickupUri': 'x-cisco-serviceuri-pickup',
                        'rejectAnonymousOutgoingCall': 'false',
                        'videoCallTrafficClass': 'Mixed',
                        'sdpTransparency': {
                            '_value_1': 'Pass all unknown SDP attributes',
                        },
                        'allowMultipleCodecs': 'false',
                        'sipSessionRefreshMethod': 'Invite',
                        'earlyOfferSuppVoiceCall': 'Best Effort (no MTP inserted)',
                        'cucmVersionInSipHeader': 'Major And Minor',
                        'confidentialAccessLevelHeaders': 'Disabled',
                        'destRouteString': 'false',
                        'inactiveSDPRequired': 'false',
                        'connectCallBeforePlayingAnnouncement': 'false'
                    }
                    )
def addpt(client, name, description):
    client.addRoutePartition(routePartition=
        {
            'name': name,
            'description': description,
            'partitionUsage': 'General'
        }
        )
def addcss(client, name, description, *args):
    client.addCss(css=
        {
            'description': description,
            'members': {'member': args[0]},
            'partitionUsage': 'General',
            'name': name
        }
        )
def addacpl(client):
    client.addAudioCodecPreferenceList(audioCodecPreferenceList=
                    {
                        'name': 'AudioCodes_Codecs-acpl',
                        'description': 'AudioCodes Codec List - Lossy Codec List',
                        'codecsInList': {
                'codecNames': [
                    'G.711 A-Law 64k',
                    'G.711 U-Law 64k',
                    'G.729 8k',
                    'OPUS (6k-510k)',
                    'MP4A-LATM 128k',
                    'AAC-LD (MP4A Generic)',
                    'MP4A-LATM 64k',
                    'MP4A-LATM 56k',
                    'L16 256k',
                    'MP4A-LATM 48k',
                    'ISAC 32k',
                    'AMR-WB (7k-24k)',
                    'MP4A-LATM 32k',
                    'G.722 64k',
                    'G.722.1 32k',
                    'G.722 56k',
                    'G.722.1 24k',
                    'G.722 48k',
                    'MP4A-LATM 24k',
                    'G.711 U-Law 56k',
                    'G.711 A-Law 56k',
                    'ILBC 16k',
                    'G.728 16k',
                    'AMR (5k-13k)',
                    'GSM Enhanced Full Rate 13k',
                    'GSM Full Rate 13k',
                    'G.729b 8k',
                    'G.729ab 8k',
                    'G.729a 8k',
                    'GSM Half Rate 6k',
                    'G.723.1 7k'
                ]
            },
                     }
                    )
def listRegion(client, item):
    result = client.listRegion(**{
        'searchCriteria': {
            'name': item,
        },
        'returnedTags': {
            'name': ''
        }
    })

    result_dict = [result['return']['region'][eachresult]['name'] for eachresult in range(0, len(result['return']['region']))]


    return result_dict
def addRegion(client, name, member_reg):

    reg = listRegion(client, member_reg)
    reg_dict = [dict(zip((
        'regionName',
        'bandwidth',
        'videoBandwidth',
        'lossyNetwork',
        'codecPreference',
        'immersiveVideoBandwidth'
                          ), (
        reg[eachresult],
        '64 kbps',
        -1,
        'Use System Default',
        'AudioCodes_Codecs-acpl',
        -1
                            )))
        for eachresult in range(0, len(reg))]

    client.addRegion(region=
        {
            'name': name,
            'relatedRegions': {'relatedRegion': reg_dict}
        }
        )
def listPNTP(client, item):
    result = client.listPhoneNtp(**{
        'searchCriteria': {
            'ipAddress': item,
        },
        'returnedTags': {
            'ipAddress': ''
        }
    })

    result_dict = [result['return']['phoneNtp'][eachresult]['ipAddress'] for eachresult in range(0, len(result['return']['phoneNtp']))]


    return result_dict
def addDTG(client, name, member_pntp):

    pntp = listPNTP(client, member_pntp)
    pntp_dict = [dict(zip((
        'phoneNtpName',
        'selectionOrder'
                          ), (
        pntp[eachresult],
        eachresult
                            )))
        for eachresult in range(0, len(pntp))]

    client.addDateTimeGroup(dateTimeGroup=
        {
            'name': name,
            'timeZone': 'Etc/UTC',
            'separator': '-',
            'dateformat': 'Y-M-D',
            'timeFormat': '24-hour',
            'phoneNtpReferences': {
                'selectedPhoneNtpReference': pntp_dict}
            }
        )
def addDP(client, name):
    client.addDevicePool(devicePool=
        {
            'name': name,
            'dateTimeSettingName': DTG,
            'callManagerGroupName': CMG,
            'regionName': REG,
            'srstName': 'Disable'
            }
        )
def addSIPTr(client):
    client.addSipTrunk(sipTrunk=
        {
            'name': '{}{}CL_ACSBC_{}-tr'.format(REGION, COUNTRY, SBC_IP[2][0].split(".")[3]),
            'description': 'AudioCodes SBC - {}'.format(SBC_IP[2][0]),
            'product': 'SIP Trunk',
            'class': 'Trunk',
            'protocol': 'SIP',
            'protocolSide': 'Network',
            'callingSearchSpaceName': CSS[1]['name'].format(REGION),
            'devicePoolName': DP,
            'networkLocation': 'Use System Default',
            'locationName': 'Hub_None',
            'securityProfileName': STSP,
            'sipProfileName': SPI,
            'presenceGroupName': 'Standard Presence group',
            'destinations': {
                'destination': [
                    {
                        'addressIpv4': 'hasbc.{}.qbe.com'.format(COUNTRY.lower()),
                        'addressIpv6': None,
                        'port': 0,
                        'sortOrder': 1
                    }]},
            }
        )
def addRG(client):
    client.addRouteGroup(routeGroup=
        {
            'name': '{}_ACSBC-rg'.format(REGION),
            'distributionAlgorithm': 'Circular',
            'members': {
                'member': [
                    {
                        'deviceSelectionOrder': 1,
                        'deviceName': '{}{}CL_ACSBC_{}-tr'.format(REGION, COUNTRY, SBC_IP[2][0].split(".")[3]),
                        'port': 0,
                    }
                ]},
            }
        )
def addRL(client):
    client.addRouteList(routeList=
        {
            'name': '{}_ACSBC-rl'.format(REGION),
            'description': 'Route calls to AudioCodes SBC',
            'callManagerGroupName': CMG,
            'routeListEnabled': 'true',
            'members': {
                'member': [
                    {
                        'routeGroupName': '{}_ACSBC-rg'.format(REGION),
                        'selectionOrder': 1,
                        'calledPartyTransformationMask': None,
                        'callingPartyTransformationMask': None,
                        'digitDiscardInstructionName': None,
                        'callingPartyPrefixDigits': None,
                        'prefixDigitsOut': None,
                        'useFullyQualifiedCallingPartyNumber': 'Default',
                        'callingPartyNumberingPlan': 'Cisco CallManager',
                        'callingPartyNumberType': 'Cisco CallManager',
                        'calledPartyNumberingPlan': 'Cisco CallManager',
                        'calledPartyNumberType': 'Cisco CallManager',
                    }
                ]
            },
            'runOnEveryNode': 'false',
            }
        )
def addRP(client, pattern, description, partition):
    client.addRoutePattern(routePattern=
        {
            'pattern': pattern,
            'description': description,
            'routePartitionName': partition,
            'blockEnable': 'false',
            'destination': {
                'routeListName': '{}_ACSBC-rl'.format(REGION),
            },
            }
        )

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

    print("Creating Sip Trunk Security Profile {} for AudioCodes".format(STSP))
    addstsp(axl, STSP)

    print("Creating Sip Trunk Profile {} for AudioCodes".format(SPI))
    addspi(axl, SPI)

    for pt in PT:
        print("Creating Partitions {} for AudioCodes".format(pt['name'].format(REGION)))
        addpt(axl, pt['name'].format(REGION), pt['desc'])

    for css in CSS:
        name = css['name'].format(REGION)
        desc = css['desc']
        pt = css['pt'].split(":")
        pt_dict = [dict(zip(('routePartitionName', 'index'), (pt[index].format(REGION), index))) for index in range(0, len(pt))]

        print("Creating Calling Search Space {} for AudioCodes".format(name))
        addcss(axl, name, desc, pt_dict)

    print("Creating the Audio Codec Preference List for AudioCodes")
    addacpl(axl)

    print("Creating the Region for AudioCodes")
    addRegion(axl, REG, "%")

    print("Creating the Date/Time Group for AudioCodes")
    addDTG(axl, DTG, '%')

    print("Creating the Device Pool for AudioCodes")
    addDP(axl, DP)

    print("Creating the SIP Trunk for AudioCodes")
    addSIPTr(axl)

    print("Creating the Route Group for AudioCodes")
    addRG(axl)

    print("Creating the Route List for AudioCodes")
    addRL(axl)

    for rp in RP:
        print("Creating the Route Pattern {} for AudioCodes".format(rp['pattern']))
        addRP(axl, rp['pattern'], rp['desc'], rp['pt'].format(REGION))


    print('\n')

if __name__ == '__main__':
    main()