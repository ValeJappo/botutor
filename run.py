import os

print("RUN")
print("> 1 - bot.py")
print("> 2 - update_timestamp.py")
print("> 3 - set.py")
print("-"*10)
print("> 10 - pull")
print("> 11 - pull and start bot")
print("> 12 - edit crontab")
print("-"*10)
print("> ? - Exit")

ans=int(input(">> "))

if ans==1:
    os.system("python3 bot.py")

if ans==2:
        os.system("python3 update_timestamp.py")

if ans==3:
        os.system("python3 set.py")

if ans==10:
        os.system("git pull origin master")

if ans==11:
        os.system("git pull origin master && python3 bot.py")

if ans==11:
        os.system("crontab -e")