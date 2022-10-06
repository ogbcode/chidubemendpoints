# -*- coding: utf-8 -*-
"""
Created on Fri Aug  5 11:17:29 2022

@author: chidubem ogbuefi
"""
from datetime import datetime,timedelta
from urllib import request
from sqlalchemy import create_engine
import pyodbc
import pandas as pd
from flask import Flask,jsonify,request
from flask_restful import Api,Resource
from hashlib import sha256
import jwt
import os
from flask_cors import CORS
from dotenv import load_dotenv
load_dotenv()
email1="chidubemogbuefi@gmail.com"
password1="chidubem"
#function to hash password
def hash(data):
        hash_var=sha256((data).encode())
        finalhash=hash_var.hexdigest()
        return finalhash

server = 'wemotedb.database.windows.net,1433'
database = 'employeedb'
username = 'chidubem'
password = 'Ogbuefi@1'   
driver= 'ODBC Driver 18 for SQL Server'
connect=pyodbc.connect('DRIVER='+driver+';SERVER=tcp:'+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password+';Encrypt=yes'+';TrustServerCertificate=no'+';Connection Timeout=0') 
cursor = connect.cursor()
connection_string=f'mssql://{username}:{password}@{server}/{database}?driver={driver}'
# connection_string=f'mssql://{str(os.getenv("USERNAME"))}:{str(os.getenv("PASSWORD"))}@{str(os.getenv("SERVER"))}/{str(os.getenv("DATABASE"))}?driver={str(os.getenv("DRIVER"))}'
def emailauthent(email):
        engine = create_engine(connection_string)
        connection=engine.connect()
        sqltable=pd.read_sql_query(str(os.getenv("selectall")),connection)
        finaltable1=pd.DataFrame(sqltable)
        emailauthentication=(email in finaltable1['email'].unique())
        return emailauthentication

def tokenauthent(email,key):
        if 'tokenauth' in request.headers:
            email_exist=emailauthent(email)
            if (email_exist==True):
                token = request.headers['tokenauth']
                tokget=cursor.execute(os.getenv("tokenselect"),email)
                for ai in tokget:
                    pass
                if(bool(ai[0])==True):
                    try:
                        decodedtoken=jwt.decode(ai[0], key=key, algorithms=['HS256', ])
                        if(decodedtoken['expiration']<str(datetime.utcnow())):
                            return{"message":"token expired"}
                        else:
                            return {"token":ai[0],"message":"token is valid"}
                    except:
                        return{"message":"token verification failed"}
            else:
                return {"message":"email does not exist"}
        else:
            return{"message":"token not included"}
cursor = connect.cursor()


app = Flask(__name__)
CORS(app)
app=Flask(__name__)
api=Api(app)
@app.route('/')
def helloworld():
    return{"message":"Backend server is running"}
class login(Resource):
    def post(self):
        email_pass=request.get_json()
        cursor = connect.cursor()
        self.email=email_pass['email']
        password=hash(email_pass['Password'])
        self.connection_string=connection_string
        self.engine = create_engine(self.connection_string)
        self.connection=self.engine.connect()
        sqltable=pd.read_sql_query(str(os.getenv("selectall")),self.connection)
        finaltable1=pd.DataFrame(sqltable)
        emailauthentication=(self.email in finaltable1['email'].unique())
        if (emailauthentication==True):
            # passwordauthentication=(password in finaltable1['password'].unique())
            passwordauthentication=cursor.execute(os.getenv("accpassword"),self.email)
            for passw in passwordauthentication:
                pass
            pass_word=passw[0]

            if (pass_word==password):
                sqlroleid=cursor.execute(os.getenv("roleid"),self.email)
                for  d in sqlroleid:
                    pass
                roleid=d[0]
                sqlrole=cursor.execute(os.getenv("role"),roleid)
                for b in sqlrole:
                    pass
                role=b[0]
                sqlunitid=cursor.execute  (os.getenv("unitid"),self.email)
                for unid in sqlunitid:
                    pass
                unitid=unid[0]
                sqlunit=cursor.execute(str(os.getenv("unitname")),unitid)
                for unidd in sqlunit:
                    pass
                unit=unidd[0]
                key=str(os.getenv("key"))
                encodedtoken = jwt.encode({
                    'email': self.email,
                    "unit":unit,
                    "role":role,
                    "message":"you are connected",
                'expiration': str(datetime.utcnow() + timedelta(seconds=999))
                },key)
                cursor.execute(str(os.getenv("updatetoken")),str(encodedtoken),self.email)
                connect.commit()
            else:
                
                return {"message":"incorrect password"}
        else:
            
            return {"message":"user does not exist"}
        return  jwt.decode(encodedtoken, key=str(os.getenv("key")), algorithms=['HS256', ])
api.add_resource(login,'/login')
class demologin(Resource):
    def post(self):
        data=request.get_json()
        email=data['email']
        password=data['password']
        if (email==email1 and password==password1):
            return{"message":"login approved"}
        else:
            return{"message":"login denied"}
api.add_resource(demologin,"/demologin")
class scheduledays(Resource):
    def post(self):
        data=request.get_json()
        self.email=data['email']
        tokenfunc=tokenauthent(self.email,str(os.getenv("key")))
        if (tokenfunc['message']=="token is valid"):
                data=request.get_json()
                self.email=data['email']
                x=0
                self.Monday=data['Monday']
                self.Tuesday=data['Tuesday']
                self.Wednesday=data['Wednesday']
                self.Thursday=data['Thursday']
                self.Friday=data['Friday']
                body=data['Body']
                days=[self.Monday,self.Tuesday,self.Wednesday,self.Thursday,self.Friday]
                for i in days:
                    if(i==1):
                        x=x+1
                if (self.Monday==1 and self.Tuesday==1):
                    return "you cannot pick consecutive days that follow monday and friday"
                elif (self.Monday==1 and self.Friday==1):
                    return "you cannot pick consecutive days that follow monday and friday"
                elif (self.Thursday==1 and self.Friday==1):
                    return "you cannot pick consecutive days that follow monday and friday"           
                elif(x>2):
                    return("Error you chose more than the required amount of days required to work remotely please select only two days ")
                else:
                    # try:
                    cursor.execute(os.getenv("monday"),(self.Monday,self.email))
                    cursor.execute(os.getenv("tuesday"),(self.Tuesday,self.email))
                    cursor.execute(os.getenv("wednesday"),(self.Wednesday,self.email))
                    cursor.execute(os.getenv("thursday"),(self.Thursday,self.email))
                    cursor.execute(os.getenv("friday"),(self.Friday,self.email))
                    cursor.execute(os.getenv("body"),(str(body),self.email))
                    cursor.execute(os.getenv("datesent"),(str(datetime.utcnow()),self.email))
                    connect.commit()
                    return{"message":"token is valid and scheduleddays assinged succefully",'Monday':bool(self.Monday),'Tuesday':bool(self.Tuesday),'Wednesday':bool(self.Wednesday),'Thursday':bool(self.Thursday),'Friday':bool(self.Friday)}
                    # except:
                    #     return{"message":("could not update scheduled days")}
        else :
            return{"message":tokenfunc['message']}
      
    def patch(self):
        data=request.get_json()
        self.email=data['email']
        tokenfunc=tokenauthent(self.email,str(os.getenv("key")))
        if (tokenfunc['message']=="token is valid"):
                data=request.get_json()
                self.email=data['email']
                x=0
                self.Monday=data['Monday']
                self.Tuesday=data['Tuesday']
                self.Wednesday=data['Wednesday']
                self.Thursday=data['Thursday']
                self.Friday=data['Friday']
                days=[self.Monday,self.Tuesday,self.Wednesday,self.Thursday,self.Friday]
                for i in days:
                    if(i==1):
                        x=x+1
                if (self.Monday==1 and self.Tuesday==1):
                    return "you cannot pick consecutive days that follow monday and friday"
                elif (self.Monday==1 and self.Friday==1):
                    return "you cannot pick consecutive days that follow monday and friday"
                elif (self.Thursday==1 and self.Friday==1):
                    return "you cannot pick consecutive days that follow monday and friday"           
                elif(x>2):
                    return("Error you chose more than the required amount of days required to work remotely please select only two days ")
                else:
                    try:
                        cursor.execute(os.getenv("monday"),(self.Monday,self.email))
                        cursor.execute(os.getenv("tuesday"),(self.Tuesday,self.email))
                        cursor.execute(os.getenv("wednesday"),(self.Wednesday,self.email))
                        cursor.execute(os.getenv("thursday"),(self.Thursday,self.email))
                        cursor.execute(os.getenv("friday"),(self.Friday,self.email))
                        cursor.execute(os.getenv("datesent"),(str(datetime.utcnow()),self.email))
                        connect.commit()
                        return{"message":"token is valid and scheduleddays assinged succefully",'Monday':bool(self.Monday),'Tuesday':bool(self.Tuesday),'Wednesday':bool(self.Wednesday),'Thursday':bool(self.Thursday),'Friday':bool(self.Friday)}
                    except:
                        return{"message":("could not update scheduled days")}

        else :
            return{"message":tokenfunc['message']}
      
api.add_resource(scheduledays,"/scheduleddays")
class logout(Resource):
    def post(self):
            data=request.get_json()
            self.email=data['email']
            loggedout=cursor.execute(os.getenv("tokenselect"),(self.email))
            for i in loggedout:
                pass
            token=i[0]
            decodedtoken=jwt.decode(token,key=str(os.getenv("key")), algorithms=['HS256'])
            decodedtoken['expiration']=str(datetime.utcnow() - timedelta(seconds=999))
            loggedouttoken=jwt.encode((decodedtoken),key=str(os.getenv("key")))
            try:
                cursor.execute(str(os.getenv("updatetoken")),str(loggedouttoken),self.email)
                connect.commit()
                return{"message":"you have been logged out succefully"}
            except:
                return{"message":"error login you out"}
            
        #pass in the login page
api.add_resource(logout,'/logout')



# IDENTITY MANAGEMENT


class roles(Resource):
    def get(self):
        data=request.get_json()
        self.email=data['email']
        tokenfunc=tokenauthent(self.email,"f9bb43fda47e9f127dee774b5f424a1b24b354bace8566e236770c70c3eabfed")
        if (tokenfunc['message']=="token is valid"):
            # to return available roles
            x=cursor.execute("Select [roles] , [Description_] FROM [employeedb].[dbo].[Roles] ")
            roles=[]
            for row in x:
                roles.append({"role" :row[0],"Description":row[1]})
            return jsonify(roles)
        else :
            return{"message":tokenfunc['message']}

    def post(self):
        data=request.get_json()
        self.email=data['email']
        tokenfunc=tokenauthent(self.email,str(os.getenv("key")))
        if (tokenfunc['message']=="token is valid"):
            try:
                cursor.execute(os.getenv("rolesinsert"),(data['Role'],data['DesignationID'],data['Description']))
                connect.commit()
                return{"message":"role added succesfully"}
            except:
                return {"message":"failed to add role"}
        else :
            return{"message":tokenfunc['message']}

api.add_resource(roles,"/roles")
class designtion(Resource):
    def get(self):
        data=request.get_json()
        self.email=data['email']
        tokenfunc=tokenauthent(self.email,str(os.getenv("key")))
        if (tokenfunc['message']=="token is valid"):
            # to return available roles
            x=cursor.execute(os.getenv("designationcreate"))
            roles=[]
            for row in x:
                roles.append({"Description":row[1],"Designation":row[0]})
            return jsonify(roles)
        else :
            return{"message":tokenfunc['message']}
    def post(self):
        data=request.get_json()
        self.email=data['email']
        tokenfunc=tokenauthent(self.email,str(os.getenv("key")))
        if (tokenfunc['message']=="token is valid"):
            try:
                cursor.execute(os.getenv("designationinsert"),(data['Designation'],data['Description']))
                connect.commit()
                return{"message":"desingtion added succesfully"}
            except:
                return {"message":"failed to add destination"}
        else :
            return{"message":tokenfunc['message']}
api.add_resource(designtion,"/designation")
if __name__ =="__main__":
    app.run(debug=True)
    