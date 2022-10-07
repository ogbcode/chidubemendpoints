
from flask import Flask, request, redirect, jsonify
from flask_restful import Resource, Api
from flask_cors import CORS 
import pypyodbc as odbc 
import pandas as pd
import pyodbc
import os
from hashlib import sha256
import datetime
import jwt
import re


app = Flask(__name__)
api = Api(app)
CORS(app)
cors = CORS(app, resources={
    r"/*":{
        "origins": "*"
    }
})

app.config['SECRET_KEY'] = 'oluwapesealo'

def tokenauthent(Email,key):
        if 'tokenauth' in request.headers:
                token = request.headers['tokenauth']
                tokget=cursor.execute(str(os.getenv("tokenselect")), Email)
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
            return{"message":"token not included"}

def validemail(Email):
   pat = "^[a-zA-Z0-9-.]+@[a-zA-Z0-9]+\.[a-z]{1,3}$"
   if re.match(pat,Email):
      return True
   return False

def hash(data):
        hash_var=sha256((data).encode())
        finalhash=hash_var.hexdigest()
        return finalhash

SERVER='PESES-LAPTOP'
DATABASE='wemabank'
DRIVER='SQL Server Native Client 11.0'
USERNAME='sa'
PASSWORD='sa'
drivername='SQL SERVER'
servername='PESES-LAPTOP'
database='wemabank'
connection_string=f"""
DRIVER={{{drivername}}};
SERVER={servername};
DATABASE={database};
Trust_Connection=yes;
    """ 
connect = pyodbc.connect('Driver={SQL Server};'
            'Server=PESES-LAPTOP;'
            'Database=wemabank;'
            'Trusted_Connection=yes;')
connection_string1=f'mssql://{USERNAME}:{PASSWORD}@{SERVER}/{DATABASE}?driver={DRIVER}'
# connection_string=f'mssql://{str(os.getenv("USERNAME"))}:{str(os.getenv("PASSWORD"))}@{str(os.getenv("SERVER"))}/{str(os.getenv("DATABASE"))}?driver={str(os.getenv("DRIVER"))}'
cursor = connect.cursor()

class employees(Resource):

    def post( Email=''):
        content_type = request.headers.get('Content-Type')
        json = request.get_json()
        
        emailcheck = validemail(json['Email'])
        if emailcheck == True :
            names = json['Email']
            fnames, _, _ =names.partition("@") 
            name = fnames.split(".")
            fullname = ' '.join(name)
            Fullname = fullname
            success = "Successfully"
            readdata=odbc.connect(connection_string)
            SQL_Query=pd.read_sql_query('''select Email from AllStaff''',readdata)
            emailtable= pd.DataFrame(SQL_Query)


            Password=hash(json['unhashedpassword'])
            print(Password)
            cursor = connect.cursor()
            emailexist=(json["Email"] in emailtable['email'].unique())
            if (emailexist==True):
                    return "Email already exists "
            else:
                    cursor.execute('''INSERT INTO AllStaff VALUES (?,?,?,?,?, NULL,NULL, ? )''',(json["StaffID"], json["Email"],Password, Fullname , json["UnitID"],  json["DesignationID"]))
                    connect.commit()
                    success='sign up was successful'
                    return success
        else:
            return {"message":"Email does not match supported format"}

api.add_resource(employees,'/newuser')


class alltasks(Resource):

    def get(self,Email='', UnitID = ''):
        self.Email=Email
        self.UnitID=UnitID
        readdata=odbc.connect(connection_string)
        SQL_Query=pd.read_sql_query('''select *from Alltasks

                                        ''', readdata,)
        vrequests= SQL_Query.to_dict('records')
        return(vrequests)
    
api.add_resource(alltasks,'/alltasks')


class viewtask(Resource):
    def get(Email):
        Email = request.args['Email']
        
        readdata=odbc.connect(connection_string)
        SQL_Query=pd.read_sql_query('''select *from Alltasks where Email = ''' +Email, readdata)
        vtask= SQL_Query.to_dict('records')
        return(vtask)

api.add_resource(viewtask,'/alltasks/viewtask')


class teamapproval(Resource):

    def patch( self, Email='', Reason_for_TeamLead_Decline=''):
            self.Email = Email
            self.Reason_for_TeamLead_Decline = Reason_for_TeamLead_Decline
            Email = request.args['Email']
            content_type = request.headers.get('Content-Type')
            json = request.get_json()
            if json["TeamLead_Approval"] == 'True':
                
                cursor.execute('''update AllScheduleDays set TeamLead_Approval = 1 where Email ='''+Email)
                connect.commit()
                success = "True Update was successful"
                return success
            if json["TeamLead_Approval"] == 'False':
                
                cursor.execute('''update AllScheduleDays set TeamLead_Approval = 0 where Email = '''+Email) 
                cursor.execute('''update AllScheduleDays set Reason_for_TeamLead_Decline = ? where Email =?''',self.Reason_for_TeamLead_Decline, self.Email )
                connect.commit()
                success = "False Update was successful"
                return success
            else:
                failure = "Could not update"
                return failure

api.add_resource(teamapproval,'/alltasks/viewtask/teamleadapproval')


class linemanager(Resource):
    
        def patch( self, Email='', Reason_for_Linemanager_Decline=''):
            self.Email = Email
            self.Reason_for_Linemanager_Decline = Reason_for_Linemanager_Decline
            Email = request.args['Email']
            content_type = request.headers.get('Content-Type')
            json = request.get_json()
            if json["LineManager_Approval"] == 'True':
                
                cursor.execute('''update AllScheduleDays set LineManager_Approval = 1 where Email ='''+Email)
                connect.commit()
                success = "True Update was successful"
                return success
            if json["LineManager_Approval"] == 'False':
                
                cursor.execute('''update AllScheduleDays set LineManager_Approval = 0 where Email = '''+Email) 
                cursor.execute('''update AllScheduleDays set Reason_for_Linemanager_Decline = ? where Email =?''',self.Reason_for_Linemanager_Decline, self.Email )
                connect.commit()
                success = "False Update was successful"
                return success
            else:
                failure = "Could not update"
                return failure

api.add_resource(linemanager,'/alltasks/viewtask/linemanagerapproval')


class downloadreq(Resource):
    def get(Email):
        Email = request.args['Email']
        readdata=odbc.connect(connection_string)
        SQL_Query=pd.read_sql_query('''select *from AllScheduleDays where Email ='''+Email, readdata,)
        df = pd.DataFrame(SQL_Query)
        down = df.to_csv(Email+".csv")
        success = 'Download was successful'
        return success

    # def donwload(url, filename=''):
    #     downloadurl = '/allrequests/viewrequest/<string:Email>/linemanagerapproval/download'
    #     if filename:
    #         pass
    #     else:
    #         filename = req.url[downloadurl.rfind('/')+1:]

    #     with requests.get(url) as req:
    #         with open(filename, 'wb') as f:
    #             for chunk in req.iter_content(chunk_size =8192):
    #                 if chunk:
    #                     f.write(chunk)
    #         return filename
api.add_resource(downloadreq, '/alltasks/viewtask/linemanagerapproval/download')

#IDENTITY MANAGEMENT 

class units(Resource): 
    def get(Email=''):
            readdata=odbc.connect(connection_string)
            SQL_Query=pd.read_sql_query('''Select Unit FROM Unit''', readdata)
            unit= SQL_Query.to_dict('records')
            
            units = (unit)
            return jsonify(units)

api.add_resource(units,"/units")

class departments(Resource):
    def get(Email=''):
            readdata=odbc.connect(connection_string)
            SQL_Query=pd.read_sql_query('''Select Department_name FROM Department''', readdata)
            depart= SQL_Query.to_dict('records')
            
            departments =(depart)
            return jsonify(departments)

api.add_resource(departments,"/departments")

class newdepartments(Resource):

    def post(self,Email=''):
        self.Email=Email
        tokenfunc=tokenauthent(self.Email,str(os.getenv("key")))
        if (tokenfunc['message']=="token is valid"):
            content_type = request.headers.get('Content-Type')
            if (content_type == 'application/json'):
                json = request.get_json()
                print (json)
            else:
                return 'Error'

            cursor = connect.cursor()
            cursor.execute('''INSERT INTO Department VALUES (?,?)''',(json["Department_name"], json["Description"]))
            
            connect.commit()
            success='Department created successfully'
            return success

api.add_resource(newdepartments,"/departments/new")

class newunits(Resource):
    def post(self,Email=''):
        self.Email=Email
        tokenfunc=tokenauthent(self.Email,str(os.getenv("key")))
        if (tokenfunc['message']=="token is valid"):
            content_type = request.headers.get('Content-Type')
            if (content_type == 'application/json'):
                json = request.get_json()
                print (json)
            else:
                return 'Error'
            
            cursor = connect.cursor()
            cursor.execute('''INSERT INTO Unit VALUES (?,?,?)''',(json["Unit_name"], json["DepartmentID"], json["Description"]))
            
            connect.commit()
            success='Unit created successfully'
            return success

api.add_resource(newunits,"/units/new")


# class login(Resource):
#     def get(self,Email='',unhashedpassword=''):
#         cursor = connect.cursor()
#         self.Email=Email
#         password=hash(unhashedpassword)
#         self.connection_string=f'mssql://{USERNAME}:{PASSWORD}@{SERVER}/{DATABASE}?driver={DRIVER}'
#         self.ensgine = create_engine(self.connection_string)
#         self.connection=self.engine.connect()
#         sqltable=pd.read_sql_query('''SELECT * FROM employeetable2''',self.connection)
#         finaltable1=pd.DataFrame(sqltable)
#         emailauthentication=(self.Email in finaltable1['Email'].unique())
#         if (emailauthentication==True):
#             passwordauthentication=(password in finaltable1['Password'].unique())
#             if (passwordauthentication==True):
#                 # cursor = connect.cursor()
#                 # normalemployee=cursor.execute("select Status from employeetable2 where Email=? ",self.Email)
#                 # for i in normalemployee:
#                 #     pass
#                 # status=i[0]
#                 # if (status=="line manager"):
#                 #     employedas="you are a line manager"
#                 #     #redirct(/"linemanager")
#                 #     #take them line manger endpoint passed here
#                 # elif(status=="employee"):
#                 #     #redirect(/"employee")
#                 #     employedas="you are an employee"
#                 # else:
#                 #     employedas="you dont have a role yet"
#                 # cursor.execute("update employeetable2 set token = 1 where Email =? ",(self.Email))
#                 # connect.commit()
               
#                 # connectstat=" and you have been connected succesfully"
#                 success = 'Welcome User'
#                 return success            
#             else:
#                 employedas=""
#                 connectstat="incorrect password"
#         else:
#             employedas=""
#             connectstat= "user does not exist"
#         return employedas + ""+connectstat
# api.add_resource(login,'/login')
# class scheduledays(Resource):
#     def post(self,email,Monday,Tuesday,Wednesday,Thursday,Friday):
#         self.email=email
#         y=cursor.execute("select token from [employeedb].[chidubem].[employe]  where email=? ",(self.email))
#         for a in y:
#             pass
#         newexpiry=int(a[0])
#         if (newexpiry==1):
#             x=0
#             self.Monday=Monday
#             self.Tuesday=Tuesday
#             self.Wednesday=Wednesday
#             self.Thursday=Thursday
#             self.Friday=Friday
#             days=[self.Monday,self.Tuesday,self.Wednesday,self.Thursday,self.Friday]
#             for i in days:
#                 if(i==1):
#                     x=x+1
#             if (self.Monday==1 and self.Tuesday==1):
#                 return "you cannot pick consecutive days that follow monday and friday"
#             elif (self.Monday==1 and self.Friday==1):
#                 return "you cannot pick consecutive days that follow monday and friday"
#             elif (self.Thursday==1 and self.Friday==1):
#                 return "you cannot pick consecutive days that follow monday and friday"           
#             elif(x>2):
#                 return("Error you chose more than the required amount of days required to work remotely please select only two days ")
#             else:
#                 cursor.execute("update [employeedb].[chidubem].[employe] set monday = ? where email =? ",(self.Monday,self.email))
#                 cursor.execute("update [employeedb].[chidubem].[employe] set tuesday = ? where email =? ",(self.Tuesday,self.email))
#                 cursor.execute("update [employeedb].[chidubem].[employe] set wednesday = ? where email =? ",(self.Wednesday,self.email))
#                 cursor.execute("update [employeedb].[chidubem].[employe] set thursday = ? where email =? ",(self.Thursday,self.email))
#                 cursor.execute("update [employeedb].[chidubem].[employe] set friday = ? where email =? ",(self.Friday,self.email))
#                 pddays=cursor.execute("select monday,tuesday,wednesday,thursday,friday FROM [employeedb].[chidubem].[employe]  where email=?",(self.email))
#                 xy=pd.DataFrame(pddays)
#                 self.days={'Monday':bool(self.Monday),'Tuesday':bool(self.Tuesday),'Wednesday':bool(self.Wednesday),'Thursday':bool(self.Thursday),'Friday':bool(self.Friday)}
#                 return(self.days)
#         else:
#             return"your session has expired"
#     def patch(self,Monday,Tuesday,Wednesday,Thursday,Friday):
#         y=cursor.execute("select token from [employeedb].[chidubem].[employe]  where email=? ",(self.email))
#         for a in y:
#             pass
#         newexpiry=int(a[0])
#         if (newexpiry==1):
#             x=0
#             self.Monday=Monday
#             self.Tuesday=Tuesday
#             self.Wednesday=Wednesday
#             self.Thursday=Thursday
#             self.Friday=Friday
#             days=[self.Monday,self.Tuesday,self.Wednesday,self.Thursday,self.Friday]
#             for i in days:
#                 if(i==1):
#                     x=x+1
#             if(x>2):
#                 return("Error you chose more than the required amount of days required to work remotely please select only two days ")
#             else:
#                 cursor.execute("update [employeedb].[chidubem].[employe] set monday = ? where email =? ",(self.Monday,self.email))
#                 cursor.execute("update [employeedb].[chidubem].[employe] set tuesday = ? where email =? ",(self.Tuesday,self.email))
#                 cursor.execute("update [employeedb].[chidubem].[employe] set wednesday = ? where email =? ",(self.Wednesday,self.email))
#                 cursor.execute("update [employeedb].[chidubem].[employe] set thursday = ? where email =? ",(self.Thursday,self.email))
#                 cursor.execute("update [employeedb].[chidubem].[employe] set friday = ? where email =? ",(self.Friday,self.email))
#                 connect.commit()
#                 self.days={'Monday':bool(self.Monday),'Tuesday':bool(self.Tuesday),'Wednesday':bool(self.Wednesday),'Thursday':bool(self.Thursday),'Friday':bool(self.Friday)}
#                 return(self.days)
#         else:
#             return"your session has expired"
# api.add_resource(scheduledays,"/scheduleddays/<string:email>/<int:Monday>/<int:Tuesday>/<int:Wednesday>/<int:Thursday>/<int:Friday>")
# class logout(Resource):
#     def post(self,email):
#             self.email=email
#             cursor.execute("update [employeedb].[chidubem].[employe] set token = 0 where email =? ",(self.email))
#             connect.commit()
#             loggedout=cursor.execute("select token from [employeedb].[chidubem].[employe] where email=?",(self.email))
#             for i in loggedout:
#                 pass
#             a=i[0]
#             success=int(a)
#             if(success==0):
#                 #redirect('/login')
#                 return("you have been logged out succefully")
#             else:
#                 return("error login out")
            
#         #pass in the login page
# api.add_resource(logout,'/logout/<string:email>')

     


if __name__ == '__main__':
    app.run(debug =True)
#loopholes
#active directory
# can not pick days that consecutively follow friday and monday
# eg. Monday and Friday, Mondays and Tuesday
# line manager can not approve his own request, needs to be sent to a line manager of another department
#can not yet select whcich request to view
#uses static viewing
