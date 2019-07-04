# UDP - User guide
For example, you could search the end user that is ldap and create UDP using informations from ldap.
You will have to create credentials using Create_Login from [Login Credential](https://github.com/lpdescamps/Python/tree/master/credential)

## Dependencies
> cryptography module  
> zeep module  
> encrypted credential for CUCM using Create_Login script  

## UDP_to_User.py
That script will scan the cucm and check if end user has a udp or not. If not, the script will check if a udp name matches the user ID. If it does it will return information. This script only reads the cucm, it won't write anything
>Details explaining each variables
* **REGION**: Where is your cluster. See the README.md for Create_Login  

under def main()
* **path**: The path where your credentials are stored. See the README.md for Create_Login
* **wsdl**: The path where your wsdl is stored.
* **platform**: The platform we are using. I assume it would be CUCM. See the README.md for Create_Login
* **role**: To define the API user's permission. Here we need read permission so r. See the README.md for Create_Login
