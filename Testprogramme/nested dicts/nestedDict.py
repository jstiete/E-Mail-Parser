#!/usr/bin/env python3
# Name:       nestedDict.py
# Kommentar:  Tests mit verschachtelten dicts
# Autor:      Jan Stietenroth, Nov, 2017
# Version:    0.1

mydict={}

mysubdict_1={}
mysubdict_1[1]="eins"
mysubdict_1[2]="zwei"

mysubdict_2={}
mysubdict_2[1]="one"
mysubdict_2[2]="two"

mydict["a"]=mysubdict_1
mydict["b"]=mysubdict_2

print(mydict)

print("hier sollte eins stehen: ", mydict["a"][1])
