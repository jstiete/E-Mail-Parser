#!/usr/bin/env python3
# Name:       readTagsFromFile.py
# Kommentar:  Metadaten von einem Bild ädern
# Autor:      Jan Stietenroth, Nov, 2017
# Version:    0.1

import exiftool
import os
with exiftool.ExifTool() as et:
	zebra_file=os.path.abspath("../InputData/zebra.jpg")
	#Tag von einem Bild auslesen:
	tag = et.get_tag("CreateDate", zebra_file)
	print("CreateDate:", tag)
	
	print("###### zwei Tags auslesen ######")
	tag = et.get_tags(["CreateDate", "DateTimeOriginal"], zebra_file)
	print(tag)

	tag = et.get_tag("SubSecTimeOriginal", zebra_file)
	print("SubSecTimeOriginal:", tag)





