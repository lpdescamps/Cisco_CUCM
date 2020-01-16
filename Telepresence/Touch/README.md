# Touch - User guide
Any script regarding the macro and UI on the touch panel

You will have to create credentials using Create_Login from [Login Credential](https://github.com/lpdescamps/Python/tree/master/credential)

## Dependencies
> cryptography module  
> zeep module  
> encrypted credential for CUCM using Create_Login script  

## codec_ui-macro.py
This script will search for SIP Telepresence codec on the cucm, then 
- check if macro compatible
- If compatible, enable macro, upload macro, upload inroom and add DNS ip
it will also create a csv file with codecs
This script can do a dry run to see what device will be affected by that script and it will ask you to confirm if dry run is disable

>Details explaining each variables
* **DRY_RUN**: "enable" or "disable". If disable it will make the change. If enable, you will be prompted to confirm by YES or NO
* **REGION**: Where is your cluster. See the README.md for Create_Login  
* **IPS**: If you have an IP range or use the will card ['*'] or ['10.1.1.1'] or ['10.1.1.*'] or ['10.1.1.1', '10.2.2.2']
* **DNS**: the IP for DNS server
* **NAME**: The name you want to use for macro
* **JS_MACRO**: The macro file. The file is in macro subfolder
* **XML_INROOM**: The xml file. The file is in ui subfolder
* **CSV_FILE** = The output csv file location

under def main()
* **path**: The path where your credentials are stored. See the README.md for Create_Login
* **wsdl**: The path where your wsdl is stored.
* **platform**: The platform we are using. I assume it would be CUCM. See the README.md for Create_Login
* **role**: To define the API user's permission. Here we need read permission so r. See the README.md for Create_Login
* **codec_platform**: The platform we are using. I assume it would be codec. See the README.md for Create_Login
* **codec_role**: To define the API user's permission. Here we need read permission so rwx. See the README.md for Create_Login
