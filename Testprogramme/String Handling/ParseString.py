#!/usr/bin/env python3
# This Python file uses the following encoding: utf-8
# Name:       ParseString.py
# Kommentar:  Veschiedene Tests um einen String zu parsen
# Autor:      Jan Stietenroth, Okt, 2017
# Version:    0.1
#(([\w-]+(,? ?))+[\w-]) --> suche 1..n (1...n Buchstaben/Zahlen & '-', denen 0..1 komma und 0..1 leerzeichen folgen) mit anschließenden 1..n buchstaben&-
# ([\w-]+(,? ?)(?=[\w-]))+[\w-]+

htmlStr = "<div dir=\"ltr\"><div><div><div>Meine HTML-Nachricht<br></div>Kategorie: Foto<br></div>Autor: Jan<br></div>Tag: Koala, Tulpen<br></div>"
textStr = "Meine HTML-Nachricht\nmeineKategorie: Foto \nAutor: Jan\nmeineStichworte: Koala, Tulpen\n"

message=textStr

from ParseKeys import myParseConfig
dataName=0
dataOpt=1
dataValue=2
data=myParseConfig()
for value in data.values():
	value.append(None)
#data={key0:[Name, Optional, Wert], key1:[Name, Optional, Wert],...}
print("Eingelesene Konfiguration: ",data)
dataNames = [item[dataName] for item in data.values()]
dataKeys = list(data.keys())

# abgewandelter Parser aus tokenizer.py
import re
aktKey=""
lastKind=""
token_specification = [
   ('ASSIGN',  r'[:=]'),                   # Assignment operator ':' or '='
   ('END',     r'[;\n]'),                  # Statement terminator
   ('ID',      r'(([\w-]+(,? ?))+[\w-])'), # Identifiers (one or more words)
   ('SKIP',    r'[ \t]+'),                 # Skip over spaces and tabs
   ('MISMATCH',r'.'),                      # Any other character
]
tok_regex = '|'.join('(?P<%s>%s)' % pair for pair in token_specification)
for matchObj in re.finditer(tok_regex, message):
	kind = matchObj.lastgroup
	value = matchObj.group(kind)
	print("Kind:", kind)
	print("Value:", repr(value))
	print("lastKind:",lastKind)
	if kind == 'SKIP':
		continue
	elif kind == 'MISMATCH':
		raise RuntimeError('{} unexpected on line' %(value))
	elif kind == 'ID':
		if value in dataNames:
			i=dataNames.index(value)
			aktKey=dataKeys[i]
			print("i:",i)
		elif lastKind == "ASSIGN" and aktKey!="":
			print("aktKey:",aktKey)
			data[aktKey][dataValue]=value
			aktKey = ""
			print("Assign")
	elif kind == 'END':
		aktKey=""
	lastKind=kind
print(data)
