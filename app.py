from flask import Flask, render_template, request, url_for
from flask_pymongo import PyMongo
from flask_wtf import FlaskForm
from wtforms import StringField, DateField, SelectField, DecimalField
from wtforms.validators import InputRequired
from datetime import date
import requests

app = Flask(__name__)

app.config["SECRET_KEY"]="cop4813"
app.config["MONGO_URI"]="mongodb+srv://cop4813:5770425@learningmongodb.1xbgs.mongodb.net/db?retryWrites=true&w=majority"

mongo = PyMongo(app)

class Expenses(FlaskForm):
    #Stringfield for description
    #Selectfield for category and another for currency
    #Decimalfield for cost
    #Datefield for date
    string_input = StringField(validators=[InputRequired()])
    select_input = SelectField(
        choices=[('harddrives', 'Hard Drives'), ('gpus', 'GPUs'), ('cpus', 'CPUs'), ('monitors', 'Monitors'),
                 ('headsets', 'Headsets'), ('keyboards', 'Keyboards'), ('mice', 'Mice'), ('psus', 'PSUs')])
    decimal_input = DecimalField(default=0)
    select_input_currency = SelectField(
        choices=[('usd', 'US Dollar'), ('inr', 'Indian Rupee'), ('mxn', 'Mexican Peso'), ('eur', 'Euro'),
                 ('jpy', 'Japanese Yen'), ('cad', 'Canadian Dollar'), ('gbp', 'British Pound Sterling')])
    date_input = DateField(format='%m/%d/%Y', default=date.today())


def get_total_expenses(category):
    #access the database and add the cost of all documents that are a part of the category passed as input parameter
    total_category_expenses = 0
    query = {"category": category}
    for x in mongo.db.expenses.find(query):
        total_category_expenses += float(x['cost'])
    return total_category_expenses

@app.route('/')
def index():
    my_expenses = mongo.db.expenses.find()
    total_cost = 0
    for i in my_expenses:
        total_cost += float(i['cost'])

    #Display total cost of each category by calling the get_total_expenses function for each category
    expensesByCategory = [('Hard Drives', get_total_expenses("harddrives")), ('GPUs', get_total_expenses("gpus")),
                          ('CPUs', get_total_expenses("cpus")), ('Monitors', get_total_expenses("monitors")),
                          ('Headsets', get_total_expenses("headsets")), ('Keyboards', get_total_expenses("keyboards")),
                          ('Mice', get_total_expenses("mice")), ('PSUs', get_total_expenses("psus"))]
    return render_template("index.html",expenses=total_cost,expensesByCategory=expensesByCategory)

@app.route('/addExpenses',methods=["GET","POST"])
def addExpenses():
    expensesForm = Expenses(request.form)
    if request.method == "POST":
        #Save user inputs to variables
        stringinput = request.form['string_input']
        selectinput = request.form['select_input']
        decimalinput = request.form['decimal_input']
        currencyinput = request.form['select_input_currency']
        dateinput = request.form['date_input']

        # Insert one document to the database containing the data logged by the user
        expenseEntry = {'description': stringinput,
                        'category': selectinput,
                        'cost': currency_converter(decimalinput, currencyinput), #Call currency_converter for cost
                        'date': dateinput}
        mongo.db.expenses.insert_one(expenseEntry)

        return render_template("expenseAdded.html")
    return render_template("addExpenses.html", form=expensesForm)


def currency_converter(cost,currency):
    #Call currencylayer API and save JSON to variable
    url="http://api.currencylayer.com/live?access_key=553e60be067a25184a1a998796f336f1"
    response = requests.get(url).json()

    #If currency is not USD, convert it and return the USD value. Else return original value
    converted_cost = 0
    if currency != 'usd':
        code = ('usd' + currency).upper() #code to find exchange rate in dictionary/json
        converted_cost = round(float(cost) / response['quotes'][code], 2) #converting cost and rounding to 2 dec. places
    else:
        return cost
    return converted_cost


app.run()

