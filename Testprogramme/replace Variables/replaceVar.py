#!/usr/bin/env python3
# This Python file uses the following encoding: utf-8
# Name:       replaceVar.py
# Kommentar:  Variablen in den Keys ersetzen
# Autor:      Jan Stietenroth, Nov, 2017
# Version:    0.1


def replaceVariableByValue(variableString, keyWords):
	import re
	missingKeys=[]
	for var in re.findall("\$\(\w+\)",variableString):
		var_slice = var[2:-1] # slicing returns the letters 2...end-1. should be the same as re.find("\w", var)
		temp = keyWords[var_slice]["value"]
		if(temp != None):		
			if(re.search("\$\(\w+\)", temp) != None):
				retval, temp = replaceVariableByValue(temp, keyWords)
				missingKeys += retval
			print("Replaced \'%s\' by \'%s\' in \'%s\'" %(var, temp, variableString))
			variableString = variableString.replace(var, temp, 1)
		else:
			print("Can't replace \'%s\' in \'%s\'. Value is empty" %(var, variableString))
			missingKeys.append(keyWords[var_slice]["name"])
	return missingKeys, variableString
		
	

######## Main Schleife ###########
if __name__ == '__main__':
	subkey1={"value":"ein Wert mit vielen variablen $(event)! Ist das ein Satz? $(satz)  -> den bestimmt nicht alle kennt $(pech)", "name":"test"}
	subkey2={"value":None, "name":"Event"}
	subkey3={"value":"$(tag) ist ein Satz", "name":"Satz"}
	subkey4={"value":"Das", "name":"Tag"}
	subkey5={"value":None, "name":"Pech"}

	keyWords={"test":subkey1, "event":subkey2, "satz":subkey3, "tag":subkey4, "pech":subkey5}
	retval, subkey1["value"] = replaceVariableByValue(subkey1["value"], keyWords)
	print("## Unbekannte Variablen: ",retval)
	print("Ergebnis: ",subkey1["value"])

	msg="Noch ein Test"
	print("\n")
	retval, msg1 = replaceVariableByValue(msg, keyWords)
	print("## Unbekannte Variablen: ",retval)
	print("Ergebnis: ",msg1)

	
