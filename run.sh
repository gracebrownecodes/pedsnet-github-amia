#!/bin/bash
/usr/bin/env pip install -r requirements.txt
/usr/bin/env python retrieve_data.py
/usr/bin/env Rscript analyze_data.R
