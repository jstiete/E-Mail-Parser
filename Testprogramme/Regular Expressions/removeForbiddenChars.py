#!/usr/bin/env python3
# Name:       removeForbiddenChars.py
# Kommentar:  verbotene Zeichen aus String entfernen
# Autor:      Jan Stietenroth, Nov, 2017
# Version:    0.1

import re
inputString="./home\\path soll hier. nicht stehen"

outputString, subs = re.subn(r'[/\\.]+', ' ', inputString)

print("input String: ", inputString)
print("subs: ", subs)
print("output String: ", outputString)
if subs>=1:
	print('[/\\.]', " Zeichen entfernt")
