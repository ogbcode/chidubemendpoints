# -*- coding: utf-8 -*-
"""
Created on Fri Aug  5 11:17:29 2022

@author: chidubem ogbuefi
"""

from flask import Flask,jsonify,request

app = Flask(__name__)
app=Flask(__name__)
@app.route('/')
def helloworld():
    return{"message":"helloworld"}
if __name__ =="__main__":
    app.run(debug=True)