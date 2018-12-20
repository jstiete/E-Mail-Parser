#!/usr/bin/env python3
# This Python file uses the following encoding: utf-8
# Name:       analyseMail_from_IMAP.py
# Kommentar:  Ruft alle E-mails ab, die mit den Suchbegriffen übereinstimmen
#             und gibt deren Struktur aus.
#             !!! KEINE FEHLERBEHANDLUNG !!!
# Autor:      Jan Stietenroth, Dez, 2017
# Version:    0.1


import imaplib
import email


i=imaplib.IMAP4_SSL("imap.gmail.com")
i.login('meineMailAdresse@gmail.com', 'MEIN_PASSWORT')

i.select("INBOX")

########### hier die Suchworte definieren ################
result, uids=i.search(None, ['SINCE 01-Jan-2015', 'FROM alice@example.com'])


# Parse every Mail:
for uid in uids:
	print("##### E-Mail Analysieren: #####")
	
	result, email_data = i.uid("fetch", uid,"(RFC822)")
	raw_email = email_data[0][1]
	msg = email.message_from_bytes(raw_email)

	print(email.iterators._structure(msg))
	print("---------------------------------")

	for part in msg.walk():
		contentMaintype = part.get_content_maintype()
		contentSubtype = part.get_content_subtype()
		contentDisp = part.get("Content-Disposition")
		fileName = part.get_filename()
		keys = part.keys()

		print("Maintype:\t", contentMaintype)
		print("Maintype:\t", contentSubtype)
		print("Content-Disposition:\t", contentDisp)
		print("Filename:\t", fileName)
		print("Keys:\t", keys)
		print("---------------------------------")

i.logout()
