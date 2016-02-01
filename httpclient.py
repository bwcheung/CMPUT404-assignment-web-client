#!/usr/bin/env python
# coding: utf-8
# Copyright 2013 Abram Hindle
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib

def help():
    print "httpclient.py [GET/POST] [URL]\n"

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
	
    
    httpRequest = " HTTP/1.1 \r\n"
    user = "User-Agent: Mozilla/5.0 (Windows NT 6.1; WOW64; rv:43.0) Gecko/20100101 Firefox/43.0\r\n"
    accept = "Accept: text/html,application/xhtml+xml,application/xml,application/json\r\n"
    accept_lan = "Accept-Language: en-US,en;q=0.5\r\n"
    connection = "Connection: close\r\n"
    content_len = "Content-Length: "
    content_type = "Content-Type: application/x-www-form-urlencoded,application/json; \r\n"

    def get_host_port(self,url):
	self.url_parse = re.search("^(http[s]?:\/\/)?(([^:\/])+)(:\d+)?($|\/)([^#?\s]+)?(.*?)?(#[\w\-]+)?$", url)
	if (self.url_parse.group(3) is None):
		self.port_number = 80
	else:
		self.port_number = int(self.url_parse.group(3)[1:])
	return self.port_number

    def get_host(self,url):
	self.url_parse = re.search("^(http[s]?:\/\/)?(([^:\/])+)(:\d+)?($|\/)([^#?\s]+)?(.*?)?(#[\w\-]+)?$", url)
	if (self.url_parse.group(2) is None):
		raise Exception("invalid url")
	else:
		self.host_name = self.url_parse.group(2)
	return self.host_name

    def get_path(self, url):
	self.url_parse = re.search("^(http[s]?:\/\/)?(([^:\/])+)(:\d+)?($|\/)([^#?\s]+)?(.*?)?(#[\w\-]+)?$", url)
	if (self.url_parse.group(2) is None):
		return None
	else:
		self.path = self.url_parse.group(4)
		return self.path


    def connect(self, host, port):
        # use sockets!
	ClientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	ClientSocket.connect((host, port))
        return ClientSocket

    def get_code(self, data):
        lines = data.split('\r\n\r\n')
        header_lines = str.splitlines(lines[0])
        http_line = header_lines[0].split()
        return int(http_line[1])

    def get_headers(self,data):
        lines = data.split('\r\n\r\n')
        return lines[0]

    def get_body(self, data):
        lines = data.split('\r\n\r\n')
        return lines[1]

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return str(buffer)

    def GET(self, url, args=None):
	
	self.host_name = self.get_host(url)
	self.port_number = self.get_host_port(url)
	self.path = self.get_path(url)

	self.request = "GET /" + self.path + self.httpRequest + "HOST: " + self.host_name + ":" + str(self.port_number) + "\r\n" + self.user + self.accept + self.accept_lan + self.connection
	sock = self.connect(self.host_name, self.port_number)
	sock.sendall(self.request)
	self.response = self.recvall(sock)
	

        code = self.get_code(self.response)
        body = self.get_body(self.response)
	
	print(self.response)

        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        self.host_name = self.get_host(url)
	self.port_number = self.get_host_port(url)
	self.path = self.get_path(url)

        self.post_arg = ""
	if(args):
            self.post_arg = urllib.urlencode(args)

	self.request = "POST " + self.path + self.httpRequest + "HOST: " + self.host_name + ":" + str(self.port_number) + "\r\n" + self.user + self.accept + self.accept_lan + self.connection
	self.request = self.request + self.content_type + self.content_len + str(len(self.post_arg)) + "\r\n\r\n" + self.post_arg
	sock = self.connect(self.host_name, self.port_number)
	sock.sendall(self.request)
	self.response = self.recvall(sock)
	

        code = self.get_code(self.response)
        body = self.get_body(self.response)

	print(self.response)

        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__": 
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print client.command( sys.argv[2], sys.argv[1] )
    else:
        print client.command( sys.argv[1] )    
