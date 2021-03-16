# Scanner - User guide
To search a data in any field you want.
You will have to create credentials using Create_Login from [Login Credential](https://github.com/lpdescamps/Python/tree/master/credential)

## Dependencies
> cryptography module  
> zeep module  
> encrypted credential for CUCM using Create_Login script  

## NumberScanner.py
This script will scan the cucm and will write it to a csv when the numbers you are searching for are found.

>Details explaining each variables
* **REGION**: Where is your cluster. See the README.md for Create_Login  
* **PATTERN**: If you want to target a specific range or number otherwise use % for everything
* **FILE**: where you want the csv file to be written and what name you want.
* **NBS**: what number to search for

under def main()
* **path**: The path where your credentials are stored. See the README.md for Create_Login
* **wsdl**: The path where your wsdl is stored.
* **platform**: The platform we are using. I assume it would be CUCM. See the README.md for Create_Login
* **role**: To define the API user's permission. Here we need read permission so r. See the README.md for Create_Login


## Find_DDI.py
This script will scan the cucm and will write it to a csv when a end user email address match in the csv file if the DN in csv is set to not known

>Details explaining each variables
* **REGION**: Where is your cluster. See the README.md for Create_Login  
* **USER**: The end user wildcard. For every users, use %
* **FILE**: where you want the csv file to be written and what name you want.
* **NEWFILE**: where you want the csv file to be written and what name you want.

under def main()
* **path**: The path where your credentials are stored. See the README.md for Create_Login
* **wsdl**: The path where your wsdl is stored.
* **platform**: The platform we are using. I assume it would be CUCM. See the README.md for Create_Login
* **role**: To define the API user's permission. Here we need read permission so r. See the README.md for Create_Login

csv FILE sample
Name,email,DN
Louis-Philippe Descamps,louis@noemail.com,not known

## Find_TP_fromPT.py
This script will scan the cucm and will write it to a csv when a Translation Pattern is in a specific partition

>Details explaining each variables
* **REGION**: Where is your cluster. See the README.md for Create_Login  
* **USER**: The end user wildcard. For every users, use %
* **PTLEG**: The partition you want to search (change line 186)
* **PTCIC**: The partition you want to search (change line 187)
* **FILE**: where you want the csv file to be written and what name you want.

under def main()
* **path**: The path where your credentials are stored. See the README.md for Create_Login
* **wsdl**: The path where your wsdl is stored.
* **platform**: The platform we are using. I assume it would be CUCM. See the README.md for Create_Login
* **role**: To define the API user's permission. Here we need read permission so r. See the README.md for Create_Login
