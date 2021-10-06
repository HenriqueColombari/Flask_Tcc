from firebase import firebase

from app import app
from flask import Flask, flash, redirect, render_template, request, session, abort, url_for

import gensim

import ast

import nltk
from nltk.tokenize import word_tokenize
from nltk.tokenize import sent_tokenize
from nltk.corpus import stopwords
from string import punctuation
from nltk.probability import FreqDist
from collections import defaultdict
from heapq import nlargest


firebase = firebase.FirebaseApplication('your_project_url', None)
autor_list = firebase.get('/Autores', None)
new_authors = firebase.get('/NewAuthor', None)

new_authors_list = list(new_authors)

new_authors_values = [value for value in new_authors.values()]

user_authors = {}


stopwords = set(stopwords.words('portuguese') + list(punctuation))

@app.route("/resume", methods=["GET", "POST"])
def resume():
    person = request.args.get('person')
    person = ast.literal_eval(person)

    i = 0
    while i < len(new_authors_list):
        if new_authors_values[i]['Usuario'] == person['nome']:
            user_authors[new_authors_list[i]] = new_authors_values[i]
        i = i + 1


    if person['is_logged_in']:
        if request.method == "POST":
            result = request.form
            check_value = result['user_authors_check']
            initial_text = result['input_text']
            autor = result['autor']

            app.logger.info(check_value)

            if check_value == '0':
                textos = firebase.get('/Textos', None)
                autor_texts = ''

                textos_list = [value for value in textos.values()]

                i = 0
                while i < len(textos_list):
                    if textos_list[i] is None:
                        textos_list.pop(i)
                        i = i - 1

                    elif textos_list[i]['Autor'] == autor:
                        autor_texts = autor_texts + textos_list[i]['Texto']
                    i = i + 1

                input_text = ''.join([i for i in initial_text if not i.isdigit()])

                sentencas = sent_tokenize(input_text)
                palavras = word_tokenize(autor_texts.lower())

                palavras_sem_stopwords = [palavra for palavra in palavras if palavra not in stopwords]

                frequencia = FreqDist(palavras_sem_stopwords)

                sentencas_importantes = defaultdict(int)

                for i, sentenca in enumerate(sentencas):
                    for palavra in word_tokenize(sentenca.lower()):
                        if palavra in frequencia:
                            sentencas_importantes[i] += frequencia[palavra]

                idx_sentencas_importantes = nlargest(4, sentencas_importantes, sentencas_importantes.get)

                output_text = ""
                for i in sorted(idx_sentencas_importantes):
                    output_text = output_text + ' ' + str(sentencas[i])

                output_text.replace("\r\n",  "<br>")
                return render_template("resume.html", 
                    input_text = initial_text, 
                    output_text = output_text, 
                    places = autor_list,
                    person = person,
                    user_places = user_authors)
            

            elif check_value == '1':
                textos = firebase.get('/UserTexts', None)
                autor_texts = ''

                textos_list = [value for value in textos.values()]

                i = 0
                texts_number = 0
                while i < len(textos_list):
                    if textos_list[i] is None:
                        textos_list.pop(i)
                        i = i - 1

                    elif textos_list[i]['Autor'] == autor and textos_list[i]['Usuario'] == person['nome']:
                        texts_number = texts_number + 1
                        autor_texts = autor_texts + textos_list[i]['Texto']
                    i = i + 1

                if texts_number > 0:

                    input_text = ''.join([i for i in initial_text if not i.isdigit()])

                    sentencas = sent_tokenize(input_text)
                    palavras = word_tokenize(autor_texts.lower())

                    palavras_sem_stopwords = [palavra for palavra in palavras if palavra not in stopwords]

                    frequencia = FreqDist(palavras_sem_stopwords)

                    sentencas_importantes = defaultdict(int)

                    for i, sentenca in enumerate(sentencas):
                        for palavra in word_tokenize(sentenca.lower()):
                            if palavra in frequencia:
                                sentencas_importantes[i] += frequencia[palavra]

                    idx_sentencas_importantes = nlargest(4, sentencas_importantes, sentencas_importantes.get)

                    output_text = ""
                    for i in sorted(idx_sentencas_importantes):
                        output_text = output_text + ' ' + str(sentencas[i])

                    output_text.replace("\r\n",  "<br>")
                    return render_template("resume.html", 
                        input_text = initial_text, 
                        output_text = output_text, 
                        places = autor_list,
                        person = person,
                        user_places = user_authors)

                elif texts_number == 0:
                    return render_template("resume.html", 
                        input_text = initial_text, 
                        output_text = "O Autor Personalizado não possuí textos o suficiente.", 
                        places = autor_list,
                        person = person,
                        user_places = user_authors)
        else:
            return render_template("resume.html",  
                input_text = "", 
                output_text = "" ,
                places = autor_list,
                person = person,
                user_places = user_authors)
    else:
        return redirect(url_for('login'))