__author__ = 'YutongGu'

import socket
import threading
import time

#class is meant for transmitting to a remote computer via sockets over wifi
#will automatically try to connect if disconnected
#print statements make the code pretty self explanatory
class Connector:
    try:
        HOST=socket.gethostbyname('GuLaptop.yutong.gu.com')
    except:
	print 'Failed to resolve hostname, going with default'
        HOST='192.168.1.110'

    #comment this out eventually
#<<<<<<< HEAD
    # HOST='192.168.118.1'
#=======
    #useful resource for connecting using DNS: http://unix.stackexchange.com/questions/16890/how-to-make-a-machine-accessible-from-the-lan-using-its-hostname
    #HOST='192.168.1.109'
#>>>>>>> b5ffdc2ff4b452cd2e4c742a4772872d619ff8c6

    PORT=13000
    message=''
    connected=False
    statusChanged=False
    input=''
    TIMEOUT=1
    sock=object
    quit=False

    def __init__(self, data):
        print 'Host ip set as: '+self.HOST
        self.datalist = data
        try:
            thread1 = threading.Thread(target=self.startclient, args=())
            thread1.daemon = True
            thread1.start()
        except:
            print('failed to thread startclient')
        pass

    def __del__(self):
        if ~self.quit:
            print "PiConnector deconstructed"
            self.closeall()
        pass

    def startclient(self):
        #set up socket
        print "starting client"

        while self.connected==False and ~self.quit:

            print "****************Setting up socket*******************"
            try:
                #create an AF_INET, STREAM socket (TCP)
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
                self.sock.settimeout(self.TIMEOUT)
            except:
                print 'Failed to create socket'
            self.connect()
            if self.quit:
                break
            time.sleep(10)


    def connect(self):
        try:
            print('***********Trying to connect to '+self.HOST+'*************')
            self.sock.connect((self.HOST,self.PORT))
            self.connected = True
            self.statusChanged=True
            print('***************Connection established***************')
        except:
            self.sock.close()
            del self.sock
            self.sock=None
            print('***************Connection failed********************')
            pass

        try:
            thread2 = threading.Thread(target=self.transmitData, args=())
            thread2.daemon = True
            thread2.start()
        except:
            print('failed to thread transmitData')

    def transmitData(self):
        failedAttempts=0

        while self.connected and ~self.quit:
            message = ""
            try:
                polling=self.sock.recv(16)
            except socket.timeout:
                print("Connection timed out. Disconnected")
                thread3 = threading.Thread(target=self.closeserv, args=())
                thread3.daemon = True
                thread3.start()
                break
            except socket.error:
                print"error"
                thread3 = threading.Thread(target=self.closeserv, args=())
                thread3.daemon = True
                thread3.start()
                break

            if polling == "poll":
                for x in self.datalist.value_names:
                    message = message+x+':'+str(self.datalist.data[x])+';'
                message = message[:-1]
                if failedAttempts >= 50:
                    self.closeserv()
                    break
                try:
                    self.sock.sendall(message)
                except:
                    print('sending data failed.')
                    failedAttempts += 1
            else:
                print"error"
                thread3 = threading.Thread(target=self.closeserv, args=())
                thread3.daemon = True
                thread3.start()
                break
            
    def closeserv(self):
        if self.connected:
            try:
                self.sock.sendall("quit")
            except:
                print 'connection already closed'
            self.sock.close()
            self.connected=False
            self.statusChanged=True
            print "connected set to false***"
            if ~self.quit:
                print "starting client from closeserv"
                self.startclient()

    def closeall(self):
        try:
            self.sock.sendall("quit")
        except:
            print 'couldnt communicate to telemetry'
        self.quit = True
        print "quit set to true***"
        if self.sock is not None:
            self.sock.close()



