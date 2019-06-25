# Add - User guide
Add anything in CUCM.
You will to create credentials using Create_Login from [Login Credential](https://github.com/lpdescamps/Python/tree/master/credential)
The variables are mandatory.

## Dependencies
> cryptography module  
> zeep module  
> encrypted credential for CUCM using Create_Login script
> lxml if you want to pass xml string for vendorConfig

## add_{Global Settings}.py
>Details explaining each variables
* **REGION**: Where is your cluster. See the README.md for Create_Login  
under def main()
* **path**: The path where your credentials are stored. See the README.md for Create_Login
* **wsdl**: The path where your wsdl is stored.
* **platform**: The platform we are using. I assume it would be CUCM_DEV as you want to test the script in a none production. See the README.md for Create_Login
* **role**: To define the API user's permission. Here we need full permission so rwx. See the README.md for Create_Login

## add_Route_List.py
>Details explaining each variables
* **NAME**: The name you want to call the Route List.

## add_Route_Pattern.py
>Details explaining each variables
* **PATTERN**: The number for your Route Pattern.
* **RL**: The route list you want to use.

## add_Line.py
>Details explaining each variables
* **DN**: The number for your Route Pattern.
* **USE**: What the line will be used for. Usually Device

## add_Phone.py
>Details explaining each variables
* **DN**: The number for your Route Pattern
* **USE**: What the line will be used for. Usually Device
* **NAME**: The phone name. SEP + MAC address
* **MODEL**: The model of the phone. For example, Cisco 8845
* **DP**: Device Pool
* **CPP**: Common Phone Profile
* **LOC**: Location
* **UTRP**: Trusted Relay Point
* **PTN**: Phone Template Name
* **PPN**: Primary Phone Name
* **BIBS**: built-In Bridge Status
* **PCM**: packet Capture Mode
* **CO**: certificate Operation
* **DMM**: device Mobility Mode
* **DN**: The phone line. Must exist and is not mandatory but what's the point of a phone without a line?
* **DNPT**: The partition of the phone line. Not mandatory