#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import webbrowser
from http.server import HTTPServer, CGIHTTPRequestHandler


def start_server():
    webdir = '.'  # каталог с файлами HTML и подкаталогом cgi-bin для сценариев
    port = 9200  # http://servername/ если 80, иначе http://servername:xxxx/
    if len(sys.argv) > 1:
        webdir = sys.argv[1]  # аргументы командной строки
    if len(sys.argv) > 2:
        port = int(sys.argv[2])  # иначе по умолчанию ., 80
    print('webdir "%s", port %s' % (webdir, port))
    os.chdir(webdir)  # перейти в корневой веб-каталог
    srvraddr = ('', port)  # имя хоста, номер порта
    srvrobj = HTTPServer(srvraddr, CGIHTTPRequestHandler)
    try:
        srvrobj.serve_forever()
    except KeyboardInterrupt:
        pass
    srvrobj.server_close()


if __name__ == '__main__':
    webbrowser.open_new_tab("http://localhost:9200")
    start_server()
