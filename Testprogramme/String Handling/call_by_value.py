#!/usr/bin/env python3
# This Python file uses the following encoding: utf-8
# Name:       call_by_value.py
# Kommentar:  call-by-value for Strings
# Autor:      Jan Stietenroth, Okt, 2017
# Version:    0.1


def hallo_welt(string):
	string = string+" Welt!"
	return string


######## Main Schleife ###########
if __name__ == '__main__':
	string  = "Hallo"
	string2 = hallo_welt(string)
	print("String: ", string)
	print("String2: ", string2)
