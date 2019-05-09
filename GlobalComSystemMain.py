import _thread as thread
import time
from time import gmtime, strftime
import socket
import urllib.request as urllib

allServers = {}
allPasswords = {}
allmsg = {}

def init(conn):
    initMsg = conn.recv(4096).decode()
    print("Attempted app connection to: " + str(initMsg))
    return initMsg

def createNewServer(appName, conn, addr):
    print("Creating new server for: " + str(appName))
    allServers[str(appName)] = [(conn, addr)]
    print("EXISTING SERVERS WITH RECORD IN SYSTEM: ")
    for server in allServers:
        print("\t" + str(server))
    print("="*20)

def addToServer(appName, conn, addr):
    allServers[str(appName)] += [(conn, addr)]

def get(appName, conn, addr):
    global allServers
    
    while True:
        try:
            msg = conn.recv(10000).decode()
            if msg.lower() == "give_me_all_the_servers_cause_i_am_the_admin":
                secretInfo = ""
                for server in allServers:
                    secretInfo += str(server) + "\n"
                send(conn, secretInfo)
            else:
                handleGroupSend(appName, addr, msg)
        except ConnectionResetError:
            print("Clearing old conn from server...")
            conn.close()
            break
            #TODO ^

def send(conn, msg):
    conn.send(msg.encode())
    
def handleGroupSend(appName, addr, msg):
    global allServers
    
    print("Sending to: " + str(appName) + " from: " + str(addr) + "...")
    for x in allServers[str(appName)]:
        if not (x[1] == addr):
            try:
                x[0].send(str(msg).encode())
            except OSError:
                #not working yet
                #del allServers[str(serverName)][x]
                print("Remove failed connection")
                
def handleNewConn(appName, conn, addr):
    get(appName, conn, addr)
    


pub_ip = urllib.urlopen("https://www.myglobalip.com").read().decode().split('<span class="ip">')[1].split("</span>")[0]
print(pub_ip)


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
hostIP = socket.gethostbyname(socket.gethostname())
print(hostIP)
port = 12345

#s.bind(("104.36.47.213",port))
s.bind(("0.0.0.0",port))
print(s.getsockname())
try:
    print(s.getpeername())
except OSError:
    print("WinError 10057: A request to send or receive data was disallowed because the socket is not connected and (when sending on a datagram socket using a sendto call) no address was supplied")    

threadNum = 0

while True:
    s.listen(0)
    conn,addr = s.accept()
    print("New connection from: " + str(addr))
    info = init(conn)
    
    try:
        appName = info.split("|")[0]
        #make some sort of login auth
        try:
            addToServer(appName, conn, addr)
        except KeyError:
            createNewServer(appName, conn, addr)
        thread.start_new_thread(handleNewConn, (appName, conn, addr, ))
        threadNum += 1
        
    except IndexError:
        print("False")
    

conn.close()
s.close()
