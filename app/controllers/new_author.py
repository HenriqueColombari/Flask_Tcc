from firebase import firebase

from app import app
from flask import Flask, Response, flash, redirect, render_template, request, session, abort, url_for

import gensim

import ast

import nltk
from nltk.tokenize import word_tokenize
from nltk.tokenize import sent_tokenize
from string import punctuation
from nltk.probability import FreqDist
from collections import defaultdict
from heapq import nlargest


firebase = firebase.FirebaseApplication('your_project_url', None)

@app.route("/new_author", methods=["GET", "POST"])
def new_author():
    result = request.form
    url = request.url
    person = request.args.get('person')
    person = ast.literal_eval(person)


    if person['is_logged_in']:
        if request.method == "POST":
            method = result['method']
            if method == "Inserir_Texto":
                autor = result['autor']
                input_text = result['input_text']
                input_titulo = result['input_titulo']

                texto = {
                'Autor' : autor,
                'Titulo' : input_titulo,
                'Usuario' : person['nome'],
                'Texto' : input_text
                }

                insert = firebase.post('/UserTexts', texto)

                user_authors = update_user_authores(person)

                return render_template("new_author.html",
                    places = user_authors,
                    person = person)

            elif method == "Inserir_Autor":
                input_nome = result['input_nome']
                input_genero = result['input_genero']

                insert_author = {
                    'Autor' : input_nome,
                    'Genero' : input_genero,
                    'Usuario' : person['nome']
                }

                insert = firebase.post('/NewAuthor', insert_author)

                user_authors = update_user_authores(person)

                response = render_template("new_author.html",
                    places = user_authors,
                    person = person)

                # return (response, 200, {'Refresh': '0;url=' + url, 'Cache-Control': "no-cache, no-store, must-revalidate"})
                return (response, 200)

            elif method == "Deletar_Autor":
                autor = result['autor']
                email = person['email']
                password = result['input_password']

                users = firebase.get('/Usuarios', None)
                users_list = [value for value in users.values()]
                users_values = []

                for i in range(len(users_list)):
                    users_values.append([users_list[i]['email'], users_list[i]['nome'], users_list[i]['senha']])

                for i in range(len(users_values)):
                    if users_values[i][0] == email and users_values[i][2] == password:
                        autor_personalizado = firebase.get('/NewAuthor', None)
                        autor_personalizado_list = [item for item in autor_personalizado.items()]
                        for k in range(len(autor_personalizado_list)):
                            if autor_personalizado_list[k][1]['Autor'] == autor:
                                delete = firebase.delete('/NewAuthor', autor_personalizado_list[k][0])

                user_authors = update_user_authores(person)

                return render_template("new_author.html",  
                places = user_authors,
                person = person)

            else:
                user_authors = update_user_authores(person)

                return render_template("new_author.html",  
                places = user_authors,
                person = person)

            
        else:
            user_authors = update_user_authores(person)

            return render_template("new_author.html",  
                places = user_authors,
                person = person)
    else:
        return redirect(url_for('login'))

@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return response


def update_user_authores(person):
    new_authors = firebase.get('/NewAuthor', None)
    
    authors_list = list(new_authors)

    authors_values = [value for value in new_authors.values()]

    user_authors = {}


    i = 0
    while i < len(authors_list):
        if authors_values[i]['Usuario'] == person['nome']:
            user_authors[authors_list[i]] = authors_values[i]
        i = i + 1

    return user_authors