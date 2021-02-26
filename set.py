from configparser import ConfigParser
config_object = ConfigParser()
config_object.read("config.conf")

print("SETTINGS")
print("> 1 - User")
print("> 2 - Site")
print("> 0 - Exit")
ans=-1
while ans>3 or ans<0:
    ans=int(input(">> "))

if ans==1:
    info=config_object["INFO"]
    info["username"]=str(input("Username :")),
    info["password"]=str(input("Password :"))

if ans==2:
    config_object["INFO"]["site"]=str(input("Site (language code) :")) 

with open('config.conf', 'w') as conf:
    config_object.write(conf)   