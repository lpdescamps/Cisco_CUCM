# Find Speed Dial - User guide
For example, you have a speed dial across your company called Reception with number 123456. That number doesn't long exist and you need to know who has it from every phone and user device profile.
You will to create credentials using Create_Login from [Login Credential](https://github.com/lpdescamps/Python/tree/master/credential)

## Dependencies
> cryptography module  
> zeep module  
> encrypted credential for CUCM using Create_Login script  

## Remove_Speed_Dial.py
>Details explaining each variables
* **REGION**: Where is your cluster. See the README.md for Create_Login  
* **UDP**: You can narrow down to a specific User Device Profile or use the wildcard %
* **RMSD**: Remove Speed Dial. Put the number of the speed dial you want to find and remove
* **PHONE**: You can narrow down to a specific Phone or use the wildcard SEP%
under def main()
* **path**: The path where your credentials are stored. See the README.md for Create_Login
* **wsdl**: The path where your wsdl is stored.
* **platform**: The platform we are using. I assume it would be CUCM. See the README.md for Create_Login
* **role**: To define the API user's permission. Here we need read permission so r. See the README.md for Create_Login
