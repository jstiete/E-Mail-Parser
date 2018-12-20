#!/usr/bin/env python3
# This Python file uses the following encoding: utf-8
# Name:       PrintFolderTree.py
# Kommentar:  Script zum Anzeigen einer Ordnerstruktur ausgehend von "rootPath"
#             Es sollen alle Unterverzeichnisse aber keine Dateien angezeigt werden.
# Autor:      Jan Stietenroth, Okt, 2017
# Version:    0.1

import os

rootPath = "." #current directory
for root, dirs, files in os.walk(rootPath):
	level = root.replace(rootPath, '').count(os.sep)
	if(level == 0):
		indent=''
	else:
		#indent = ' ' * 2 * ()(level)
		indent = ' ' * (2 * (level-1))
		indent = indent + "+-"
	print(indent + os.path.basename(root) + "/")


print("########### Ordner und Unterordner ###################")
#rootPath = os.path.abspath(rootPath)
dirList=[]
for root, dirs, files in os.walk(rootPath):
	relPath=root.replace(rootPath,"")
	dirList.append(relPath)
del dirList[0]
for d in dirList:
	print(d)

print("########### nur Unterordner (die keinen Ordner mehr enthalten) ###############")
dirList=[]
for root, dirs, files in os.walk(rootPath):
	if(dirs == []):
		relPath=root.replace(rootPath,"")
		dirList.append(relPath)
for d in dirList:
	print(d)


#import re
#mylist = ["dog", "cat", "wildcat", "thundercat", "cow", "hooo"]
#r = re.compile(".*cat")
#newlist = filter(r.match, mylist)
#print str(newlist)




#import re
## Sample strings.
#list = ["dog dot", "do don't", "dumb-dumb", "no match"]
## Loop.
#for element in list:
#    # Match if two words starting with letter d.
#    m = re.match("(d\w+)\W(d\w+)", element)
#    # See if success.
#    if m:
#        print(m.groups())

