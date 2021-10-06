from app import app
from firebase import firebase
from flask import Flask, flash, redirect, render_template, request, session, abort, url_for

firebase = firebase.FirebaseApplication('your_project_url', None)
person = {"is_logged_in": False, "nome": "", "email": "", "uid": ""}

@app.route("/",  methods=["GET", "POST"])
def login():
	usuarios = firebase.get('/Usuarios', None)
	return render_template("login.html", places = usuarios)

@app.route("/welcome")
def welcome():
    if person["is_logged_in"] == True:
        return render_template("welcome.html", person = person)
    else:
        try:
            person_temp = request.args.get('person')
            person_temp = ast.literal_eval(person_temp)
            if person_temp['is_logged_in'] == True:
                return render_template("welcome.html", person = person_temp)
        except:
            return redirect(url_for('login'))

#If someone clicks on login, they are redirected to /result
@app.route("/result", methods = ["POST", "GET"])
def result():
    if request.method == "POST":        #Only if data has been posted
        result = request.form           #Get the data
        email = result["email"]
        password = result["pass"]

        results = firebase.get('/Usuarios', None)
        results_list = [value for value in results.values()]
        results_values = []

        for i in range(len(results_list)):
            results_values.append([results_list[i]['email'], results_list[i]['nome'], results_list[i]['senha']])

        for i in range(len(results_values)):
            if results_values[i][0] == email and results_values[i][2] == password:
                global person
                person["is_logged_in"] = True
                person["email"] = email
                person["uid"] = list(results.keys())[i]
                person['nome'] = results_values[i][1]

                return redirect(url_for('welcome', person = person))
        return redirect(url_for('login'))

    else:
        if person["is_logged_in"] == True:
            return redirect(url_for('welcome', person = person))
        else:
            return redirect(url_for('login'))

#If someone clicks on register, they are redirected to /register
@app.route("/register", methods = ["POST", "GET"])
def register():
    if request.method == "POST":        #Only listen to POST
        result = request.form           #Get the data submitted
        email = result["email"]
        nome = result["nome"]
        password = result["pass"]

        results = firebase.get('/Usuarios', None)
        results_list = [value for value in results.values()]
        results_values = []
        email_list = []
        for i in range(len(results_list)):
            results_values.append([results_list[i]['email'], results_list[i]['nome'], results_list[i]['senha']])
            email_list.append(results_list[i]['email'])

        
        if email not in email_list:
            new_user = {
                    'email' : email,
                    'nome' :  nome,
                    'senha' : password
                } 

            insert = firebase.post('/Usuarios',new_user)
            results = firebase.get('/Usuarios', None)
            results_list = [value for value in results.values()]
            results_values = []

            for i in range(len(results_list)):
                results_values.append([results_list[i]['email'], results_list[i]['nome'], results_list[i]['senha']])

            for i in range(len(results_list)):
                if results_values[i][0] == email and results_values[i][2] == password:
                    global person
                    person["is_logged_in"] = True
                    person["email"] = email
                    person["uid"] = list(results.keys())[i]
                    person['nome'] = results_values[i][1]

            return redirect(url_for('welcome', person = person))
        else:
            return redirect(url_for('login'))


    else:
        if person["is_logged_in"] == True:
            return redirect(url_for('welcome', person = person))
        else:
            return redirect(url_for('login'))