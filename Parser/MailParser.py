#!/usr/bin/env python3
# This Python file uses the following encoding: utf-8
#---------------------------------------------------------------------
# MailParser - A program to save e-mail attachments automatically
# Copyright (C) 2018  Jan Stietenroth
# <Link auf Github einfügen>
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
# Name:       MailParser.py
# Comment:    This Script reads e-mail messages from an IMAP server 
#             and stores attached data on the computer.
#             Individual variables for each datatype are parsed an applyed to the data.
#             It's also possible to read or modify the metadata of the attachment.
#             This feature requieres Phil Harvey's ExifTool and PyExifTool by Sven Marnach
#             The MIME extensions (plain/text, etc.) are documented on https://tools.ietf.org/html/rfc2046 .
#             requiered software for full usability:
#                       ExifTool (http://dev.perl.org/licenses/) https://www.sno.phy.queensu.ca/~phil/exiftool/
#                       PyExifTool (GNU GPL v3 or later) https://github.com/smarnach/pyexiftool
#             supported metadata tags are documented on https://sno.phy.queensu.ca/~phil/exiftool/TagNames/index.html 
#             To test the correct input of tag names/groups in your configuration
#             you can (should) use the pyExiftool testscripts (changeFileMetaData.py and readTagsFromFile.py).
#
#             version 0.1  Oct. 2017
#                 Initial version 
#             Version 0.2: Dec. 2017
#                 split the script into three files
#             Version 0.3: Jan. 2018
#                 Set category as a seperate datatype option.
#                 So, each datatype can use it's own category tree.
#
# Autor:      Jan Stietenroth, Dec, 2017
# Version:    0.3
#---------------------------------------------------------------------

import imaplib
import email
import sys
import copy
import os

########################### read Config: ###########################
import configparser
configPath = os.path.abspath("./MailConfig.ini")
config = configparser.SafeConfigParser(allow_no_value=True)
try:
	fp = open(configPath, "r")
	config.readfp(fp)
except:
	print("Can not read the configuration from %s:" %configPath,sys.exc_info()[0])
	exit("Error")

########################## initialise logger ##########################
from helpers import init_logger
if (config.has_option("General","logFile")):
	loggerPath = config.get("General","logfile")
	loggerPath = os.path.abspath(loggerPath)
	logger = init_logger(loggerPath)
else:
	loggerPath = os.path.abspath("./MailParser.log")
	logger = init_logger(loggerPath)
	logger.warn("No logfile path found in configuration. Created logfile on %s" %loggerPath)
logger.info("#################### MailParser.py started ####################")

####################### connect to imap server #######################
if(config.get("General", "protocol").lower() == "imap"):
	server = config.get("General", "imapserver")
	userName = config.get("General", "username")
	password = config.get("General", "password")
	server = server.split(":")
	try:
		if(len(server)==1):
			imapObj = imaplib.IMAP4_SSL(server)
		else:
			port=server[1]
			server=server[0]
			imapObj = imaplib.IMAP4_SSL(server, int(port))
		imapObj.login(userName, password)
	except imaplib.IMAP4.error:
		logger.error("Can not connect to %s. See Traceback", 
		              exc_info=True)
		exit("No connection to server")
	else:
		logger.info("Connection to %s established as %s." %(server, userName))
	try:
		mailboxFolder=config.get("General", "mailboxfolder")
		imapObj.select(mailboxFolder)
	except:
		logger.error("Can not open \'%s\'-Folder in Mailbox. See Traceback"%(mailboxFolder))
		logger.info("Available folders: %s" %(", ".join(imapObj.list())))
		logger.error(exc_info=True)

	imapQuery = config.get("General", "imapquery")
	result, uids = imapObj.uid('search', None, imapQuery)
	logger.info("Search Mails. Result=\'%s\' Query=%s" %(result, imapQuery))
	if result != "OK":
		logger.info("No unread messages found! Exit!")
		imapObj.logout()
		exit()

############## or declare the UIDs to read mails from file ################
elif(config.get("General", "protocol").lower() == "file"):
	uids=["complete", "incomplete_1", "mixed", "incomplete_2"]

########################## load configuration #############################
from helpers import get_keywords_from_config
from helpers import get_datatypes_from_config
from helpers import get_file_extensions_from_config
dataTypes = get_datatypes_from_config(config)
keyWordsConfig = get_keywords_from_config(dataTypes, config)
fileExtensions = get_file_extensions_from_config(dataTypes)

################### read path for cache and temp data #####################
tempPathExists = False
if(config.has_option("General", "tempPath") and 
  (config.get("General", "tempPath") != "")):
	tempPathExists = True
	tempPathConfig = config.get("General", "tempPath")
	cachePathConfig = config.get("General", "cachePath")
else:
	cachePathConfig = config.get("General", "cachePath")
	tempPathConfig = cachePathConfig

tempPathConfig = os.path.abspath(tempPathConfig)
cachePathConfig = os.path.abspath(cachePathConfig)


########################## processing E-Mails ##########################
for mailUID in uids:
	########################## fetch E-Mails ##########################
	if(config.get("General", "protocol").lower() == "imap"):
		result, email_data = imapObj.uid("fetch", mailUID,"(RFC822)")
		raw_email = email_data[0][1]
		msg = email.message_from_bytes(raw_email)
	
	elif(config.get("General", "protocol").lower() == "file"):
		#open e-mail
		fp=open("./InputData/"+mailUID+".msg","rb")
		msg= email.message_from_binary_file(fp)
		fp.close()

	########################## processing E-Mails ##########################
	# Mail handling:
	# check if mail is reply to older mail (variable request):
	#     yes:    load old mails
	#             read old texts / parse variables (newest first)
	#             replace actual mail by oldest mail (that one with attachment)
	# read text / parse variables    
	# handle attachments:
	#     read metadata
	#     get Category
	#     write metadata
	# all required variables OK?
	#       YES:    save files and exit
	#       NO:     save mail to temp
	#               generate mail (request missing variables)
	#
	from mail_functions import check_if_mail_is_reply
	from mail_functions import read_message
	from helpers import get_var_from_mail
	from mail_functions import parse_message_attachments

	keyWordsMail = copy.deepcopy(keyWordsConfig) #Restore initial values from Config
	tempPath = tempPathConfig+os.sep+mailUID
	cachePath = cachePathConfig+os.sep+mailUID

	######################## handle reply ########################
	message_reply = False
	origUID = check_if_mail_is_reply(msg["SUBJECT"], cachePathConfig)
	if(origUID != None):
		from mail_functions import parse_all_reply_mails
		message_reply = True
		replyUID=mailUID
		mailUID=origUID
		tempPath = tempPathConfig+os.sep+mailUID
		cachePath = cachePathConfig+os.sep+mailUID
		#directory = cachePathConfig + os.sep + mailUID
		msg = parse_all_reply_mails(msg, cachePath, keyWordsMail, config, mailUID)
		
	######################## parse received message ########################
	# Parse all keywords from Message	
	keyWordsMail = read_message(msg, keyWordsMail, config, mailUID)
	if(keyWordsMail == None):
		logger.error("Can not read e-mail data. processing aborted!")
		continue

	# Get Message Data ( $(Mail_Date), etc.)
	keyWordsMail.update(get_var_from_mail(msg))

	######################## parse attachments ########################
	missingKeys, parsedFiles = parse_message_attachments(msg, dataTypes, fileExtensions, 
	                               keyWordsMail, tempPath, config)
	# remove duplicates from list:
	missingKeys = list(set(missingKeys))

	############## save attachments if no keywords are missing ##############
	if(missingKeys == []):
		# Everything was fine, save data in output directory:
		# move files and delete temporary directories
		from helpers import move_files_to_output
		from mail_functions import generate_info_mail
		from mail_functions import send_request_mail
		if(move_files_to_output(parsedFiles)):
			import shutil
			if(os.path.exists(tempPath)):
				shutil.rmtree(tempPath)
			if(message_reply and tempPathExists and os.path.exists(cachePath)):
				shutil.rmtree(cachePath)
		# moving to output was not successful.
		elif(tempPathExists):
			from helpers import move_files_to_cache
			move_files_to_cache(parsedFiles, cachePath)
			try:
				os.rmdir(tempPath)
			except:
				logger.error("Can not delete %s. Siehe Traceback" %tempPath, 
				             exc_info=True)

		mailText = generate_info_mail(parsedFiles)
		print(mailText)
		#send_request_mail(msg, mailText, mailUID, config)
		deleteMailFromServer = True
	else:
		# Or: keys are missing, save data and generate request mail
		from mail_functions import generate_request_mail
		from helpers import delete_parsedFiles
		from helpers import save_mail_to_cache
		from mail_functions import send_request_mail
		deleteMailFromServer = save_mail_to_cache(msg, cachePath)
		replyText = generate_request_mail(missingKeys, keyWordsMail)
		print(replyText)
		#send_request_mail(msg, replyText, mailUID, config)
		delete_parsedFiles(parsedFiles)
		if(tempPathExists):
			os.rmdir(tempPath)
	
	######################## clean up ########################
	if (deleteMailFromServer and 
	   (config.get("General", "protocol").lower() == "imap")):
		logger.info("Delete processed e-mails from server.")
		if message_reply == False:
			imapObj.delete_messages(mailUID) #you may want to comment out that line
		else:
			imapObj.delete_messages(replyUID) #you may want to comment out that line
		imapObj.expunge()

######################## close imap connection ########################
if(config.get("General", "protocol").lower() == "imap"):
	imapObj.logout()


print("Program finished")
exit()

