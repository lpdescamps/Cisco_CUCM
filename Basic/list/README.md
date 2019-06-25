# List - User guide
List anything in CUCM. The LIST API does accept wildcard. You will need to be specific on what you want to return otherwise it will return 0.
You will to create credentials using Create_Login from [Login Credential](https://github.com/lpdescamps/Python/tree/master/credential)
The variables are mandatory.

## Dependencies
> cryptography module  
> zeep module  
> encrypted credential for CUCM using Create_Login script

## list_{Global Settings}.py
>Details explaining each variables
* **REGION**: Where is your cluster. See the README.md for Create_Login  
under def main()
* **path**: The path where your credentials are stored. See the README.md for Create_Login
* **wsdl**: The path where your wsdl is stored.
* **platform**: The platform we are using. I assume it would be CUCM_DEV as you want to test the script in a none production. See the README.md for Create_Login
* **role**: To define the API user's permission. Here we need read permission so r. See the README.md for Create_Login

## list_UDP.py
>Details explaining each variables
* **UDP**: The user device profile on your cucm. You can use % as wildcard
