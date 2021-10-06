from app import app
from flask import Flask, flash, redirect, render_template, request, session, abort, url_for

import ast

@app.route("/info")
def info():
	person = request.args.get('person')
	person = ast.literal_eval(person)

	if person["is_logged_in"] == True:
		return render_template("info.html", person = person)

	else:
		return redirect(url_for('login'))