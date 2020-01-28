# -*- coding: utf-8 -*-
"""
Created on Sun Dec  8 13:57:27 2019

@author: sqr_p
"""

# import numpy as np
from collections import defaultdict as ddict

Values = ddict(float)

Values['old6'] = 1 + 15
Values['old5'] = 1 + 8
Values['new6'] = 180 - Values['old6']
Values['new5'] = 45 - Values['old5']
Values['get4'] = 1 + 30*Values['green']
Values['get3'] = 10 * Values['green']
