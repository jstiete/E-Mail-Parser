#!/usr/bin/env python3
# Name:       regularExpr.py
# Kommentar:  Tests für regular Expressions
# Autor:      Jan Stietenroth, Nov, 2017
# Version:    0.1

import re
msg="hallo $(File_Name) ende!"
x=re.search('\$\(\w+\)', msg)
print(x)
