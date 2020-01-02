# Call Routing - User guide
For example, you could search the end user that is ldap and create UDP using informations from ldap.
You will have to create credentials using Create_Login from [Login Credential](https://github.com/lpdescamps/Python/tree/master/credential)

## Dependencies
> cryptography module  
> zeep module  
> encrypted credential for CUCM using Create_Login script  

## Create_TP.py
This script will create a Translation Pattern (TP) based on information found in a csv file. It will also remove the forward to voicemail for callForwardNotRegistered if a DN exists

>Details explaining each variables
* **REGION**: Where is your cluster. See the README.md for Create_Login
* **CSS**: The calling search space to be used when creating the TP
* **PT**: The partition to be used when creating the TP
* **FILE**: The CSV file location
* **USERPT**: The user's DN partition

under def main()
* **path**: The path where your credentials are stored. See the README.md for Create_Login
* **wsdl**: The path where your wsdl is stored.
* **platform**: The platform we are using. I assume it would be CUCM. See the README.md for Create_Login
* **role**: To define the API user's permission. Here we need read permission so rwx. See the README.md for Create_Login

The csv file has a header. Below a sample
Name,email,DN
Louis-Philippe Descamps,louis@noemail.com,\+44123456789


## Delete_TP.py
This script will delete a Translation Pattern (TP) based on information found in a csv file. It will also add the forward to voicemail for callForwardNotRegistered if a DN exists

>Details explaining each variables
* **REGION**: Where is your cluster. See the README.md for Create_Login
* **CSS**: The calling search space to be used when creating the TP
* **PT**: The partition to be used when creating the TP
* **FILE**: The CSV file location
* **USERPT**: The user's DN partition

under def main()
* **path**: The path where your credentials are stored. See the README.md for Create_Login
* **wsdl**: The path where your wsdl is stored.
* **platform**: The platform we are using. I assume it would be CUCM. See the README.md for Create_Login
* **role**: To define the API user's permission. Here we need read permission so rwx. See the README.md for Create_Login

The csv file has a header. Below a sample
Name,email,DN
Louis-Philippe Descamps,louis@noemail.com,\+44123456789


## addORremove_TPcss.py
This script will add or remove a pt in a css

>Details explaining each variables
* **REGION**: Where is your cluster. See the README.md for Create_Login
* **CSS**: The calling search space to be found
* **PT**: The partition to be added or removed from to found CSS

under def main()
* **path**: The path where your credentials are stored. See the README.md for Create_Login
* **wsdl**: The path where your wsdl is stored.
* **platform**: The platform we are using. I assume it would be CUCM. See the README.md for Create_Login
* **role**: To define the API user's permission. Here we need read permission so rwx. See the README.md for Create_Login
