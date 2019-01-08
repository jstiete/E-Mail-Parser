#!/usr/bin/env python3
# This Python file uses the following encoding: utf-8
#---------------------------------------------------------------------
# This file is part of MailParser
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
# Name:       helpers.py
# Comment:    Additional functions for e-mail parser
# Author:     Jan Stietenroth, Oct, 2017
# Version:    0.3
#---------------------------------------------------------------------


#initialize logger for terminal and file-output
def init_logger(logFile):
	import logging
	from logging.handlers import RotatingFileHandler
	logger = logging.getLogger()
	logger.setLevel(logging.DEBUG)
	# create console handler which logs even debug messages
	logFormatter = logging.Formatter('%(asctime)s\t- %(levelname)s\t- %(filename)s:(%(lineno)d) - %(message)s')
	ch = logging.StreamHandler()
	ch.setFormatter(logFormatter)
	ch.setLevel(logging.DEBUG)
	# create file handler with a higher log level and a rotating file (max. size)
	logfileFormatter = logging.Formatter('%(asctime)s\t%(levelname)s\t%(filename)s:(%(lineno)d) %(funcName)s: %(message)s')
	fh = RotatingFileHandler(logFile, mode='a', maxBytes=1*1024*1024, backupCount=1, encoding=None, delay=0)
	fh.setFormatter(logfileFormatter)                 ##=1MB
	fh.setLevel(logging.INFO)
	# add the handlers to logger
	logger.addHandler(ch)
	logger.addHandler(fh)
	return logger


# Convert HTML-Text  to plain-text 
# (replace newline tags by '\n' and remove other tags)
def myHtmlToText(message):
	import re
	newLine="(<br>)|(</p>)"
	expr="<[^>]*>"
	message = re.sub(newLine, "\n", message)
	message = re.sub(expr, "", message)
	return message

# Analyse the message text and extract the values of given keywords.
# Divide the text into different tokens and look for <ID> <ASSIGN> <ID>
def parse_text_for_keywords(message, keyDict):
	import re
	import logging
	keyDictNames = [subdict["name"] for subdict in keyDict.values()]
	keyDictKeys  = list(keyDict.keys())
	aktKeys=[]
	lastKind=""
	token_specification = [
	  ('ASSIGN',  r'[:=]'),                   # Assignment operator ':' or '='
	  ('END',     r'[;\n]'),                  # Statement terminator
	  ('ID',      r'(([\w-]+(,? ?))+[\w-])'), # Identifiers (one or more words seperated by comma or space)
	  ('SKIP',    r'[ \t]+'),                 # Skip over spaces and tabs
	  ('MISMATCH',r'.'),                      # Any other character
	]
	tok_regex = '|'.join('(?P<%s>%s)' % pair for pair in token_specification)
	for matchObj in re.finditer(tok_regex, message):
		kind = matchObj.lastgroup
		value = matchObj.group(kind)
		logging.debug("Text Parser found:\tKind: %s;\tValue: %s" %(kind, repr(value)))
		if kind == 'ID':
			if value in keyDictNames:
				indices = [i for i,key in enumerate(keyDictNames) if key==value]
				for i in indices:
					aktKeys.append(keyDictKeys[i])
			elif lastKind == "ASSIGN" and aktKeys!=[]:
				logging.info("Text Parser found: %s=%s" %(str(aktKeys), value))
				#value = remove_forbidden_characters(value) #not nessesary because of ID-regex
				for key in aktKeys:
					keyDict[key]["value"]=value
				aktKeys = []
		elif kind == 'SKIP':              #Don't remember this State!
			continue
		elif kind == 'END':
			aktKeys=[]
		elif kind == 'MISMATCH':          #Found something wrong
			aktKeys=[]
			logging.warn("Text Parser found unknown token: %s" %(value))
		lastKind=kind
	return keyDict

# Get all datatypes from config file and write them into a dict:
# dataTypes={key0:{name:Name, value:(default)-value, optional:Wert, appendMetadata:[List], writeMetadata:[List]},
#            key1:{name:Name, value:(default)-value, optional:Wert, appendMetadata:[List], writeMetadata[List]},
#            ...}
# i.e.:  dataTypes={Photo:{fileformats:[List], keys:[List], directory:String, filename:String},  
#                   PDF:{fileformats:[List], keys:[List], directory:String, filename:String},
#                   ...}
def get_datatypes_from_config(configFile):
	import configparser
	import re
	import sys
	import logging
	dataTypes={}
	types=configFile.get("General","dataTypes")
	types=re.split(",\s*", types) #comma with zero or more spaces
	logging.info("Parsing data types from configuration:")
	logging.debug("Found following data types in configuration: %s" %(", ".join(types)))
	for datatype in types:
		try:
			if(not configFile.has_section(datatype)):
				raise Exception("Section %s not found in configuration" %datatype)
			subdict={}
			if(configFile.has_option(datatype,"fileFormats")):
				tempValue = configFile.get(datatype, "fileFormats")
				tempValue = re.split(",\s*", tempValue)
				subdict["fileFormats"]=tempValue
				logging.debug("Datatype %s;\tOption %s=%s"%(datatype,"fileFormats",str(tempValue)))
			else:
				raise Exception("Option \'fileFormats\' not found in Section %s" %datatype)
			if(configFile.has_option(datatype,"keys")):
				tempValue = configFile.get(datatype, "keys")
				tempValue = re.split(",\s*", tempValue)
				subdict["keys"]=tempValue
				logging.debug("Datatype %s;\tOption %s=%s"%(datatype,"keys",str(tempValue)))
			else:
				raise Exception("Option \'keys\' not found in Section %s" %datatyp)
			if(configFile.has_option(datatype,"directory")):
				tempValue = configFile.get(datatype, "directory")
				subdict["directory"]=tempValue
				logging.debug("Datatype %s;\tOption %s=%s"%(datatype,"directory",tempValue))
			else:
				raise Exception("Option \'directory\' not found in Section %s" %datatyp)
			if(configFile.has_option(datatype,"filename")):
				tempValue = configFile.get(datatype, "filename")
				logging.debug("Datatype %s;\tOption %s=%s"%(datatype,"filename",tempValue))
			else:
				tempValue=None
			subdict["filename"]=tempValue
#			if(configFile.has_option(datatype,"name")):
#				tempValue = configFile.get(datatype, "name")
#				logging.debug("Datatype %s;\tOption %s=%s"%(datatype,"name",tempValue))
#			else:
#				tempValue=None
#			subdict["name"]=tempValue
			if(configFile.has_option(datatype,"category")):
				tempValue = configFile.get(datatype, "category")
				logging.debug("Datatype %s;\tOption %s=%s"%(datatype,"category",tempValue))
			else:
				tempValue=None
			subdict["category"]=tempValue
		except:
			logging.error("Error while reading datatype %s. See Traceback" %datatype, exc_info=True)
			exit()
		dataTypes[datatype]=subdict
	return dataTypes

# Read the fileFormats option from the datatype sections
# fileExtensions={jpg:Photo, png:Photo, pdf:PDF} (.extension : dataType)
def get_file_extensions_from_config(dataTypes):
	import logging
	fileExtensions={}
	for key, value in dataTypes.items():
		extensionlist = value["fileFormats"]
		for extension in extensionlist:
			if extension in fileExtensions:
				logging.warn("Multiple entry for %s-extension. it now belongs to %s." %(extension, key))
			fileExtensions[extension]=key
	return fileExtensions

# Read all keywords from configuration file and write them into a dict:
# keyDict={key0:{name:Name, value:(default)-value, optional:boolean, appendMetadata:[List], writeMetadata:[List], ...}, 
#          key1:{name:Name, value:(default)-value, optional:boolean, appendMetadata:[List], writeMetadata[List], ...},
#          ...}
def get_keywords_from_config(dataTypes, configFile):
	import configparser
	import re
	import sys
	import logging

	keyDict = {}
	categories=[]
	for dataType in dataTypes.values():
		for key in dataType["keys"]:
			if key not in keyDict:
				keyDict[key]=None
		if (dataType["category"] != None and
		    dataType["category"] not in keyDict):
			keyDict[dataType["category"]]=None
			categories.append(dataType["category"])
		
	if configFile.has_section("DataType"):
		keyDict["DataType"]=None
	else:
		logging.warn("The Section \'DataType\' (Global-Key) does not exist.")
	logging.info("Parsing the follwowing keywords: %s" %list(keyDict.keys()))
	for key in keyDict.keys():
		subDict={}
		try:
			subDict["name"] = configFile.get(key, "name")
			logging.debug("Keyword %s;\tOption %s=%s"%(key,"name",subDict["name"]))
			if(configFile.has_option(key,"default")):
				tempValue = configFile.get(key, "default")
				logging.debug("Keyword %s;\tOption %s=%s"%(key,"default",tempValue))
			else:
				tempValue=None
			subDict["value"]=tempValue
			if(configFile.has_option(key,"appendMetadata")):
				tempValue = configFile.get(key, "appendMetadata")
				tempValue = re.split(",\s*", tempValue)
				logging.debug("Keyword %s;\tOption %s=%s"%(key,"appendMetadata",str(tempValue)))
			else:
				tempValue=[]
			subDict["appendMetadata"]=tempValue
			if(configFile.has_option(key,"writeMetadata")):
				tempValue = configFile.get(key, "writeMetadata")
				tempValue = re.split(",\s*", tempValue)
				logging.debug("Keyword %s;\tOption %s=%s"%(key,"writeMetadata",str(tempValue)))
			else:
				tempValue=[]
			subDict["writeMetadata"]=tempValue
			if(configFile.has_option(key,"readMetadata")):
				tempValue = configFile.get(key, "readMetadata")
				tempValue = re.split(",\s*", tempValue)
				logging.debug("Keyword %s;\tOption %s=%s"%(key,"readMetadata",str(tempValue)))
			else:
				tempValue=[]
			subDict["readMetadata"]=tempValue
			if(configFile.has_option(key,"RegExprPattern")):
				tempValue = configFile.get(key, "RegExprPattern")
				logging.debug("Keyword %s;\tOption %s=%s"%(key,"RegExprPattern",str(tempValue)))
			else:
				tempValue=None
			subDict["RegExprPattern"]=tempValue
			if(key in categories):
				if(configFile.has_option(key,"categoryRoot")):
					tempValue = configFile.get(key, "categoryRoot")
					logging.debug("Keyword %s;\tOption %s=%r"%(key,"categoryRoot",tempValue))
					subDict["categoryRoot"]=tempValue
				else:
					raise Exception("Option \'categoryRoot\' not found in Section %s" %key)
				if(configFile.has_option(key,"allowSupercategory")):
					tempValue = configFile.getboolean(key, "allowSupercategory")
					logging.debug("Keyword %s;\tOption %s=%r"%(key,"allowSupercategory",tempValue))
				else:
					logging.warn("allowSupercategory not found in section %s. Set to False" %key)
					tempValue=False
				subDict["allowSupercategory"]=tempValue
		except:
			logging.error("Error while reading key-Section: %s" %key, exc_info=True)
			exit()
		keyDict[key]=subDict
	return keyDict


#Parse variables from e-mail:
def get_var_from_mail(message):
	import logging
	import email.utils
	mailVariables={}
	date = email.utils.parsedate(message["Date"])
	if(date == None):
		logging.error("Parsing E-Mail Date returns: None. -> Set date to Systemtime.")
		import datetime
		date = datetime.datetime.now()
		date = datetime.date.timetuple(date)
	mailVariables["Mail_Year"] = {"value": str(date[0])}
	mailVariables["Mail_Month"] = {"value": str(date[1])}
	mailVariables["Mail_Day"] = {"value": str(date[2])}
	return mailVariables


# substitute variables by it's values and return missingVariables
def replace_variable_by_value(variableString, keyWords):
	import logging
	import re
	missingKeys=[]
	for var in re.findall("\$\(\w+\)",variableString):
		var_slice = var[2:-1] # slicing returns the letters 2...end-1.
		temp = keyWords[var_slice]["value"]
		if(temp != None):
			if(re.search("\$\(\w+\)", temp) != None):
				retval, temp = replace_variable_by_value(temp, keyWords)
				missingKeys += retval
			logging.info("Replaced \'%s\' by \'%s\' in %s" %(var, temp, variableString))
			variableString = variableString.replace(var, temp, 1)
		else:
			logging.error("Can't replace \'%s\' in %s. Value is empty" %(var, variableString))
			missingKeys.append(var_slice)
	return missingKeys, variableString


# check if there are keys for writing metadata
def check_WriteMetadata(dataType, dataTypes, keyWords):
	for key in dataTypes[dataType]["keys"]:
		if(keyWords[key]["writeMetadata"] != [] or keyWords[key]["appendMetadata"] != []):
			return True
	return False
# check if there are keys for reading metadata
def check_ReadMetadata(dataType, dataTypes, keyWords):
	for key in dataTypes[dataType]["keys"]:
		if(keyWords[key]["readMetadata"] != []):
			return True
	return False


# read metadata from given file (filename). The metadata is defined by the keywords for the datatype
def read_metadata(filename, dataType, dataTypes, keyWords, config):
	import logging
	import re
	try:
		import exiftool
		exiftoolPath = None
		if(config.has_option("General", "exiftoolPath") and (config.get("General", "exiftoolPath") != "")):
			exiftoolPath = config.get("General", "exiftoolPath")
		with exiftool.ExifTool(exiftoolPath) as et:
			for key in dataTypes[dataType]["keys"]:
				if(keyWords[key]["readMetadata"] == []):
					continue
				regExpr=keyWords[key]["RegExprPattern"]
				tags=keyWords[key]["readMetadata"]
				for tag in tags:
					logging.debug("Read Tag %s: execute: et.get_tag(\'-%s\', \'%s\')" %(tag, tag, filename))
					value=et.get_tag(tag, filename)
					if(value == None):
						logging.debug("Tag was empty")
						continue
					logging.info("Tag value is: %s" %value)
					if(regExpr != None):
						value = re.search(regExpr, value)
						value = value.group(0)
						logging.debug("Executing regular expression \'%s\' results: %s" %(regExpr, value))
					if(value != None):
						value = remove_forbidden_characters(value)
						keyWords[key]["value"]=value
						logging.info("Reading metadata \'%s\' = %s" %(keyWords[key]["name"], value))
						break
	except:
		logging.error("Error while reading metadata with exiftool", exc_info=True)


# write keyword values to metadata of file "filename"
def write_metadata(filename, datatype, dataTypes, keyWords, config):
	import logging
	import re
	missingKeys=[]
	try:
		import exiftool
		exiftoolPath = None
		if(config.has_option("General", "exiftoolPath") and (config.get("General", "exiftoolPath") != "")):
			exiftoolPath = config.get("General", "exiftoolPath")
		with exiftool.ExifTool(exiftoolPath) as et:
			for key in dataTypes[datatype]["keys"]:
				value = keyWords[key]["value"]
				if(keyWords[key]["writeMetadata"] == [] and keyWords[key]["appendMetadata"] == []):
					continue
				logging.info("Processing Key: %s: AppendMetadata: %s; WriteMetadata: %s, Value: %s" %(key, keyWords[key]["appendMetadata"], str(keyWords[key]["writeMetadata"]), str(value)))		
				if (value == None):
					missingKeys.append(key)
					logging.info("Can't write/append metadata for key %s (name=%s). Missing value(s)" %(key, keyWords[key]["name"]))
					continue
				elif(re.search("\$\(\w+\)", value) != None):
					retval, value = replace_variable_by_value(value, keyWords)
					if(retval != []):
						missingKeys += retval
						logging.info("Can't substitute variable to write/append metadata for key %s. Missing value(s): %s" %(key, retval))
						continue
				for meta in keyWords[key]["writeMetadata"]:
					command=("-"+meta+"="+value).encode()
					logging.info("Write metadata. Execute et.execute(\'%s\', b\'-m\', b\'-overwrite_original\', \'%s\')" %(command, filename))
					et.execute(command, b"-m", b"-overwrite_original", filename.encode())
				for meta in keyWords[key]["appendMetadata"]:
					command=("-"+meta+"<$"+meta+" "+value).encode()
					logging.info("Append metadata. Execute et.execute(\'%s\', b\'-m\', b\'-overwrite_original\', \'%s\')" %(command, filename))
					et.execute(command, b"-m", b"-overwrite_original", filename.encode())
	except:
		logging.error("Error while writing metadata with exiftool", exc_info=True)
	return missingKeys


#Parse category keyword and return the related path
def get_category_path(keyWords, category):
	import logging
	import os
	import re

	# parse the category tree
	categoryRoot = keyWords[category]["categoryRoot"]
	categoryRoot = os.path.abspath(categoryRoot)
	dirList=[]
	if keyWords[category]["allowSupercategory"]:
		for root, dirs, files in os.walk(categoryRoot):
			relPath=root.replace(categoryRoot,"")
			dirList.append(relPath)
			logging.debug("Found Category: %s" %relPath)
		del dirList[0]
	else:
		for root, dirs, files in os.walk(categoryRoot):
			if(dirs == []):
				relPath=root.replace(categoryRoot,"")
				dirList.append(relPath)
				logging.debug("Found Category: %s" %relPath)
	#replace variables
	error=False
	missingKeys=[]
	value=keyWords[category]["value"]
	if(re.search("\$\(\w+\)", value) != None):
		retval, value = replaceVariableByValue(value, keyWords)
		if(retval != []):
			missingKeys += retval
			logging.warn("Can't substitute Variable to get category. Missing value(s): %s" %retval)
			error=True
	# search for matching category in the tree
	if not error:
		error=True
		value=re.escape(value)
		sep=re.escape(os.sep)
		regex=".*"+sep+value+"$"
		missingKeys=category
		for directory in dirList:
			mo=re.search(regex, directory, re.IGNORECASE)
			if mo:
				logging.info("Categorie \'%s\' belongs to path \'%s\'" %(value, directory))
				keyWords[category]["value"]=directory
				missingKeys=[]
				error=False
				break
	return missingKeys, keyWords


# init the replacement of serial numbers
def init_setSerialNo(variableString):
	import re
	mo = re.search("\$\(\*+\)",variableString)
	if mo:
		var=mo.group()
		d=len(var[2:-1])
		strFormatter = "%0"+str(d)+"d"
		return var, strFormatter
	else:
		return None, None


# Replace the SerialNo-Variable in a directory path or in an filename.
# Remember that only one SerialNo is supported. So, check directory path first!
# The two functions only differ in the break-condition (path.exists() vs. path.isfile())
def filePath_setSerialNo(filePath, var, strFormatter):
	import logging
	import os
	serialNo=0
	while True:
		number=strFormatter %serialNo
		outputString = filePath.replace(var, number, 1)
		serialNo += 1
		if(not os.path.exists(filePath)):
			logging.debug("Replaced serial numbers: \'%s\' to \'%s\'" %(filePath, outputString))
			break
	return outputString
def fileName_setSerialNo(fileName, var, strFormatter):
	import logging
	import os
	serialNo=0
	while True:
		number=strFormatter %serialNo
		outputString = fileName.replace(var, number, 1)
		serialNo += 1
		if(not os.path.isfile(outputString)):
			logging.debug("Replaced serial numbers: \'%s\' to \'%s\'" %(fileName, outputString))
			break
	return outputString


# recieves a list of parsedFileData-dicts (see: mail_functions.py: parse_message_attachments())
# and move the files to the output directory
def move_files_to_output(parsedFiles):
	import logging
	import shutil
	import os
	sucess = True
	for parsedFileData in parsedFiles:
		src = parsedFileData["tempFilePath"]
		destDir = parsedFileData["outputdir"]
		dest = parsedFileData["outputfile"]
		try:
			if not os.path.exists(destDir):
				os.makedirs(destDir, mode=0o777)
				logging.debug("Create directory: %s" %(repr(destDir)))
			if not os.path.isfile(dest):
				shutil.move(src,dest)
				logging.info("Move \'%s\' to \'%s\'" %(src, dest))
			else: 
				raise Exception("File \'%s\' already exists. Skip this!" %dest)
		except:
			logging.error("%s was not moved to output directory. See Traceback" %src, exc_info=True)
			sucess = False
	return sucess


# move the files to cache directory
def move_files_to_cache(parsedFiles, cacheRootPath):
	import logging
	import shutil
	import os
	cachePath = os.path.abspath(cacheRootPath+os.sep+"saved_Data")
	try:
		if not os.path.exists(cachePath):
			os.makedirs(cachePath, mode=0o777)
			logging.debug("Create directory: %s" %(repr(cachePath)))
		for parsedFileData in parsedFiles:
			src = parsedFileData["tempFilePath"]
			outputfile = parsedFileData["outputfile"]
			path, filename = os.path.split(outputfile)
			dest = os.path.abspath(cachePath+os.sep+filename)
			shutil.move(src,dest)
			logging.info("saved file in cache: \'%s\'" %dest)
	except:
		logging.error("Error while copying files to cache directory . See traceback" %src, exc_info=True)


# delete parsed files from temp directory
def delete_parsedFiles(parsedFiles):
	import os
	for parsedFileData in parsedFiles:
		src = parsedFileData["tempFilePath"]
		os.remove(src)


#save mail in cache directory
def save_mail_to_cache(message, msgCache):
	import logging
	import email
	import os
	e_mailPath = msgCache + os.sep + "e_mail.msg"
	e_mailPath = os.path.abspath(e_mailPath)
	if not os.path.exists(msgCache):
		os.makedirs(msgCache, mode=0o777)
		logging.debug("Create directory: %s" %(repr(e_mailPath)))
	# add and increment a serial number if the file already exists
	if (os.path.isfile(e_mailPath)):
		serNo=1
		while (os.path.isfile(e_mailPath)):
			e_mailPath = msgCache+os.sep+"e_mail"+"_("+str(serNo)+").msg"
			e_mailPath = os.path.abspath(e_mailPath)
			serNo += 1
	try:
		f=open(e_mailPath, "wb")
		f.write(message.as_bytes())
	except:
		logging.error("Error! Incomplete Mail was not saved to temp directory. See traceback", exc_info=True)
		return False
	else:
		f.close()
		logging.info("Incomplete Mail was saved in: %s" %e_mailPath)
		return True


# remove special characters from input string to prevent Code-Injection, etc.
def remove_forbidden_characters(inputString):
	import re
	outputString, subs = re.subn(r'[/\\.]+', '', inputString)
	if subs>=1:
		import logging
		logging.warn("removed \'/\\.\'characters from variable: %s" %outputString)
	return outputString

