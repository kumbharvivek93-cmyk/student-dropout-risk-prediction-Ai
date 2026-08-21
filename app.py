from flask import Flask,render_template,redirect,session,flash,request,url_for
from flask_sqlalchemy import SQLAlchemy  
from datetime import timedelta,datetime
import joblib

app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///students.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False   
db=SQLAlchemy(app) 
app.permanent_session_lifetime=timedelta(days=2)
app.secret_key='vivekkali'
model=joblib.load("C:/Users/vivek kumbhar/Desktop/student risk predictor/model/vivekmodel.pkl")
scaler=joblib.load("C:/Users/vivek kumbhar/Desktop/student risk predictor/model/scaler.pkl")


class Students_sy_AI_C(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(50),nullable=False)     
    email=db.Column(db.String(50),nullable=False)
    roll_no=db.Column(db.String(50),nullable=False)
    mobile_no=db.Column(db.String(13),nullable=False)
    DOB=db.Column(db.DateTime,nullable=False)   
    address=db.Column(db.String(30),nullable=False)

class Admin(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(30),nullable=False)
    password=db.Column(db.String(30),nullable=False)

# with app.app_context():
#     db.create_all()                     
#     print("database is created")

def string_validator(sample):
    if sample.strip()=='' or len(sample)<2:
        return f'enter a valid username or password'

def prediction_score(backlogs, attendence, privious_year_cgpa, internal_marks, assi, score_of_attentation):
    obs = scaler.transform([[
        backlogs,
        attendence,
        privious_year_cgpa,
        internal_marks,
        assi,
        score_of_attentation
    ]])

    rep = round(float(model.predict(obs)[0]), 2)
    return rep

def give_category(resp):
    cat=None
    if 60<resp<1000:
        cat='High'
        return cat
    if 30<resp<60:
        cat='Medium'
        return cat
    if -100<resp<30:
        cat='Low'
        return cat


@app.route("/",methods=['GET','POST'])     
def home():
    return render_template('index.html')
   

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method=='POST':
        username=request.form.get("username")
        password=request.form.get("password")

        string_validator(username)
        string_validator(password)

        user=Admin.query.filter_by(username=username).first()

        if user and user.password==password:
            flash('logged in successfully!')
            return redirect(url_for('predict'))
        else:
            flash('user not found')
            return redirect(url_for('home'))
    else:
        return render_template("login.html")

@app.route('/predict',methods=['GET','POST'])
def predict():
    if request.method=='POST':
        name=request.form.get('name')
        attendence=int(request.form.get('attendence'))
        privious_year_cgpa=float(request.form.get('privious_year_cgpa'))      # use random forest regressor
        internal_marks=int(request.form.get('internal_marks'))
        backlogs=int(request.form.get('backlogs'))
        assi=int(request.form.get('assi'))
        score_of_attentation=int(request.form.get('score'))

        string_validator(name)

        resp=[backlogs,attendence,privious_year_cgpa,internal_marks,assi,score_of_attentation]
        respo=prediction_score(backlogs,attendence,privious_year_cgpa,internal_marks,assi,score_of_attentation)
        category=give_category(respo)
        return f'the risk is {respo} and category is {category}'
    else :
        return render_template('predict.html')





        

if __name__=='__main__':  # running conditions
    app.run(debug=True)
