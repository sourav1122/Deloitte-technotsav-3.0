from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
import calendar, time
from flask import request
import json
import requests
import ast
import gFit


app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)
class User(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=True)
    avatar = db.Column(db.String(200))
    active = db.Column(db.Boolean, default=True)
    tokens = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow())
    nodemcu = db.Column(db.Text, default='')
    def __repr__(self):
       return {'id':self.id,'email':self.email,'name':self.name,'avatar':self.avatar,'active':self.active,'token':self.tokens,'created at':self.created_at,'nodemcu':self.nodemcu}

####################### calling of refresh token function ###############################

def new_access_token(refresh_token):
    data = {
      'grant_type': 'refresh_token',
      'client_id': "552833547680-pf5eserplcmvsnmt18jp4197ru21u0u5.apps.googleusercontent.com",
      'client_secret': "8x44hBSsgxOwBezTqXqMbNQD",
      #   'refresh_token':"1//0grv2p2xFhVucCgYIARAAGBASNwF-L9IrlelcE5TTtkyaxnAf1T2UddBCz3egbyGLzPCBlBF1MEd3CgniF6Lauu8jgwLWSsPr0J0"
      'refresh_token': refresh_token
    }

    response = requests.post('https://oauth2.googleapis.com/token', data=data)
    # print(response.json())
    resp = response.json()
    new_refresh_token = refresh_token
    if 'refresh_token' in resp:
      new_refresh_token = resp['refresh_token']
    return resp["access_token"] , new_refresh_token
    
########################end of refresh token functn ##############################

def toggle_light(nodemcu, state):
  vars = nodemcu['vars']
  vars['LED_STATUS'] = state
  headers = {
    'Content-Type': 'application/json'
  }
  payload = "{\"LED_STATUS\":"+str(state)+"}"
  resp = requests.patch(url=nodemcu['url'], headers=headers, data=payload)
  # print(resp.json())
  return nodemcu

########################   main_user_functn  ###############################



fgh=1
while(fgh):
  fgh=0
  
  all_user=User.query.all()
  for i in all_user:
    if not i.active:
      continue
    
    # print("i.nodemcu" , i.nodemcu)
    # print("i.created_at" , i.created_at)
    # print("i.tokens" , i.tokens)
    # tok = ast.literal_eval(i.tokens)
    # print("refresh_token" , tok["refresh_token"])
    # tok['refresh_token'] = '1//0gLCiGWGZiCcoCgYIARAAGBASNwF-L9IrBDx2rcyoZIyDuhTZqEcwgG7PUxz2xESgtgdxBaJ6WEACnoD9TmdZw7qr8qCBO7weiiI'
    # i.tokens = str(tok)
    # db.session.commit()
    # print("access_token" , tok["access_token"])
    # print("refresh_token" , tok["refresh_token"])

    # if i.active:
    #   continue
    tok = ast.literal_eval(i.tokens)
    ctime = int(calendar.timegm(time.strptime(str(i.created_at), '%Y-%m-%d %H:%M:%S.%f')))
    # ctime is in sec
    # if atleat 15 min left to expire
    # print(int(round(time.time())))
    # print(ctime)
    # if i.active:
    #   continue
    if int(round(time.time())) - ctime < 2700 :
      # print('access_token not expired')
      access_token = tok["access_token"]
    else :
      # print('getting new access_token')
      access_token, refresh_token = new_access_token(tok["refresh_token"])
      i.created_at = datetime.utcnow()
      tok["access_token"] = access_token
      if refresh_token != tok["refresh_token"]:
        tok["refresh_token"] = refresh_token

    # print("access_token" , access_token)
    # print(i.created_at)

    endTimeMillis = int(round(time.time() * 1000))
    startTimeMillis = endTimeMillis - 1800000
    # if gFit.is_sleeping(startTimeMillis, endTimeMillis, access_token):
    if gFit.is_sleeping(1584157920000, 1584157920001, access_token):
      print("sleeping")
      i.nodemcu = str( toggle_light(ast.literal_eval(i.nodemcu), 0) )
    else:
      print("Not sleeping")
      i.nodemcu = str( toggle_light(ast.literal_eval(i.nodemcu), 1) )
    
    i.tokens = str(tok)
    db.session.commit()
