from flask import Flask , render_template , request , redirect
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Statement.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Statement(db.Model):
    id = db.Column(db.Integer , primary_key = True)    
    date = db.Column(db.String(50) , nullable = False)
    name = db.Column(db.String(100) , nullable = False)
    amount = db.Column(db.Integer , nullable = False)
    catagory = db.Column(db.String(100) , nullable = False)

with app.app_context():
    db.create_all()

@app.template_filter()
def currencyFormat(value) :
    value = float(value)
    return "{:,.2f}".format(value)

@app.route("/")
def index():
    return render_template("index.html")

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
    app.run(debug = True)