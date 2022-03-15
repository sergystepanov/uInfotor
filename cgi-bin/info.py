#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import cgi
import codecs
import sqlite3
import sys
import zlib

import modbbcode

sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

''''''


def calc(bsize=0):
    it = 0
    razmer = ['б', 'Кб', 'Мб', 'Гб', 'Тб']
    while bsize > 1024:
        bsize /= 1024
        it += 1
    if it > 0:
        p = str(bsize).split(".")
        return ('{} ' + razmer[it]).format(round(bsize, 2))
    else:
        return ('{} ' + razmer[0]).format(int(bsize))


def sepp(bsize=0):
    s = str(bsize)
    return s[-12:-9] + ' ' + s[-9:-6] + ' ' + s[-6:-3] + ' ' + s[-3:]


def sel_content(id_tor):
    DB = sqlite3.connect('DB/content.db3')
    cur = DB.cursor()
    cur.execute('SELECT cont FROM contents WHERE tid=?;', (id_tor,))
    r = cur.fetchone()
    if r:
        S = zlib.decompress(r[0])
        result = modbbcode.bbcode2html(S.decode('utf-8'))
    else:
        result = '''<h3 style="text-align:center">Запись отсутствует</h3>'''
    cur.close()
    DB.close()
    return result


def exist_table():
    DB = sqlite3.connect('DB/content.db3')
    cur = DB.cursor()
    cur.execute("SELECT count(*) FROM sqlite_master WHERE name='files';")
    r = cur.fetchone()
    cur.close()
    DB.close()
    if r[0] == 1:
        return "block"
    else:
        return "none"


form = cgi.FieldStorage()
tid = 0

if "tid" in form.keys():
    tid = int(form.getfirst("tid"))

DB = sqlite3.connect('DB/torrents.db3')
cur = DB.cursor()
cur.execute('''SELECT name_category, name_forum, hash_info, title, size_b, date_reg
    FROM (torrent AS t inner join forum AS p on t.forum_id=p.code_forum) inner join category AS r on p.category_id=r.code_category
    WHERE file_id=%s;''' % tid)
r = cur.fetchone()
cur.close()
DB.close()

if exist_table() == 'block':
    global fl
    fl = []
    DB = sqlite3.connect('DB/content.db3')
    cur = DB.cursor()
    try:
        cur.execute('SELECT tid, name, size, ord FROM files WHERE tid=%s;' % tid)
        rr = cur.fetchall()
        if rr:
            fl = rr
            # list_files = zlib.decompress(rr[0])
            # fl = list_files.decode('utf-8')
            # fl = eval(fl)
        else:
            result = '''<h3 style="text-align:center">Запись отсутствует</h3>'''
    except sqlite3.OperationalError:
        print('error')
    cur.close()
    DB.close()

html_head = '''<!DOCTYPE HTML>
<html land="ru"><head>
<meta http-equiv="content-type" content="text/html; charset=utf-8">
<meta name="author" content="y3401">
<meta name="description" content="Локальная поисковая система InfoTor">
<title>%s</title>
<link rel="stylesheet" type="text/css" href="../infotor.css" />
</head><body>
<script>
    function showBlock(t) {
           var elStyle = document.getElementById(t).style;
           elStyle.display = (elStyle.display == 'none') ? '' : 'none'}
</script>
<div class="layer6">
'''

print('content-type: text/html\n')
if r:
    print(html_head % (r[3]))
    print('<table class="subtable"><tr>')
    print('<td style="vertical-align:top;"><p class="info">{}<br />&rArr; {}</p></td>'.format(r[0], r[1]))
    print(
        '<td style="width: 18%; vertical-align:middle"><p class="info" title="{} байт">Размер: <b>{}</b></p></td>'.format(
            sepp(r[4]), calc(r[4])))
    print(
        '<td style="width: 10%; vertical-align:middle" align="right"><div class="folder" style="display:{}"><div '
        'class="files"><h2 style="margin-bottom:3px">Список файлов:</h2>'.format(
            exist_table()))
    print('''<table class="subtable">''')
    if len(fl) > 0:
        offset = 1

        if int(fl[0][2]) == 0:
            print(
                '''<tr><td colspan=2 style="background-color:#bad5cc; padding-left: {}em"><img class="td-folder" 
                src="../IMG/opened-folder.png"><h4 style="display:inline">{}</h4></td></tr>'''.format(
                    offset, fl[0][1]))
            cat = "f"
        else:
            print(
                '''<tr><td style="padding-left: {}em"><img class="td-file" src="../IMG/file.png">{}</td><td 
                align="right" style="padding-right: 1em;width: 7em;" title="{} байт">{}</td></tr>'''.format(
                    offset + 1, fl[0][1], sepp(fl[0][2]), calc(int(fl[0][2]))))
            cat = "d"
            offset += 1
        for item in fl[1:]:
            if int(item[2]) == 0:
                if cat != "d":
                    offset += 2
                if cat == "f":
                    offset -= 2
                print(
                    '''<tr><td colspan=2 style="background-color:#d1e6df; padding-left: {}em"><img class="td-folder" 
                    src="../IMG/opened-folder.png"><h4 style="display:inline">{}</h4></td></tr>'''.format(
                        offset + 1, item[1]))
                cat = "d"
            else:
                print(
                    '''<tr><td style="padding-left: {}em"><img class="td-file" src="../IMG/file.png">{}</td><td 
                    align="right" style="padding-right: 1em; width: 7em;" title="{} байт">{}</td></tr>'''.format(
                        offset + 2, item[1], sepp(item[2]), calc(int(item[2]))))
                cat = "f"
    print('''</table><br>''')
    print('</div></div>')
    print('<td style="width: 15%; vertical-align:middle" align="right"><p class="info"><b>{}</b> {}</p></td>'.format(
        r[5][:10], r[5][11:]))
    print(
        '<td style="width: 7%;">'
        '<a href="magnet:?xt=urn:btih:{}&tr=http%3A%2F%2Fbt3.t-ru.org%2Fann%3Fmagnet">'
        '<img src="../IMG/download40.png" align="right" alt="Скачать" title="Скачать по magnet-ссылке">'
        '</a>'
        '</td></tr></table></div>'.format(r[2]))
    print('<div class="layer3" style="height: 91vh">')
    print('<div class="layer5"><h2>{}</h2></div>'.format(r[3]))
else:
    print(html_head % '')
    print('''<div class="layer3" style="height: 91vh">''')
print('''<div class="post_body">''')
print(sel_content(tid))
print('''<br /><br /></div></div>
<div class="layer4">
<table class="subtable" cellpadding="0" cellspacing="0">
<tr><td width="30%"><p>...</p></td>
<td width="60%" align="center"><p>...</p></td>
<td style="text-align:right"><p style="margin-top:5px">&copy;Y3401</p></td>
</tr></table></div>''')
print('''<div class="clo"><a class="cl1" href="javascript:window.close()" title="Закрыть"></a></div></body></html>''')
