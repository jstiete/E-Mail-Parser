#!/usr/bin/env python3
# This Python file uses the following encoding: utf-8
#---------------------------------------------------------------------
# MailParser - A program to save e-mail attachments automatically
# <github>
# Copyright (C) 2018  Jan Stietenroth
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#---------------------------------------------------------------------
# Name:       Create_MailTo_Doc.py
# Comment:    This Script creates a html document with templates 
#             for various E-Mail bodies
#
#             version 0.1  Jun. 2018
#                 Initial version 
#
# Autor:      Jan Stietenroth, Jun, 2018
# Version:    0.1
#---------------------------------------------------------------------


import os

def get_Categories(config, category, keyWords):
	import logging
	import os

	# parse the category tree
	categoryRoot = keyWords[category]["categoryRoot"]
	categoryRoot = os.path.abspath(categoryRoot)
	dirDict={}
	if keyWords[category]["allowSupercategory"]:
		for root, dirs, files in os.walk(categoryRoot):
			relPath=root.replace(categoryRoot,"")
			dirDict[os.path.basename(root)]=relPath
			logging.debug("Found Category: %s" %relPath)
		del dirDict[os.path.basename(categoryRoot)]
		
	else:
		for root, dirs, files in os.walk(categoryRoot):
			if(dirs == []):
				relPath=root.replace(categoryRoot,"")
				dirDict[os.path.basename(root)] = relPath
				logging.debug("Found Category: %s" %relPath)
	return dirDict




######## Main Schleife ###########
if __name__ == '__main__':
	############## Read the Configuration of MailParser ##############
	import configparser
	configPath = os.path.abspath("./MailConfig.ini")
	config = configparser.SafeConfigParser(allow_no_value=True)
	try:
		fp = open(configPath, "r")
		config.readfp(fp)
	except:
		print("Can not read the configuration from %s:" %configPath,sys.exc_info()[0])
		exit("Error")
	
	from helpers import get_keywords_from_config
	from helpers import get_datatypes_from_config
	dataTypes = get_datatypes_from_config(config)
	keyWords = get_keywords_from_config(dataTypes, config)

	htmlContent=""	

	# get informations about each datatype
	for datatype,values in dataTypes.items():
		fileFormats = values["fileFormats"]
		keys=values["keys"]
		keyNames=[]
		mailto=[]
		for key in keys:
			keyNames.append(keyWords[key]["name"])

		# Built HTML Content (Datatype and file extensions)
		#htmlContent += "<h1><span style=\"font-family:Arial\">%s</span></h1>\n"%datatype
		htmlContent += "<h1 style=\"background-color:#CCCCCC;\">%s</h1>\n"%datatype			
		htmlContent += "<p>File extensions:  %s</p>\n"%(", ".join(fileFormats))
		htmlContent += "<p>Keywords: %s</p>\n"%("\n".join(keyNames))
		
		categoryDict={}
		if(values["category"] != None):
			categoryDict = get_Categories(config, values["category"], keyWords)
			# Add Categories to HMTL Content
			categoryName=values["category"]
			htmlContent += "<p>%s: %s</p>\n"%(str(keyWords[categoryName]["name"]),", ".join(categoryDict.keys()))
			
			# Add MailTo
			for category,path in categoryDict.items():
				htmlContent += "<h2>%s (%s) </h2>\n"%(category, path)
				htmlContent += "<p><A HREF=\"mailto:?subject=new %s &body=%%0D%%0A%s = %%0D%%0A%s = %s\">Send E-Mail</A></p>\n"%(datatype,"= %0D%0A".join(keyNames),str(keyWords[categoryName]["name"]),category)
		else:
			# Add MailTo
			htmlContent += "<p><A HREF=\"mailto:?subject=new %s &body=%%0D%%0A%s = \">Send E-Mail</A></p>"%(datatype,"= %0D%0A".join(keyNames))
	print(htmlContent)

	# Write HTML file
	with open("./InputData/MailTo-template.html", 'r') as fp:
    		html=fp.read()
	html_output = html%(htmlContent)
	with open("Output.html", "w") as text_file:
    		text_file.write(html_output)
		
			
		
