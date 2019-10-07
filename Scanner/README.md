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
