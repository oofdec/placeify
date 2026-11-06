import sys, os, threading
import socket

running = True


def server_manager(s,add_song_callback):
    global running

    while running:
        try:
            cli, _ = s.accept()

            cmd = cli.recv(1024).decode()
            if os.path.exists(cmd):
                print("receiveing signal to add path:"+cmd)
                add_song_callback(cmd)
            else:
                add_song_callback("ping")

            cli.close()
        except socket.timeout:
            pass

    s.close()
    print("socket closed")

def main(app_arguments, add_song_callback):
    s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    s.settimeout(1)

    try:
        s.bind(("127.0.0.1", 58391))
        s.listen(1)
    except OSError:
        s = None

    openwith = False
    if len(app_arguments) > 1:
        openwith = True

    #check for exit first
    if not s and not openwith: #if server is already running, and not opened with
        s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        s.settimeout(1)

        s.connect(("localhost",58391))
        s.send("ping".encode())
        sys.exit(-1)


    #if no server running, always create one.
    if s:
        threading.Thread(target=server_manager,args=(s,add_song_callback,)).start()
    

    #then determine open with
    if openwith:
        if s:
            add_song_callback(app_arguments[1])
        else:
            s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            s.settimeout(1)

            s.connect(("localhost",58391))
            s.send(str(app_arguments[1]).encode())
            sys.exit(-1)
    

    #this is SOOOOO MUCH CLEANER you dont understand for i have reach peak logic
        
        
