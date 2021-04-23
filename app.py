from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
import sqlalchemy
from flask import Flask, render_template, abort, session, redirect, request
import joblib
import numpy as np

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root@localhost/Diabetes_app"
app.config["SECRET_KEY"] = "mysecretkeywhichissupposedtobesecret"

db = SQLAlchemy(app)
admin = Admin(app)


class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))
    Comment = db.Column(db.Text)
    lab_result = db.Column(db.String(255))
    date_posted = db.Column(db.DateTime)
    Dr_Sign = db.Column(db.String(255))


# db.create_all()


class SecureModelView(ModelView):
    def is_accessible(self):
        if "logged_in" in session:
            return True
        else:
            abort(403)


admin.add_view(SecureModelView(Posts, db.session))


model = joblib.load("model.pkl")


@app.route("/")
def host():
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if (
            request.form.get("username") == "oscar"
            and request.form.get("password") == "admin123"
        ):
            session["logged_in"] = True
            return redirect("/admin")
        else:
            return render_template("login.html", failed=True)
    return render_template("login.html")


@app.route("/home")
def home():
    return render_template("home.html")


@app.route("/about_diabetes")
def about_diabetes():
    return render_template("about_diabetes.html")


@app.route("/working")
def working():
    return render_template("working.html")


@app.route("/userinput")
def input():
    return render_template("userinput.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


@app.route("/userinput", methods=["POST"])
def predict():
    if request.method == "POST":
        pregnancies = int(request.form["pregnancies"])
        glucose = int(request.form["glucose"])
        blood_pressure = int(request.form["blood_pressure"])
        skin_thickness = int(request.form["skin_thickness"])
        insulin = int(request.form["insulin"])
        BMI = float(request.form["BMI"])
        DPF = float(request.form["DPF"])
        age = int(request.form["age"])
        data = np.array(
            [
                [
                    pregnancies,
                    glucose,
                    blood_pressure,
                    skin_thickness,
                    insulin,
                    BMI,
                    DPF,
                    age,
                ]
            ]
        )

        answer = model.predict(data)

        if answer == 0:
            return render_template("congratulations.html")

        else:
            return render_template("alert.html")


app.run(debug=True)
