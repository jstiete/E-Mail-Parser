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
# Name:       mail_functions.py
# Comment:    Functions for e-mail processing
# Author:     Jan Stietenroth, Nov, 2017
# Version:    0.3
#---------------------------------------------------------------------


# Compare foldernames in cache directory with mail subject.
# If a 'UID'+foldername matches mail subject return true.
def check_if_mail_is_reply(msgSubject, cachePath):
	import logging
	import os
	tempDirs = os.listdir(cachePath)
	for UIDdir in tempDirs:
		if("UID "+UIDdir in msgSubject):
			logging.info("There is an e-mail in the cache directory: %s" %(UIDdir))
			return UIDdir
	return None



# log the message main parameters (date, sender, etc.) and parse it's the text contents for keywords
# return the keywords as a dic object
def read_message(msg, keyWordsMail, config, mailUID):
	import logging
	logging.info("############## processing new e-mail ##############")
	if(msg["FROM"]==None or msg["DATE"]==None or msg["MIME-Version"]==None):
		from helpers import save_mail_to_cache
		logging.error("Cannot read msg[FROM], msg[DATE], msg[MIME-Version] from e-mail. Mail will be saved in cache.")
		cachePath = config.get("General", "cachePath")
		cachePath = cachePath+os.sep+mailUID
		save_mail_to_cache(msg, cachePath)
		return None
	logging.info("Parsing e-mail from %s; date: %s; subject:\'%s\' MIME-version: %s" %(msg["FROM"],msg["DATE"],msg["SUBJECT"],msg["MIME-Version"]))

	# Walk through e-Mail message parts and read the text contents
	# e.g. multipart/mixed
	#      +- multipart/related
	#      |   +- multipart/alternative
	#      |   |   +- text/plain
	#      |   |   +- text/html
	#      |   +- image/png
	#      +-- application/msexcel
	plainText=""
	htmlText=""
	for part in msg.walk():
		typ = part.get_content_type()
		logging.debug("Mail contains content type: "+typ)
		if(part.get("Content-Disposition") == None):
			if(typ == "text/plain"):
				plainText += "\n"+part.get_payload(decode=True).decode()
				logging.info("Part \'text/plain\' contains (%s): %s" %(part.get_content_charset(),repr(plainText)))
			if(typ == "text/html"):
				from helpers import myHtmlToText
				tempHtmlText = part.get_payload(decode=True).decode()
				logging.debug("Part \'text/html\' contains (%s): %s" %(part.get_content_charset(),repr(tempHtmlText)))
				htmlText += "\n"+myHtmlToText(tempHtmlText)
				logging.info("Parsed text/html: %s" %(repr(htmlText)))
	
	# parse text for keywords and related values
	# Prio_0 = default value (configuration); Prio_1 = html text; Prio_2 = plain text
	from helpers import parse_text_for_keywords
	keyWordsMail = parse_text_for_keywords(htmlText, keyWordsMail)
	keyWordsMail = parse_text_for_keywords(plainText, keyWordsMail)

	return keyWordsMail



# Iterate over all message attachments an check if an attachment is an known datatype.
# If it is, save it to the temp directory, read metadata and category information and write all informations
# required by it's data type (set in configuration).
# Return missing keyword names and the paths of parsed files.
def parse_message_attachments(message, dataTypes, fileExtensions, keyWordsMail, tempPath, config):
	import logging
	import copy
	import os
	missingKeys=[]
	parsedFiles=[]
	for part in message.walk():
		keyWordsPart = copy.deepcopy(keyWordsMail) #Restore values from e-mail

		#get the parts main information and check if it should be processed
		contentMaintype = part.get_content_maintype()
		contentSubtype = part.get_content_subtype()
		if(part.get("Content-Disposition") != None):	
			if(part.get("Content-Disposition").startswith("inline")): #skip inline Photos (most times Logos, Icons, etc)
				logging.info("Found inline image (%s). Skip this file. Check if it is a logos, etc. or not." %str(part.get_filename()))
				continue

			# parsing filename and fileextension from message-part object
			parsedFileData={}
			fileName = part.get_filename()
			logging.info("Parse filename for content-type %s/%s: Filename: \'%s\' split to in <Name>.<ext>" %(contentMaintype, contentSubtype, fileName))
			parsedFileData["orig_filename"] = fileName
			substr = fileName.rsplit(".",1)
			fileName = substr[0]
			fileExt = substr[1].lower()
			keyWordsPart["File_Name"] = {"value":fileName}
		
			# Parse or recognise datatype of attachment:
			# check if the data type was given as a keyword, otherwise use the objects file extension as data type
			if(keyWordsPart["DataType"]["value"] != None):
				dataType = keyWordsPart["DataType"]["value"]
			elif(fileExt in fileExtensions.keys()):
				dataType = fileExtensions[fileExt]
			else:
				dataType = fileExt
				logging.warn("Received mail from %s on %s: It contains a unknown datatype(.%s) which will be skiped!" %(message["FROM"],message["DATE"],fileExt))
				continue

			# save attachment for further processing on file level
			tempPath = os.path.abspath(tempPath)
			if not os.path.exists(tempPath):
				os.makedirs(tempPath, mode=0o777)
				logging.debug("Create directory: %s" %(repr(tempPath)))
			tempFilePath = tempPath+os.sep+fileName+"."+fileExt
			# add and increment a serial number if the file already exists
			if (os.path.isfile(tempFilePath)):
				serNo=1
				while (os.path.isfile(tempFilePath)):
					tempFilePath = tempPath+os.sep+fileName+"_("+str(serNo)+")."+fileExt
					serNo += 1
			try:
				fp=open(tempFilePath, "wb")
				fp.write(part.get_payload(decode=True))
				logging.debug("save %s" %(tempFilePath))
			except:
				logging.error("Writing temp-data %s was not sucessfull. See Traceback! Skip this file." %(tempFilePath), exc_info=True)
				continue
			else:
				parsedFileData["tempFilePath"] = tempFilePath
				fp.close()

			# read tags from metadata?
			from helpers import check_ReadMetadata
			if(check_ReadMetadata(dataType, dataTypes, keyWordsPart)):
				from helpers import read_metadata
				read_metadata(tempFilePath, dataType, dataTypes, keyWordsPart, config)
			#Parse Category-keyword if existing
			if(dataTypes[dataType]["category"] != None):
				from helpers import get_category_path
				category = dataTypes[dataType]["category"]
				retval, keyWordsPart = get_category_path(keyWordsPart, category)
				if(retval != []):
					missingKeys += retval
					logging.warn("Can't read category. Category value: \'%s\' was not found in category tree." %keyWordsPart[category]["value"])

			# write tags to metadata?
			from helpers import check_WriteMetadata
			if(check_WriteMetadata(dataType, dataTypes, keyWordsPart)):
				from helpers import write_metadata
				missingKeys += write_metadata(tempFilePath, dataType, dataTypes, keyWordsPart, config)
			
			# parse output directory and output filename
			from helpers import replace_variable_by_value
			from helpers import init_setSerialNo
			from helpers import filePath_setSerialNo
			from helpers import fileName_setSerialNo
			outputdir = dataTypes[dataType]["directory"]
			outputdir = os.path.abspath(outputdir)
			retval, outputdir = replace_variable_by_value(outputdir, keyWordsPart)
			if(retval != []):
				logging.warn("Error while parsing output directory. Missing Key: %s" %str(retval))
				missingKeys += retval
			var, strFormatter = init_setSerialNo(outputdir)
			if(var):
				outputdir = filePath_setSerialNo(outputdir, var, strFormatter)
			
			if(dataTypes[dataType]["filename"]):
				outputfile = dataTypes[dataType]["filename"]
				retval, outputfile = replace_variable_by_value(outputfile, keyWordsPart)
				if(retval != []):
					logging.error("Error while parsing output filename. Missing Key: %s" %str(retval))
					missingKeys += retval
				outputfile = outputdir+os.sep+outputfile+"."+fileExt
				var, strFormatter = init_setSerialNo(outputfile)
				if(var):
					outputfile = fileName_setSerialNo(outputfile, var, strFormatter)
			else:
				outputfile=outputdir+os.sep+fileName+"."+fileExt

			parsedFileData["outputdir"] = outputdir
			parsedFileData["outputfile"] = outputfile
			parsedFiles.append(parsedFileData)
	return missingKeys, parsedFiles


# generate an e-mail text which applies for the missing values
def generate_request_mail(missingKeys, keyWords):
	# You may write down your own message:
	text = ("Hello, \n"
		"please add the following informations to your last mail. "
		"I need more information to save your data correctly.\n")
	# get missing key names
	for key in missingKeys:
		text += keyWords[key]["name"]+":"+"\n"
	# if missing key is a category-key, list all possible categroies
	for key in missingKeys:	
		if "categoryRoot" in keyWords[key]:
			import os
			text += "\n Possible values for %s are:\n" %keyWords[key]["name"]
			# parse the category tree
			categoryRoot = keyWords[key]["categoryRoot"]
			categoryRoot = os.path.abspath(categoryRoot)
			dirList=[]
			if keyWords[key]["allowSupercategory"]:
				for root, dirs, files in os.walk(categoryRoot):
					relPath=root.replace(categoryRoot,"")
					dirList.append(relPath)
				del dirList[0]
			else:
				for root, dirs, files in os.walk(categoryRoot):
					if(dirs == []):
						relPath=root.replace(categoryRoot,"")
						dirList.append(relPath)
			for directory in dirList:
				text += " - "+os.path.basename(directory)+"\n"
	# some more text
	text = text+("\n"
		 "Just click on 'reply' and don't change the subject.\n"
	         "Thanks in advance!\n")
	return text
	

#get all saved mails in descending order (newest first)	
def parse_all_reply_mails(msg, directory, keyWordsMail, config, mailUID):
	import logging
	import os
	filenamelist = []
	for root, dirs, files in os.walk(directory):
		for name in files:
			if name.endswith(".msg"):
				fullname = os.path.join(root, name)
				filenamelist.append(fullname)
	filenamelist.sort(reverse=True)

	keyWordsMail = read_message(msg, keyWordsMail, config, mailUID)
	import email
	for filename in filenamelist:
		try:
			fp=open(filename,"rb")
			msg= email.message_from_binary_file(fp)
			logging.info("Parse saved e-mail %s" %filename)
		except:
			logging.error("Can not open %s. See Traceback" %filename, exc_info=True)
		else:
			fp.close()
			keyWordsMail = read_message(msg, keyWordsMail, config, mailUID)
	return msg


def send_request_mail(oldMessage, replyText, mailUID, config):
	import logging
	import email
	from email.mime.multipart import MIMEMultipart
	from email.mime.text import MIMEText
	from email.mime.message import MIMEMessage

	####### remove attachments from original #########
	for part in oldMessage.walk():
	    if (part.get('Content-Disposition')
	        and part.get('Content-Disposition').startswith("attachment")):

	        part.set_type("text/plain")
	        part.set_payload("Attachment removed: %s (%s, %d bytes)"
	                         %(part.get_filename(), 
	                           part.get_content_type(), 
	                           len(part.get_payload(decode=True))))
	        del part["Content-Disposition"]
	        del part["Content-Transfer-Encoding"]
	
	####### Create reply mail #######
	new = MIMEMultipart("mixed")
	body = MIMEMultipart("alternative")
	body.attach( MIMEText(replyText, "plain") )
	#body.attach( MIMEText("<html>reply body text</html>", "html") )
	new.attach(body)

	new["Message-ID"] = email.utils.make_msgid()
	new["In-Reply-To"] = oldMessage["Message-ID"]
	new["References"] = oldMessage["Message-ID"]
	new["Subject"] = "Re: "+"UID "+mailUID+": "+oldMessage["Subject"]
	new["To"] = oldMessage["Reply-To"] or oldMessage["From"]
	new["From"] = email.utils.parseaddr(oldMessage["To"])[1]
	#new["Bcc"] = admin@test.de

	####### attach the original message and send it #######
	new.attach( MIMEMessage(oldMessage) )
	
	####### send mail via smtp #######
	import smtplib
	server = config.get("General", "smtpserver")
	userName = config.get("General", "username")
	password = config.get("General", "password")
	serverList = server.split(":")
	try:
		if(len(serverList)==1):
			server=serverList[0]
			port="587"
		else:
			port=serverList[1]
			server=serverList[0]
		smtpObj = smtplib.SMTP(server, int(port))
	except smtplib.SMTPConnectError:
		if(len(serverList)==1):
			port="465"
		logging.warn("Connection refused! Try to connect via SSL to %s:%s"%(server, port))
		smtpObj = smtplib.SMTP_SSl(server, int(port))
	except:
		logging.error("Can not connect to %s. See Traceback" %server, 
		              exc_info=True)

	try:
		smtpObj.ehlo_or_helo_if_needed()
		smtpObj.starttls()
		smtpObj.login(userName, password)
	except smtplib.SMTPAuthenticationError:
		logging.error("Login on %s was not sucessful. See Traceback" %server, 
		              exc_info=True)
	except:
		logging.error("Can not connect to %s. See Traceback" %server, 
		              exc_info=True)
	else:
		logging.debug("Connected to %s as %s." %(server, userName))
		logging.info("Send e-mail from %s to %s: %s" %(new["FROM"], ", ".join(new["To"]), replyText))
		smtpObj.sendmail(new["FROM"], [new["To"]], new.as_string())
		smtpObj.quit()

# generate an e-mail text which informs about parsed files
def generate_info_mail(parsedFiles):
	# You may write down your own message:
	import os
	text = ("Hello, \n"
		"from your e-mail below %d files were recognized and saved.\n"
		"Thanks for your mail\n") %len(parsedFiles)
	for parsedFileData in parsedFiles:
			outputfile = parsedFileData["outputfile"]
			path, filename = os.path.split(outputfile)
			orig_filename = parsedFileData["orig_filename"]
			text = text + orig_filename + " --> " + filename + "\n"
	return text

