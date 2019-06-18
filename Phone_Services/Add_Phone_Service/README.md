# Add a Phone Service - User guide
Used this script to add a phone service on the phone and phone profile (udp)
It will scan the cucm to find phone button template then replace it with a new phone button template. After that it will add the phone services.
It will also add the phone service as a softkey.
For the phone account (UDP), the script will log out and in the user in order to see the new phone service.
You will have to create credentials using Create_Login from [Login Credential](https://github.com/lpdescamps/Python/tree/master/credential)

## Dependencies
> cryptography module  
> zeep module  
> encrypted credential for CUCM using Create_Login script
> the template.csv file
> create phone button template and phone services

## template.csv
>Details explaining each column
* **Current_Template**: The current phone button template. This will help the script to find the device that needs to be changed.
* **New_Template**: The new template that we will apply on the device and assign the phone services to softkey.

## Add_Phone_Service.py
>Details explaining each variables
* **REGION**: Where is your cluster. See the README.md for Create_Login  
* **UDP**: You can narrow down to a specific User Device Profile or use the wildcard %
* **PHONE**: You can narrow down to a specific Phone or use the wildcard SEP%
* **TEMPLATE**: This csv file will have the current and new phone button template

under updatePhone()
To update the phone itself
* **telecasterServiceName**: The subscribed phone service name
* **name**: The phone service name. It's the same as the telecasterServiceName
* **urlLabel**: The button label you want to see on the phone
* **serviceNameAscii**: The button label you want to see on the phone

under updateUDP()
To update the phone account UDP
* **telecasterServiceName**: The subscribed phone service name
* **name**: The phone service name. It's the same as the telecasterServiceName
* **urlLabel**: The button label you want to see on the phone
* **serviceNameAscii**: The button label you want to see on the phone

under def main()
* **path**: The path where your credentials are stored. See the README.md for Create_Login
* **wsdl**: The path where your wsdl is stored.
* **platform**: The platform we are using. I assume it would be CUCM. See the README.md for Create_Login
* **role**: To define the API user's permission. Here we need full permission so rwx. See the README.md for Create_Login
