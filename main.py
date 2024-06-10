# Imports
import requests, json, time, os, websocket, threading, ssl, sys, select, datetime, subprocess, random; from colorama import Fore, Back, Style
if os.name == 'nt':
    import msvcrt

# Check Config
with open('config.json') as f:
    data = json.load(f)
token = data.get('token') or input("Enter your token: ").replace('"', '').replace("'","")
while requests.get('https://discord.com/api/v10/users/@me', headers={'Authorization': token}).status_code != 200:
    token = input("Invalid token, enter your token: ").replace('"', '').replace("'","")
data['token'] = token
data['message'] = data.get('message') or input("Enter message: ").replace('\\n','\n')
data['dmResponse'] = data.get('dmResponse') or input("Enter DM Autoresponse: ").replace('\\n','\n')
data['delay'] = data.get('delay') or input("Enter your delay (in seconds): ")
data['channels'] = data.get('channels') or input("Enter channel ID/s (separated by a space): ").split(" ")
data['status'] = status = data.get('status') or input("Enter status (online, idle, dnd, invisible): ").strip().lower()
data['webhook'] = data.get('webhook') or input("Enter webhook URL for logging (leave blank if you don't want webhook notifications): ") 
if data['webhook'] != '': data['webhookPing'] = data.get('webhookPing') or input("Enter role to ping for actions (leave blank if you don't want pings): ")
while status not in ("online", "idle", "dnd", "invisible"):status = input("Invalid status, enter status (online, idle, dnd, invisible): ").strip().lower();data['status'] = status
data['customStatus'] = data.get('customStatus') or input("Enter your custom status: ")
data['repeatBypass'] = data.get('repeatBypass') or input("Enable message repeat bypass? (y/n): ").strip().lower()
while data['repeatBypass'] not in ("y", "n"):data['repeatBypass'] = input("Invalid choice, enable message repeat bypass? (y/n): ").strip().lower()
with open('config.json', 'w') as f:
    json.dump(data, f)
    f.close()

# Message Sender
def sendMessage():
    global x
    start_time = time.time()
    stop_msg = Fore.RED + ("Press your 'escape' key to stop advertising!" if os.name == 'nt' else "Enter 'escape' to stop advertising!")
    print(stop_msg)
    while True:
        if (os.name == 'nt' and 'msvcrt' in sys.modules and msvcrt.kbhit() and msvcrt.getch() == b'\x1b') or (os.name != 'nt' and select.select([sys.stdin,],[],[],0.0)[0] and sys.stdin.readline().strip() == 'escape'):
            break
        channels = data.get('channels')
        for channel in channels:
            if data.get('repeatBypass') == 'y':
                repeatBypass = str(random.randint(752491546761342621526, 7834345876325483756245232875362457316274977135724691581387))
                requests.post(f'https://discord.com/api/v10/channels/{channel}/messages', headers={'Authorization': token}, json={'content': data.get('message')+'\n\n'+repeatBypass})
            else:
                requests.post(f'https://discord.com/api/v10/channels/{channel}/messages', headers={'Authorization': token}, json={'content': data.get('message')})
            elapsed_time = time.time() - start_time
            elapsed_time_str = f"[{datetime.timedelta(seconds=elapsed_time)}s]"
            if data.get('webhook'):requests.post(data.get('webhook'), json={'content': f'{elapsed_time_str} Sent message to channel <#{channel}>'})
            x+=1;subprocess.call('title="Discord Advertiser | Messages Sent: {}"'.format(x), shell=True)
        if data.get('webhook'):requests.post(data.get('webhook'), json={'content': f'{data.get("webhookPing")} Cooldown has been reached. Sleeping for {data.get("delay")} seconds.'})
        time.sleep(int(data.get('delay')))

# Channels Changer
def modifyChannels(operation):
    channel = input("Enter channel ID: ")
    if operation == 'add':
        data['channels'].append(channel)
        update_config(data, 'channels')
    elif operation == 'remove':
        data['channels'].remove(channel)
        update_config(data, 'channels')

# Delay Changer
def changeMessage():
    data['message'] = input("Enter your message: ")
    update_config(data, 'message')

# Delay Changer
def changeDelay():
    data['delay'] = input("Enter your delay (in seconds): ")
    update_config(data, 'delay')

 # DM Autoresponse Changer
def changeDMResponse():
    data['dmResponse'] = input("Enter your DM Autoresponse: ")
    update_config(data, 'dmResponse')

# Status Changer
def changeStatus():
    while True:
        status = input("Enter your status (online, idle, dnd, invisible): ")
        if status in ("online", "idle", "dnd", "invisible"):
            data['status'] = status
            update_config(data, 'status')
            break
        else:
            print("Invalid status. Please try again.")

# Custom Status Changer
def changeCustomStatus():
    data['customStatus'] = input("Enter your custom status: ")
    update_config(data, 'customStatus')

# Config Updater
def update_config(data, parameter):
    with open('config.json', 'w') as f:
        json.dump(data, f, indent=4)
        print(f"Changed {parameter} to {data[parameter]}")
        time.sleep(3)

# Onliner
def onlineLoop():
    while 1:
        online()
        time.sleep(30)
def online():
    status=data.get('status');customStatus=data.get('customStatus')
    ws=websocket.WebSocket();ws.connect('wss://gateway.discord.gg/?v=9&encoding=json');cool=json.loads(ws.recv());heartbeat=cool['d']['heartbeat_interval']
    auth={"op":2,"d":{"token":token,"properties":{"$os":"Windows 11","$browser":"Mozilla Firefox","$device":"Windows",},"presence":{"status":status,"afk":False},},"s":None,"t":None,};ws.send(json.dumps(auth))
    yes={"op":3,"d":{"since":0,"activities":[{"type":4,"state":customStatus,"name":"Custom Status","id":"custom"}],"status":status,"afk":False,}}
    def send_heartbeat():
        while 1:ws.send(json.dumps(yes));time.sleep(heartbeat/1000)
    threading.Thread(target=send_heartbeat).start()

# Auto DM Reply
def autoReply():
    check = requests.get('https://discord.com/api/v10/users/@me', headers={'Authorization': token})
    if check.status_code == 200:
        lol = json.loads(check.text)
        if lol['id'] != '0':
            a = requests.get('https://discord.com/api/v10/users/@me/channels', headers={'Authorization': token})
            b = json.loads(a.text)
            for i in b:
                try:
                    if i['type'] == int(1):
                        c = requests.get(f'https://discord.com/api/v10/channels/{i["id"]}/messages', headers={'Authorization': token})
                        d = json.loads(c.text)
                        if d[0]['author']['id'] != lol['id']:
                            requests.post(f'https://discord.com/api/v10/channels/{i["id"]}/messages', headers={'Authorization': token}, json={'content': data.get('dmResponse')})                        
                            if data.get('webhook'):requests.post(data.get('webhook'), json={'content': f'{data.get("webhookPing")} Auto DM Replied to {d[0]["author"]["username"]}#{d[0]["author"]["discriminator"]} ({d[0]["author"]["id"]})'})
                            break
                except:
                    pass
def autoReplyLoop():
    while 1:
        autoReply()

# DM Deleter / Closer
def deleteDMs():
    a = requests.get('https://discord.com/api/v10/users/@me/channels', headers={'Authorization': token})
    b = json.loads(a.text)
    for i in b:
        try:
            if i['type'] == int(1):
                requests.delete(f'https://discord.com/api/v10/channels/{i["id"]}', headers={'Authorization': token})
                break
        except:
            pass

# Clear console
def clearConsole():
    os.system('cls' if os.name == 'nt' else 'clear')

# Advertiser menu
def advertiser():
    while 1:clearConsole();choice=input(Fore.RED+"Advertiser:\n"+Fore.YELLOW+"1. Start advertiser\n2. Add channel\n3. Remove channel\n4. Change message\n5. Change delay\n6. Change DM Response\n7. Auto DM Response\n8. Leave\n");{'1':lambda:sendMessage(),'2':lambda:modifyChannels('add'),'3':lambda:modifyChannels('remove'),'4':lambda:changeMessage(),'5':lambda:changeDelay(),'6':lambda:changeDMResponse(),'7':lambda:(threading.Thread(target=autoReplyLoop).start(),print("Started Auto DM Responder")),'8':lambda:main()}.get(choice,lambda:print('Invalid choice'))();time.sleep(3)

# Onliner menu
def onliner():
    while True:clearConsole();choice = input(Fore.RED + "Onliner:\n" + Fore.YELLOW + "1. Start onliner\n2. Change status\n3. Change custom status\n4. Leave\n");{'1': lambda: (threading.Thread(target=onlineLoop).start(), print("Started onliner")),'2': changeStatus,'3': changeCustomStatus,'4':lambda:main()}.get(choice, lambda: print("Invalid choice"))();time.sleep(3)

# Main menu
def main():
    while 1:clearConsole();deleteDMs();choice=input(Fore.RED+"Home:\n"+Fore.YELLOW+"1. Advertiser\n2. Onliner\n3. Leave\n");{'1':advertiser,'2':onliner,'3':lambda:exit()}.get(choice,lambda:print('Invalid choice'))();time.sleep(3)

x=0;subprocess.call('title="Discord Advertiser | Messages Sent: {}"'.format(x), shell=True)
main()
