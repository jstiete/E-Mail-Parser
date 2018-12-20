#!/usr/bin/env python3
# This Python file uses the following encoding: utf-8
# Name:       ParseKeys.py
# Kommentar:  Liest eine Konfiguration und sucht die definierten Keys
# Autor:      Jan Stietenroth, Okt, 2017
# Version:    0.1


def myParseConfig():
	import configparser
	import re
	config = configparser.SafeConfigParser(allow_no_value=True) 
	fp = open("./Config.ini", "r")
	config.readfp(fp)
	fp.close()

	keys=config.get("Foto","keys")
	keys=re.split(",\s*", keys) #komma mit 0-unendlich vielen Leerzeichen
	#print(keys)

	mydict = {}
	for key in keys:
		name = config.get(key, "name")
		if(config.has_option(key,"optional")):
			opt  = config.getboolean(key, "optional")
		else:
			opt=False
		mydict[key] = [name, opt]
	return mydict


######## Main Schleife ###########
if __name__ == '__main__':
	mydict=myParseConfig()
	print("Eingelesene Konfiguration:\n", mydict, "\n")
	
	print("Key:\t\tName:\t\t\t\'optional\'-Key:")
	for key, value in mydict.items():
		if(value[1]==True):
			print(key+" \t("+value[0]+") \t"+"ist erforderlich.")
		elif(value[1]==False):
			print(key+" \t("+value[0]+") \t"+"ist NICHT erforderlich.")
