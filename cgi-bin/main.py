#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import cgi
import codecs
import glob
import html
import locale
import re
import sqlite3
import sys

sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

locale.setlocale(locale.LC_ALL, "")
# from myutils import check_file

form = cgi.FieldStorage()
QT = u''  # текст запроса
razd = '00'  # категория (раздел)
pozlist = '1'  # смещение выборки
podr = '0'  # форум (подраздел)
vv = '0'  # тип отображения результата
vers = ''  # дата бэкапа
shd = ''

if "querytext" in form.keys(): QT = form.getfirst("querytext")
if "category" in form.keys(): razd = form["category"].value
if "pozlist" in form.keys(): pozlist = form["pozlist"].value
if "podr" in form.keys(): podr = form["podr"].value
if "shd" in form.keys(): shd = "checked"


def check_file(file_name='*', status=False):
    if glob.glob(file_name): status = True
    return status


exist_tor = check_file('./DB/torrents.db3')  # проверка на наличие основной базы
exist_con = check_file('./DB/content.db3')  # проверка на наличие вспомогат. базы


def squery(fraze='', razdel='0'):
    sfq = ' FROM (torrent AS t inner join forum AS p on t.forum_id=p.code_forum) inner join category AS r on p.category_id=r.code_category WHERE size_b>0 '
    sfq += splitter(fraze)
    if razdel != '00':
        sfq += ' AND p.category_id=%s ' % (str(int(razdel)),)
    if podr != '0':
        sfq += ' AND p.code_forum=%s ' % (str(int(podr)),)
    if shd != 'checked':
        sfq += ' AND t.title NOT LIKE "%УДАЛЕНО%"'
    sfq += ' ORDER BY p.category_id asc, p.name_forum asc, t.file_id desc '
    return sfq


def splitter(text=''):
    ssq = ''
    for fraza in re.findall(r"[\'\"](.*?)[\'\"]", text):
        text = text.replace(fraza, '')
        if len(fraza) > 0: ssq += ' AND lower(title) LIKE "%' + fraza.lower() + '%"'
    for word in re.split(r'\s', text):
        word = re.sub(r'[\"\'\*\+\<\>?]', '', word)
        if len(
                word) > 0: ssq += ' AND (lower(title) LIKE "%' + word.lower() + '%" OR title LIKE "%' + word.capitalize() + '%")'
    return ssq


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
    return '{0:n}'.format(bsize)


def outlist(i):
    if i != int(pozlist):
        print(shtml.format(str(i), str(i)))
    else:
        print('<b>[%s]</b>' % str(i))


def bolder(text=''):
    patt = r'[\(\[{].*?[\)\]}]'
    text = '<b>%s</b>' % text
    for ss in re.findall(r'[\(\[{].*?[\)\]}]', text):
        text = text.replace(ss, '</b>%s<b>' % ss)
    text = text.replace('<b><b>', '<b>')
    text = text.replace('</b></b>', '</b>')
    return text


html_head = '''<!DOCTYPE html>
<html lang="ru">
<head>
<meta http-equiv="content-type" content="text/html; charset=utf-8">
<meta name="author" content="y3401">
<meta name="description" content="Локальная поисковая система InfoTor">
<title>Локальная поисковая система InfoTor</title>
<link rel="stylesheet" type="text/css" href="../infotor.css" />
</head><body>'''

html_script = '''<script>
    function setpar(pole,param) {
    document.getElementById(pole).value = param;
    document.form1.Submit1.click()}
</script>'''

html_form1 = '''<div class="layer2">
<form method="post" action="main.py" name="form1">
	<fieldset name="Group1">
	<legend>Параметры поиска</legend>
		<input name="querytext" type="text" placeholder="Введите ключевые слова" value="{}" 
         onchange='document.getElementById("poz").value ="1";' 
         style="width: 48%; height: 20px; margin-right: 10px; word-spacing: 5px; float: left;">
		<select name="category" onchange='document.getElementById("poz").value ="1";document.getElementById("podr").value ="0";' 
         style="width: 200px; height: 20px; margin-right: 5px;">
'<option value="00">...</option>\n'
'''
html_form2 = '\n'

if exist_tor == True:
    DB = sqlite3.connect('DB/torrents.db3')
    cur = DB.cursor()
    cur.execute('SELECT code_category,name_category FROM category WHERE load_category=1 ORDER BY code_category')
    r = cur.fetchall()
    for rr in r:
        razdel = ('0' + str(rr[0]))[-2:]
        if razd == razdel:
            html_form2 += ('<option selected value="%s">%s</option>\n' % (razdel, rr[1]))
        else:
            html_form2 += ('<option value="%s">%s</option>\n' % (razdel, rr[1]))
    cur.close()
    DB.close()

html_form3 = '''
</select>
<input type="checkbox" id="shd" name="shd" value="True" {}><label for="shd"><span>Показывать удаленные записи</span></label>
<input name="Submit1" type="submit" id="submit" value="Поиск" style="position: relative; float:right; width: 60px;">
<input name="pozlist" type="hidden" id="poz" value="{}">
<input name="podr" type="hidden" id="podr" value="{}"></fieldset></form></div>
<div class="layer3">'''.format(shd, pozlist, podr)

html_footer = '''
<div class="layer4" style="">
<table class="subtable" cellpadding="0" cellspacing="0">
<tr><td style="width:30%"><p>Найдено {} записи(ей)</p></td>
<td style="width:40%; text-align:center"><p>'''
shtml = '''<a href="#" onclick="setpar('poz',{})">[{}] </a>'''
html_end = '''<div class="back" style="display: none;"><a class="cl1" href="javascript:history.back()" title="Назад"></a></div>
<script>
	if ((document.getElementsByClassName('maintable').length===1) || (document.getElementsByClassName('menu').length>1)) {
    	var but_back=document.getElementsByClassName('back');
		but_back.item('style').style.display='block';
	}
</script>
</body></html>'''

numrec = 0

print('content­type: text/html\n')
print(html_head)
print(html_script)
print(html_form1.format(html.escape(QT)))
print(html_form2)
print(html_form3)

if exist_tor == True:
    DB = sqlite3.connect('DB/torrents.db3')
    cur = DB.cursor()
    if QT != '' or podr != '0':
        vv = '0'
        print('<table align="center" cellpadding="2" cellspacing="1" class="maintable">')

        sfq = squery(QT, razd)
        cur.execute('SELECT COUNT(file_id) ' + sfq)
        numrec = cur.fetchone()[0]  # общее количество записей по запросу
        if numrec > 0:
            offset = (int(pozlist) - 1) * 100
            cur.execute(
                'SELECT name_category, name_forum, file_id, hash_info, title, size_b, date_reg, code_forum' + sfq + ' LIMIT 100 OFFSET {};'.format(
                    offset))
            r = cur.fetchall()
            nom = 0 + offset  # номер в возвращаемом списке
            for srep in r:
                nom += 1
                print('<tr><td class="cell-1"><p><center>%s</center></p></td>' % (str(nom)))
                print('<td class="td-style4"><table class="subtable" cellpadding="0" cellspacing="0">')
                print('''<tr><td class="cell-l">{} - <a href="#" onclick="setpar('podr',{})">{}</a></td>'''.format(
                    html.escape(srep[0]), srep[7], html.escape(srep[1])))
                print('<td class="cell-r">Зарегистрировано: <b>%s</b></td></tr>' % (str(srep[6])))
                if exist_con == True:
                    print(
                        '''<tr><td colspan="2" class="cell-title"><a href="#" ONCLICK="window.open('info.py?tid={}','');return false;">{}</a></td></tr>'''.format(
                            str(srep[2]), bolder(srep[4])))
                else:
                    print('''<tr><td colspan="2" class="cell-title">{}</td></tr>'''.format(bolder(srep[4])))
                print(
                    '<tr><td class="cell-l">Размер: <span title="Точный размер: {}" style="cursor: help"><b>{}</b></span></td>'.format(
                        sepp(srep[5]), calc(srep[5])))
                print('<td class="cell-r"><span id="hsh0">%s</span></td></tr></table></td>' % (srep[3],))
                print(
                    '<td class="cell-2"><a href="magnet:?xt=urn:btih:%s"><img alt="Скачать" longdesc="Скачать по magnet-ссылке" src="../IMG/download40.png"></td></tr>' % (
                        srep[3],))
        print('</table>')

    elif razd != '00':
        vv = '1'
        cur.execute('SELECT COUNT(code_forum) FROM forum where category_id=%s' % int(
            razd))  # общее количество форумов по категории
        numrec = cur.fetchone()[0]

        sfq = 'SELECT code_forum,name_forum FROM forum WHERE category_id=%s ORDER BY name_forum' % int(razd)
        cur.execute(sfq)
        r = cur.fetchall()
        print('<ul>')
        for srep in r:
            print('''<li class="menu"><a href="#" onclick="setpar('podr',{})">{} </a></li>'''.format(srep[0], srep[1]))
        print('</ul>')

    elif QT == '' and razd == '00':
        vv = '2'
        sfq = squery(QT, razd)
        cur.execute('SELECT COUNT(file_id) FROM torrent')  # общее количество записей в базе
        numrec = cur.fetchone()[0]
        print('''<center><table>
    <tr width="800px" vertical-align="middle" ><td width="20%"></td><td height="300px" align="left">
    <p>Для поиска по локальной базе данных <b>InfoTor</b> введите ключевые фразы
    или слова и/или выберите вначале категорию, затем подраздел,
    а затем поисковые фразы или слова.</p>
    <p>Фразы выделяются двойными() или одиночными() кавычками. Между фразами и словами и между слов разделитель - пробел</p>
    <p>Например:</p> <p><pre class="ppre">&quot;Особенности национальной&quot; 'зимний период' комедия</pre></p>
    <p>Предпочтительнее использовать ключевые слова.</p>
    <p>Фразы используйте в том случае, если уверены в написании регистра букв фразы на русском языке (из-за отсутствия модуля ICU поисковый запрос чувствителен к регистру русских букв. Для латиницы же можно вводить как строчными, так и прописными буквами.)<p> 
    </td><td width="20%"></td></tr></table></center>''')
    # print(sfq)
    print('</div>')

    cur.execute('SELECT vers FROM vers')  # получить дату версии базы
    vers = cur.fetchone()[0]

    cur.close()
    DB.close()

print(html_footer.format(sepp(numrec)))
if vv == '0':
    if numrec > 0:
        smax = (numrec // 100) + 1
        L = range(0, smax)
        pcur = int(pozlist) + 1
        pmin = pcur - 5
        pmax = pcur + 4
        if pmin < 2: pmin = 2
        if pmax > smax: pmax = smax
        outlist(1)
        if pcur > 6: print(' ... ')
        for j in L[pmin:pmax]: outlist(j)
        if pcur < smax - 4: print(' ... ')
        if smax != 1: outlist(smax)
elif vv == '1':
    pass
else:
    print('База данных по состоянию на <b>%s.%s.%s</b>' % (vers[-2:], vers[4:6], vers[:4]))

print('''</p></td><td style="text-align:right; width=30%"><p>&copy;Y3401</p></td></tr></table></div>''')

if exist_tor == False:
    print('''<center><table>
    <tr width="800px" vertical-align="middle" ><td width="20%"></td><td height="300px" align="left">
    <p>Для работы в программе <b>InfoTor</b> необходимо скачать, разархивировать 
	и поместить в папку "/DB" файлы базы данных "torrents.db3" и "content.db3".</p>
    <p>Актуальный архив базы "INFOTOR_DB.7z" можно скачать с <a href="https://disk.yandex.ru/d/0TeTCC2TQ8UFxQ">Yandex Disk</a></p>
    <hr>
    </td><td width="20%"></td></tr></table></center>''')
print(html_end)
