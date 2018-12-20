#!/usr/bin/env python3
# This Python file uses the following encoding: utf-8
# Name:       imapToFile.py
# Kommentar:  Das Script ruft ungelesene Mails aus einem IMAP Postfach ab und 
#             speichert sie als Byte-Strom in einer Datei.
# Autor:      Jan Stietenroth, Okt, 2017
# Version:    0.1

import imaplib
from pprint import pprint
import email

print("los gehts")
i=imaplib.IMAP4_SSL("imap.gmail.com")
print("Verbindung steht")

try:
	i.login('meineMailAdresse@gmail.com', 'MEIN_PASSWORT')
except imaplib.IMAP4.error:
	print("Login fehlgeschlagen!")
	exit()

typ, data = i.list()
#print("Response Code:", typ)
#print("Ordnerliste")
#pprint(data)
i.select("INBOX")

result, data=i.uid("SEARCH", "UNSEEN")
print("Ungelesene Nachrichten: ", data)

print("Den zweiten Programmteil mit gueltiger UID aufrufen!")
exit()
#Folgende anpassen und das exit auskommentieren
uid="13964"
result, email_data = i.uid("fetch", uid,"(RFC822)")
raw_email = email_data[0][1]
msg = email.message_from_bytes(raw_email)

name = uid+".txt"
f=open(name, "wb")
f.write(msg.as_bytes())
f.close()

print("Programm Ende")
