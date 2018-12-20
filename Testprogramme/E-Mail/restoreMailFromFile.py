#!/usr/bin/env python3
# This Python file uses the following encoding: utf-8
# Name:       restoreMailFromFile.py
# Kommentar:  Das Script erzeugt ein email.message-Objekt aus einer byte-codierten Datei.
#             Gegenstück zu imap_to_file.py
# Autor:      Jan Stietenroth, Okt, 2017
# Version:    0.1

import email,os

fp=open(os.path.abspath("../InputData/mixed.msg"),"rb")
msg= email.message_from_binary_file(fp)
fp.close()

print(msg["SUBJECT"])
