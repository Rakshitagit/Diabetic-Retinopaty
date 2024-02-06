from flask import Flask,render_template,request,session
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
import os
from flask_login import login_user,logout_user,login_manager,LoginManager
from flask_login import login_required,current_user
from werkzeug.security import generate_password_hash,check_password_hash
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.image import load_img, img_to_array
import numpy as np
from flask import Flask, request, render_template
from werkzeug.utils import secure_filename


local_server= True
app = Flask(__name__)
app.secret_key='diabetic'

# this is for getting unique user access
login_manager=LoginManager(app)
login_manager.login_view='login'



@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:root@localhost/diabeticdb'
db = SQLAlchemy(app)


class User(UserMixin,db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fname = db.Column(db.String(100), unique=True, nullable=False)
    lname = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), unique=True, nullable=False)


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/menu")
def menu():
    return render_template("menu.html")



@app.route("/signup",methods=['POST','GET'])
def signup():
    if request.method=='POST':
        fname=request.form.get("fname")
        lname=request.form.get("lname")
        email=request.form.get("email")
        password=request.form.get("password")
        user=User.query.filter_by(email=email).first()
        if user:
            print("user already Exist")
            return render_template("/signup.html",a="Email Already Exist")

        new_user=db.engine.execute(f"INSERT INTO `user`(`fname`,`lname`,`email`,`password`)VALUES('{fname}','{lname}','{email}','{password}')")
        return render_template("/login.html")   
    return render_template("signup.html")

@app.route("/login",methods=['POST','GET'])
def login():
    if request.method=='POST':
        email=request.form.get("email")
        password=request.form.get("password")
        user=User.query.filter_by(email=email,password=password).first()
        if user:
            return render_template("/menu.html")
        else:
            return render_template("/login.html",a="Invalid username & password")
    return render_template("login.html")

model_path = "model.h5"

AutoNet = load_model(model_path)

classes = {0:"Mild",1:"Moderate",2:"No_DR",3:"Proliferate_DR",4:"Severe"}

def model_predict(image_path,model):
    print("Predicted")
    image = load_img(image_path,target_size=(224,224))
    image = img_to_array(image)
    image = image/255
    image = np.expand_dims(image,axis=0)
    
    result = np.argmax(model.predict(image))
    prediction = classes[result]
    
    
    if result == 0:
        print("Mild.html")
        
        return "Mild","Mild.html"
    elif result == 1:
        print("Moderate.html")
        
        return "Moderate", "Moderate.html"

    elif result == 2:
        print("No_DR.html")
        
        return "No_DR" , "No_DR.html"
    elif result==3:
        print("Proliferate_DR.html")
        
        return "Proliferate_DR" , "Proliferate_DR.html"
    elif result==4:
        print("Severe.html")
        
        return "Severe" , "Severe.html"



@app.route("/predict",methods=['POST','GET'])
def predict():
    
    print("Entered")
    if request.method=='POST':
        print("Entered here")
        file = request.files['image'] # fet input
        filename = file.filename        
        print("@@ Input posted = ", filename)
        
        file_path = os.path.join('static/user uploaded', filename)
        file.save(file_path)

        print("@@ Predicting class......")
        pred, output_page = model_predict(file_path,AutoNet)
              
        return render_template(output_page, pred_output = pred, user_image = file_path)


@app.route("/prediction")
def prediction():
    return render_template("prediction.html")


if __name__ == "__main__":
    app.run(debug=True)
    