#!/usr/bin/env python3
# This Python file uses the following encoding: utf-8
# Name:       analyseMail_from_File.py
# Kommentar:  Gibt die Struktur einer E-Mail aus einer bestimmten Datei aus.
#             !!! KEINE FEHLERBEHANDLUNG !!!
# Autor:      Jan Stietenroth, Dez, 2017
# Version:    0.1

import email,os

filename=os.path.abspath("../InputData/mixed.msg")

fp=open(filename,"rb")
msg= email.message_from_binary_file(fp)
fp.close()

print("##### E-Mail Analysieren: #####")
print(email.iterators._structure(msg))
print("---------------------------------")

for part in msg.walk():
	contentMaintype = part.get_content_maintype()
	contentSubtype = part.get_content_subtype()
	contentDisp = part.get("Content-Disposition")
	part_fileName = part.get_filename()
	keys = part.keys()
	print("Maintype:\t", contentMaintype)
	print("Maintype:\t", contentSubtype)
	print("Content-Disposition:\t", contentDisp)
	print("Filename:\t", part_fileName)
	print("Keys:\t", keys)
	print("---------------------------------")

