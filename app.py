from flask import Flask , render_template , request , flash , url_for , redirect , session
from werkzeug.security import generate_password_hash , check_password_hash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Statement.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = "my_secret_key"
db = SQLAlchemy(app)

class Statement(db.Model):
    id = db.Column(db.Integer , primary_key = True)    
    date = db.Column(db.String(50) , nullable = False)
    name = db.Column(db.String(100) , nullable = False)
    amount = db.Column(db.Integer , nullable = False)
    catagory = db.Column(db.String(100) , nullable = False)

class User(db.Model):
    id = db.Column(db.Integer , primary_key = True)
    email = db.Column(db.String(100) , nullable = False)
    username = db.Column(db.String(100) , nullable = False)
    password_hash = db.Column(db.String(150) , nullable = False)

    def set_password(self , password):
        self.password_hash = generate_password_hash(password)

    def check_password(self , password):
        return check_password_hash(self.password_hash , password)

@app.template_filter()
def currencyFormat(value) :
    value = float(value)
    return "{:,.2f}".format(value)

@app.route("/")
def index():
    if "username" in session:
        return render_template("index.html")
    return render_template("loginPage.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username = username).first()
        if user and user.check_password(password):
            session['username'] = username
            flash("เข้าสู่ระบบสำเร็จ!", "success")
            return redirect(url_for("index"))
        else:
            flash("ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง", "danger")
            return render_template("loginPage.html")

    return render_template("loginPage.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form['email']
        username = request.form['username']
        password = request.form['password']

        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("มีผู้ใช้นี้แล้ว", "danger")
            return redirect(url_for("register"))

        new_user = User(email = email, username = username)
        new_user.set_password(password)  
        db.session.add(new_user)
        db.session.commit()
        flash("สมัครสมาชิกสำเร็จ! กรุณาเข้าสู่ระบบ", "success")
        return redirect(url_for("login"))

    return render_template("registerPage.html")

@app.route('/logout')
def logout():
    session.pop("username" , None)
    flash("ออกจากระบบเรีบร้อยเเล้ว" , "info")
    return redirect(url_for('login'))

@app.route("/addStatement" , methods = ["POST"])
def addStatement():
    date = request.form["date"]
    name = request.form["name"]
    amount = request.form["amount"]
    catagory = request.form["catagory"]
    statement = Statement(date = date , name = name , amount = amount , catagory = catagory)
    db.session.add(statement)
    db.session.commit()
    return redirect("/showData")
    
@app.route("/showData")
def showData() :
    statements = Statement.query.all()
    return render_template("statements.html" , statements = statements)

@app.route("/delete/<int:id>")
def deleteStatment(id) :
    state = Statement.query.filter_by(id = id).first()
    db.session.delete(state)
    db.session.commit()
    return redirect("/showData")

@app.route("/edit/<int:id>")
def editStatement(id) :
    state = Statement.query.filter_by(id = id).first()
    return render_template("editForm.html" , state = state) 

@app.route("/updateStatement" , methods = ["POST"])
def updateStatement() :
    id = request.form["id"]
    date = request.form["date"]
    name = request.form["name"]
    amount = request.form["amount"]
    catagory = request.form["catagory"]
    state = Statement.query.filter_by(id = id).first()
    state.date = date
    state.name = name
    state.amount = amount
    state.catagory = catagory
    db.session.commit()
    return redirect("/showData")

if __name__ == "__main__" :
    with app.app_context():
        db.create_all()
    app.run(debug = True)