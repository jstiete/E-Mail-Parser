#!/usr/bin/env python3
# This Python file uses the following encoding: utf-8
# Name:       HtmlToText.py
# Kommentar:  Entfernt HTML Tags und fügt "\n" ein.
# Autor:      Jan Stietenroth, Okt, 2017
# Version:    0.1

textStr = "Meine HTML-Nachricht\nKategorie: Foto\nAutor: Jan\nTag: Koala, Tulpen\n"

htmlStr = "<div dir=\"ltr\"><div><div><div>Meine HTML-Nachricht<br></div>Kategorie: Foto<br></div>Autor: Jan<br></div>Tag: Koala, Tulpen<br></div>"

def HtmlToText(message):
	import re
	newLine="(<br>)|(</p>)"
	expr="<[^>]*>"
	message = re.sub(newLine, "\n", message)
	message = re.sub(expr, "", message)
	return message


getHtmlToText(htmlStr)


