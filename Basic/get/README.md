# Get - User guide
Get anything in CUCM. The GET API doesnt accept wildcard like LIST API. You will need to be specific.
You will to create credentials using Create_Login from [Login Credential](https://github.com/lpdescamps/Python/tree/master/credential)
The variables are mandatory.

## Dependencies
> cryptography module  
> zeep module  
> encrypted credential for CUCM using Create_Login script

## get_{Global Settings}.py
>Details explaining each variables
* **REGION**: Where is your cluster. See the README.md for Create_Login  
under def main()
* **path**: The path where your credentials are stored. See the README.md for Create_Login
* **wsdl**: The path where your wsdl is stored.
* **platform**: The platform we are using. I assume it would be CUCM_DEV as you want to test the script in a none production. See the README.md for Create_Login
* **role**: To define the API user's permission. Here we need read permission so r. See the README.md for Create_Login

## get_UDP.py
>Details explaining each variables
* **UDP**: The exact user device profile that exist on your cucm.

## get_USER.py
>Details explaining each variables
* **USERID**: The exact enduser ID that exist on your cucm.

## get_Line.py
>Details explaining each variables
* **USERID**: The exact enduser ID that exist on your cucm.

* **DN**: An existing directory number on your cucm.
* **PARTITION**: An existing partition where your directory number belongs to on your cucm.