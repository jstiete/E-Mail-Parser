#!/usr/bin/env python3
# Name:       readConfig.py
# Kommentar:  Skript zum lesen einer INI-Datei mit verschiedenen Sectionen und Optionen
# Autor:      Jan Stietenroth, Okt, 2017
# Version:    0.1

import configparser

path="./testConfig.ini"

config = configparser.SafeConfigParser(allow_no_value=True) 
fp = open(path, "r")
config.readfp(fp)
fp.close()

sections = config.sections() #Liste alle Sektionen
print(sections)

#Parse one Section:
if config.has_section("Test"):
	section_id=sections.index("Test")
	print("Index von \'Test\': ",section_id)

	for myOption in config.options("Test"):
		if(myOption == "float"):
			f=config.getfloat("Test", "float")
			print("Section \'%s\' \tOption \'%s\'=\t%f" %(sections[section_id], myOption, f))
		if(myOption == "int"):
			i=config.getint("Test", "int")
			print("Section \'%s\' \tOption \'%s\'=\t%d" %(sections[section_id], myOption, i))
		if(myOption == "bool1"):
			b=config.getboolean("Test", "bool1")
			print("Section \'%s\' \tOption \'%s\'=\t%s" %(sections[section_id], myOption, b))
		if(myOption == "bool2"):
			b=config.getboolean("Test", "bool2")
			print("Section \'%s\' \tOption \'%s\'=\t%s" %(sections[section_id], myOption, b))
	
	string_value = config.get("Test","float")
	print("Float_value als String",string_value)


#Parse Config as dict
print("Ausgabe als Dictionary (Key-Werte-Paar):")
mydict = {}
for section in config.sections():
    mydict[section] = {}
    for key, val in config.items(section):
        mydict[section][key] = val
print(mydict)

