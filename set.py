from configparser import ConfigParser
config_object = ConfigParser()

config_object["INFO"] = {
    "username": str(input("Username :")),
    "password": str(input("Password :"))
}

with open('config.conf', 'w') as conf:
    config_object.write(conf)