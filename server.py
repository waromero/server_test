#! /usr/bin/python
#--------------------------------------------------------------------
# Name   : server.py
# Purpose: Server classes
# Author : William A. Romero R.
# ID     : $Id: tsuite-v1.1, v 1.1 2009/02/03 17:17:35 agtk-dev Exp$
#--------------------------------------------------------------------
# -*- coding: UTF-8 -*-


import os
import sys
from socket import *
from threadpool import *
import time


##
#
# \brief Server class
# \author William A. Romero R.
# \version 1.1
# \date 2009/02/03
# \see Python Library Reference,
#      7.2 socket -- Low-level networking interface
#      http://www.python.org/doc/2.5.2/lib/module-socket.html
# \see http://docs.python.org/library/socket.html
class Server:
    ## Default constructor.
    # @param pPort     Port 
    # @param pNthreads Number of threads.
    # @param pPath     Server local path.
    def __init__(self, pPort, pNthreads, pPath):
                self.port = pPort
                self.num_threads = pNthreads
                self.path = pPath
                self.socket = None
                self.pool = None
                self.file = None
                self.file_counter = 0
                self.__session = "DcUvfgEx2aY"

                
    ## Server in Single mode.
    # @param self The object pointer
    def startSinlge(self):
        self.socket = socket(AF_INET, SOCK_STREAM)
        self.socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.socket.settimeout(10000)
        self.socket.bind(('',self.port))
        self.socket.listen(1)

        self.isRunning = True
        self.printHeader('default')

        while self.isRunning:
            connection, address = self.socket.accept()
            self.serve(connection, address)

    ## Server in ThreadPool mode.
    # @param self The object pointer
    def startThreadPool(self):
        self.socket = socket(AF_INET, SOCK_STREAM)
        self.socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.socket.settimeout(10000)
        self.socket.bind(('',self.port))
        self.socket.listen(1)

        self.pool = ThreadPool(self.num_threads)

        self.isRunning = True
        self.printHeader('tp')

        while self.isRunning:
            connection, address = self.socket.accept()
            # New client
            request = WorkRequest(self.serve, args=(connection, address), exc_callback=self.handle_exception)
            self.pool.putRequest(request)
            self.pool.poll()

    ## Process the client request.
    # @param self The object pointer
    # @param socket
    # @param client
    def serve(self, socket, client):
        print("Client: ", client)
        socket.settimeout(10000)
        isConnected = True

        while isConnected:
            request = socket.recv(5120)
            if not input: break

            print("REQUEST:", request)
            response = self.messageParser(request)
            print("RESPONSE:", response)

            if response == "Ready":
                socket.sendall(response)
                f = open(str(self.file_counter)+ "_"+self.file,"wb")
                data = socket.recv(5120)
                if not response: break
                f.write(data)
                f.close()
                self.file_counter += 1
                socket.sendall("Uploaded")
            if response != "Close":
                socket.sendall(response)
            else:
                isConnected = False

        socket.close()
        return

    ## Header server message.
    # @param self The object pointer
    # @param message Server execution mode
    def messageParser(self, pMessage):

        message_line = pMessage.split(" ")

        if message_line[0] == "LogOut":
            return "Close"

        if message_line[0] == "Time":
            return time.strftime('%m/%d/%Y %H:%M:%S')

        if message_line[0] == "Process":
            #process_result = knapsack(weights(210000), profits(210000), 10)
            for i in range(1,10000000): i=i*i
            return "Done"

        if message_line[0] == "ListFiles":
            return self.OnGetFiles()

        if message_line[0] == "GetFile":
            f = open(message_line[1], "rb")
            data = f.read()
            f.close()
            return data

        if message_line[0] == "PutFile":
            self.file = message_line[1]
            print("Waiting for " + self.file)
            return "Ready"

        return "WhatAreYouDoing"

    ## Header server message.
    # @param self The object pointer
    # @param mode Server execution mode
    def printHeader(self, mode):
        if mode == "tp": mode = "(Threadpool mode)"
        else: mode = "(Single mode)"
        print ("Application: TServer\n    Version: 1.1\n     Author: William A. Romero (wil-rome@uniandes.edu.co)\n")
        print("[Server " + mode + " on port %s ready]" % self.port)

    ## Files on server.
    # @param self The object pointer
    def OnGetFiles(self):
        result = ""
        for root, dirs, files in os.walk('./'):
           for name in files:
               filename = os.path.join(root, name)
               result += filename + ":"

        return result


    ## From threadpool module
    # this will be called when an exception occurs within a thread
    # this example exception handler does little more than the default handler
    def handle_exception(self, request, exc_info):
        if not isinstance(exc_info, tuple):
            # Something is seriously wrong...
            print ( request  )
            print ( exc_info )
            raise SystemExit
        print("**** Exception occured in request #%s: %s" % \
          (request.requestID, exc_info))

##
# *** MAIN ***
#
if __name__ == '__main__':

    try:

        port = int(sys.argv[1])
        mode = sys.argv[2]
        threads = int(sys.argv[3])

        server = Server(port,threads, "./")

        if mode == 'ThreadPool':
            server.startThreadPool()
        if mode == 'Single':
            server.startSinlge()

    except:
        print("Parameter missing!\n")
