#!/usr/bin/env python3
# This Python file uses the following encoding: utf-8
# Name:       generateTestmails.py
# Kommentar:  Generate testfiles for e-mail parser
# Autor:      Jan Stietenroth, Jan, 2018
# Version:    0.1


import os,email
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.utils import formatdate
from email import encoders

def send_mail(send_from, send_to, subject, text, files, content_types=['application/octet-stream']):

    msg = MIMEMultipart("mixed")
    body = MIMEMultipart("alternative")
    content = MIMEText(None, 'plain', 'utf-8')
    content.replace_header('content-transfer-encoding', 'quoted-printable')
    content.set_payload(text, 'utf-8')
    body.attach(content)
    msg.attach(body)
    msg['From'] = send_from
    msg['To'] = send_to
    msg['Date'] = email.utils.formatdate()
    msg['Subject'] = subject

    for myfile, content_type in list(zip(files, content_types)):
        content_type = content_type.split('/')
        content_maintype = content_type[0]
        content_subtype = content_type[1]
        part = MIMEBase(content_maintype, content_subtype)
        fo=open(myfile,"rb")
        part.set_payload(fo.read() )
        fo.close()
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(myfile))
        msg.attach(part)
    return msg


######## Main Schleife ###########
if __name__ == '__main__':
	# get files:
	zebra_jpg = os.path.abspath("../InputData/zebra.jpg")
	elephants_jpg = os.path.abspath("../InputData/elephants.jpg")
	giraffe_jpg = os.path.abspath("../InputData/giraffe.jpg")
	lion_jpg = os.path.abspath("../InputData/lion.jpg")
	lion_txt = os.path.abspath("../InputData/lion-text.txt")

	# generate a complete e-mail
	send_from='john@example.com'
	send_to='parser@example.com'
	subject='e-mail with two pictures'
	text=('I send you two images from elephant and giraffe:\n'
              'Category=Animals\n'
              'Event=Safari\n'
              'Tag=animals\n'
              'Author=John\n')
	files=[elephants_jpg, giraffe_jpg]
	content_types=['image/jpeg', 'image/jpeg']
	uid='complete'
	msg=send_mail(send_from, send_to, subject, text, files, content_types)
	f=open(uid+'.msg', "wb")
	f.write(msg.as_bytes())
	f.close()
	
	# generate two incomplete mails
	send_from='john@example.com'
	send_to='parser@example.com'
	subject='incomplete e-mail with one picture'
	text=('Here is the first part of my e-mail:\n'
              'Category=Animals\n'
              'Event=Safari\n')
	files=[zebra_jpg]
	content_types=['image/jpeg']
	uid='incomplete_1'
	msg=send_mail(send_from, send_to, subject, text, files, content_types)
	f=open(uid+'.msg', "wb")
	f.write(msg.as_bytes())
	f.close()

	send_from='john@example.com'
	send_to='parser@example.com'
	subject='Re: UID incomplete_1: incomplete e-mail with one picture'
	text=('Here are the missing keywords:\n'
              'Tag=Zebra\n'
              'Autor=John\n')
	files=[]
	content_types=[]
	uid='incomplete_2'
	msg=send_mail(send_from, send_to, subject, text, files, content_types)
	f=open(uid+'.msg', "wb")
	f.write(msg.as_bytes())
	f.close()

	# generate a complete e-mail with image and text
	send_from='john@example.com'
	send_to='parser@example.com'
	subject='e-mail with two pictures'
	text=('I also saw a lion:\n'
              'Category=Animals\n'
              'Event=Safari\n'
              'Tag=Tiere\n'
              'Author=John\n')
	files=[lion_jpg, lion_txt]
	content_types=['image/jpeg', 'text/plain']
	uid='mixed'
	msg=send_mail(send_from, send_to, subject, text, files, content_types)
	f=open(uid+'.msg', "wb")
	f.write(msg.as_bytes())
	f.close()
