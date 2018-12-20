#!/usr/bin/env python3
# Name:       writeConfig.py
# Kommentar:  Skript zum erzeugen einer INI-Datei mit verschiedenen Sectionen und Optionen
# Autor:      Jan Stietenroth, Okt, 2017
# Version:    0.1

import configparser

config = configparser.ConfigParser()

Section = "Test"
config.add_section(Section)
config.set(Section, "float", "1.0")
config.set(Section, "int", "10")
config.set(Section, "bool1", "Yes")
config.set(Section, "bool2", "false")

Section = "General"
config.add_section(Section)
config.set(Section, "imapServer", "imap.internet.de")
config.set(Section, "userName", "meineMailAdresse@internet.de")
config.set(Section, "password", "meinPasswort")

Section = "Key1"
config.add_section(Section)
config.set(Section, "name", "MeinKey1Name")
config.set(Section, "optional", "No")

f = open("testConfig.ini", "w")
config.write(f)
f.close()
