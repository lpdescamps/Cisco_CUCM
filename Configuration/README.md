# Configuration - User guide
Scripts that I used to configure different elements in CUCM
You will have to create credentials using Create_Login from [Login Credential](https://github.com/lpdescamps/Python/tree/master/credential)

## Dependencies
> cryptography module  
> zeep module  
> encrypted credential for CUCM using Create_Login script  

## AudioCodes_CUCM_Config.py
This script will create the different elements in order to route calls or receive calls from another pbx or sbc over a sip trunk.
The following will be created
* SIP Trunk Security Profile
* SIP Profile for trunk
* Calling search space and partition
* Audio Codec Preference List
    Note: If using API/Zeep. Modify the AxlSoap.xsd file to change maxOccurs from 30 to 31 for XAudioCodecPreferenceList, RAudioCodecPreferenceList, and UpdateAudioCodecPreferenceListReq
* Region
* Phone NTP References
* Date/Time Group
* Device Pool
* SIP Trunk
* Route Group
* Route List
* Route Pattern
>Details explaining each variables

I have split the variables into 2 groups.

* **Dynamic Variables - Do change**: You need to adjust this to your environment

* **REGION**: Where is your cluster. See the README.md for Create_Login  
* **COUNTRY**: What country to use for naming convention  
* **CMG**: Call Manager group. Usually match the order you are using on the other side (PBX, SBC, ...)  
* **SIPtr_SBCT_InACSBCAInt_pt**: What partitions we need in the CSS for inbound calls on the sip trunk.

* **# Static Variables - Do not change**: You dont need to change those unless you know what you are doing.

under def main()
* **path**: The path where your credentials are stored. See the README.md for Create_Login
* **wsdl**: The path where your wsdl is stored.
* **platform**: The platform we are using. I assume it would be CUCM. See the README.md for Create_Login
* **role**: To define the API user's permission. Here we need full permission so rwx. See the README.md for Create_Login
