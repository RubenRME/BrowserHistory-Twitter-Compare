#!/bin/sh
set +v
pip install -r req.txt
cd bin
clear
python main.py
sleep