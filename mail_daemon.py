#!/usr/bin/python
# coding=utf-8
import poplib
from email import parser
from email.header import decode_header
import re

import os
import sys

import mail_daemon_settings

sys.path.append(mail_daemon_settings.path_to_instruments)

import instruments
instruments.app.config.from_pyfile(mail_daemon_settings.path_to_settings)

from subMarks.core import resolve_url
from subMarks import database

pop_conn = poplib.POP3_SSL(mail_daemon_settings.mail_server)
pop_conn.user(mail_daemon_settings.mail_username)
pop_conn.pass_(mail_daemon_settings.mail_password)
#Get messages from server:
messages = [pop_conn.retr(i) for i in range(1, len(pop_conn.list()[1]) + 1)]
# Concat message pieces:
messages = ["\n".join(mssg[1]) for mssg in messages]
#Parse message into an email object:
messages = [parser.Parser().parsestr(mssg) for mssg in messages]
for message in messages:
    if mail_daemon_settings.safe_receive_address in message['from']:

        if message['Content-Type'][:4] == 'text':
            text = message.get_payload() #plain text messages only have one payload, html gets more
        else:
            text = message.get_payload()[0].get_payload() #plain text messages only have one payload, html gets more
        
        url = re.search(r"""((?:[a-z][\w-]+:(?:/{1,3}|[a-z0-9%])|www\d{0,3}[.]|[a-z0-9.\-]+[.‌​][a-z]{2,4}/)(?:[^\s()<>]+|(([^\s()<>]+|(([^\s()<>]+)))*))+(?:(([^\s()<>]+|(‌​([^\s()<>]+)))*)|[^\s`!()[]{};:'".,<>?«»“”‘’]))""", text, re.DOTALL).group()
        
        url = resolve_url(url)

        subject = decode_header(message['subject'])[0]
        if subject[1]:
            bookmark_title = subject[0].decode(subject[1]).encode('ascii', 'ignore')
        else:
            bookmark_title = subject[0]
        
        project = message['to'].split('@')[0].split('+')
        if len(project) > 1:
            database.save_bookmark(url, bookmark_title, database.get_project_id(project[1]))
        else:
            database.save_bookmark(url, bookmark_title)
    
pop_conn.quit()
