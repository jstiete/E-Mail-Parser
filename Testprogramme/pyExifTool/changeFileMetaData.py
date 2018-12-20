#!/usr/bin/env python3
# Name:       changeFileMetaData.py
# Kommentar:  Metadaten von einem Bild ädern
# Autor:      Jan Stietenroth, Nov, 2017
# Version:    0.1

import os
src=open(os.path.abspath("../InputData/zebra.jpg"), "rb")
dest=open(os.path.abspath("./new.jpg"), "wb")
image=src.read()
dest.write(image)
src.close()

import exiftool
import os
with exiftool.ExifTool() as et:
	#Metadaten vom unveränderten Bild auslesen
	md = et.get_metadata("new.jpg")
	print("## alte Metadaten:")	
	key="EXIF:Artist"
	print("%s\t:\t%s"%(key,md[key]))

	#Metadaten überschreiben
	command="-Artist=Fotograf äöü".encode() # ist das selbe wie .encode("utf-8") --> utf-8 ist default wert
	# -m: unterdrück minor-errors -> Überschreiben von Werten
	# -overwrite_original: Lege kein Backup an
	et.execute(command, b"-m", b"-overwrite_original", b"./new.jpg")
	md = et.get_metadata("new.jpg")
	print("## neue (überschriebene) Metadaten:")
	md = et.get_metadata("new.jpg")
	print("%s\t:\t%s"%(key,md[key]))

	#einen neuen (in exiftool bekannten) Tag anlegen
	print("## neuen Tag \'XP Comment\' anlegen:")
	command="-XPComment=Das Zebra hat ein"	
	et.execute(command.encode("utf-8"), b"-m", b"-overwrite_original", b"./new.jpg")
	key="EXIF:XPComment" #Gruppe:TAG
	md = et.get_metadata("new.jpg")
	print("%s\t:\t%s"%(key,md[key]))

	#diesen Tag ergänzen:
	print("\'XP Comment\' ergänzen:")
	et.execute(b"-XPComment<$XPComment gestreiftes Fell", b"-m", b"-overwrite_original", b"./new.jpg")
	md = et.get_metadata("new.jpg")
	print("%s\t:\t%s"%(key,md[key]))
	
	# weite Tags zum testen
	print("## noch ein paar Tests:")
	et.execute(b"-XPKeywords=XPKeyword", b"-m", b"-overwrite_original", b"./new.jpg")
	et.execute(b"-XPKeywords<$XPKeywords, Test", b"-m", b"-overwrite_original", b"./new.jpg")
	key="EXIF:XPKeywords" #Gruppe:TAG
	md = et.get_metadata("new.jpg")
	print("%s\t:\t%s"%(key,md[key]))
	
	exit()
	for key, value in md.items():	
		print("%s\t:\t%s"%(key,value))
	
