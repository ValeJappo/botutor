from configparser import ConfigParser
config_object = ConfigParser()

config_object["INFO"] = {
    "username": str(raw_input("Username :")),
    "password": str(raw_input("Password :"))
}

with open('config.conf', 'w') as conf:
    config_object.write(conf)


