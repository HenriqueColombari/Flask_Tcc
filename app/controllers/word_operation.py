from firebase import firebase

from app import app
from flask import Flask, Response, redirect, render_template, request, url_for

from sklearn.manifold import TSNE
import pandas as pd 

import os

import io

import ast

from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

import nltk
from nltk.tokenize import word_tokenize
from nltk.tokenize import sent_tokenize
from nltk.corpus import stopwords
from string import punctuation

import gensim

firebase = firebase.FirebaseApplication('your_project_url', None)
autor_list = firebase.get('/Autores', None)
new_authors = firebase.get('/NewAuthor', None)

new_authors_list = list(new_authors)

new_authors_values = [value for value in new_authors.values()]

user_authors = {}

dirname = os.path.dirname(__file__)
filename = os.path.join(dirname, '../static/w2v_models/')

@app.route("/word_operation", methods=["GET", "POST"])
def word_operation():
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
            operation = result['operacao']
            palavra1 = result['palavra1'].lower()
            palavra2 = result['palavra2'].lower()
            autor = result['autor']


            return render_template('word_operation.html',
                autor = autor,
                check_value = check_value, 
                image = True,
                operacao = operation,
                palavra1 = palavra1,
                palavra2 = palavra2,
                places = autor_list,
                person = person,
                user_places = user_authors)


        else:    
            return render_template('word_operation.html',
                autor = "Nome", 
                image = False,
                palavra1 = '',
                palavra2 = '',
                places = autor_list,
                person = person,
                user_places = user_authors)
    else: 
        return redirect(url_for('login'))

@app.route('/plot.png')
def plot_png():

    textos = ''
    autor = request.args.get('autor')
    check_value = request.args.get('check_value')
    operation = request.args.get('operation') 
    palavra1 = request.args.get('palavra1').lower()
    palavra2 = request.args.get('palavra2').lower()
    person = request.args.get('person')
    person = ast.literal_eval(person)

    model = ''

    if check_value == '0':
        textos = firebase.get('/Textos', None)
        model = gensim.models.Word2Vec.load(filename + autor + '.model')

    elif check_value == '1':
        textos = firebase.get('/UserTexts', None)
        model = train_model(textos, autor, person)

    
    fig = create_figure(model, operation, palavra1, palavra2, autor)
    output = io.BytesIO()

    output.flush()

    FigureCanvas(fig).print_png(output)
    return Response(output.getvalue(), mimetype='image/png')

def create_figure(model, operation, palavra1, palavra2, autor):

    if model == False:
        fig = Figure()

        draw_word = 'O Autor Personalizado não possuí textos o suficiente.\n' + \
        'Volte para o menu inicial, Autores Personalizados e\n' + \
        'utilize a opção "Inserir novo Texto em um Autor Personalizado"\n' + \
        'para construir o vocabulário desse(a) autor(a)'

        word_subplot = fig.add_subplot(1,1,1)

        word_subplot.imshow(text_to_rgba(draw_word, color="black", fontsize=5, dpi=200))

        word_subplot.axis("off")

        return fig

    else:
        palavras = []
        estatisticas = []
        vocab = list(model.wv.index_to_key)

        palavra1_invocab = False
        palavra2_invocab = False

        if palavra1 in vocab:
            palavra1_invocab = True

        if palavra2 in vocab:
            palavra2_invocab = True

        if operation == "Adição" or operation == "Subtração": 
            if palavra1_invocab and palavra2_invocab: 
                data = [] 
                if operation == "Subtração":
                    for i in range(len(model.wv.most_similar(positive=[palavra1],negative=[palavra2]))):
                        palavras.append(model.wv.most_similar(positive=[palavra1],negative=[palavra2])[i][0])
                        data.append(model.wv[model.wv.most_similar(positive=[palavra1],negative=[palavra2])[i][0]])
                        estatisticas.append(str(model.wv.most_similar(positive=[palavra1],negative=[palavra2])[i][1]))

                elif operation == "Adição":
                    for i in range(len(model.wv.most_similar(positive=[palavra1, palavra2]))):
                        palavras.append(model.wv.most_similar(positive=[palavra1, palavra2])[i][0])
                        data.append(model.wv[model.wv.most_similar(positive=[palavra1, palavra2])[i][0]])
                        estatisticas.append(str(model.wv.most_similar(positive=[palavra1, palavra2])[i][1]))

                palavras.append(palavra1)
                palavras.append(palavra2) 
                data.append(model.wv[palavra1])
                data.append(model.wv[palavra2])

                

                draw_word  = 'Palavra, Semelhânça \n \n'

                for i in range(len(palavras) -2):
                    draw_word = draw_word + palavras[i] + ', ' + estatisticas[i]+ '\n'
                    

                tsne = TSNE(n_components=2) 
                data_tsne = tsne.fit_transform(data) 

                df = pd.DataFrame(data_tsne, index=palavras, columns=['x', 'y'])

                df_input = df.copy()

                for word, pos in df.iterrows():
                    if word == palavra1 or word == palavra2:
                        df = df.drop(index = word)
                    else:
                        df_input = df_input.drop(index = word)


                fig = Figure()
                

                word_subplot = fig.add_subplot(2,1,1)

                word_subplot.imshow(text_to_rgba(draw_word, color="black", fontsize=5, dpi=200))
                word_subplot.axis("off") 


                ax = fig.add_subplot(2, 1, 2)

                ax.scatter(df['x'], df['y'])

                ax.scatter(df_input['x'], df_input['y'], color = 'red')

                for word, pos in df.iterrows():
                    ax.annotate(word, pos)

                for word, pos in df_input.iterrows():
                    ax.annotate(word, pos)  

                return fig

            else:
                fig = Figure()

                draw_word = ''

                if  not palavra1_invocab and not palavra2_invocab:
                    draw_word = "Ambas as palavras não constam no vocabulário\nque possuímos de " + autor

                elif not palavra1_invocab:
                    draw_word = "A Palavra1 não constam no vocabulário\nque possuímos de " + autor

                elif not palavra2_invocab:
                     draw_word = "A Palavra1 não constam no vocabulário\nque possuímos de " + autor


                word_subplot = fig.add_subplot(1,1,1)

                word_subplot.imshow(text_to_rgba(draw_word, color="black", fontsize=5, dpi=200))

                word_subplot.axis("off")

                return fig


        elif operation == "Semelhânça": 

            data = []

            if palavra1_invocab:
                static_model = model.wv.most_similar(positive=[palavra1])
                for i in range(len(static_model)):
                    palavras.append(static_model[i][0])
                    data.append(model.wv[static_model[i][0]])

                    estatisticas.append(str(model.wv.most_similar(positive=[palavra1])[i][1]))

                palavras.append(palavra1)
                data.append(model.wv[palavra1])

                draw_word  = 'Palavra, Semelhânça \n \n'

                for i in range(len(palavras) - 1):
                    draw_word = draw_word + palavras[i] + ', ' + estatisticas[i]+ '\n'


                tsne = TSNE(n_components=2) 
                data_tsne = tsne.fit_transform(data) 

                df = pd.DataFrame(data_tsne, index=palavras, columns=['x', 'y'])   

                df_input = df.copy()

                for word, pos in df.iterrows():
                    if word == palavra1:
                        df = df.drop(index = word)
                    else:
                        df_input = df_input.drop(index = word)


                fig = Figure()


                        
                word_subplot = fig.add_subplot(2,1,1)
                word_subplot.imshow(text_to_rgba(draw_word, color="black", fontsize=5, dpi=200))
                word_subplot.axis("off") 


                ax = fig.add_subplot(2, 1, 2)

                ax.scatter(df['x'], df['y'])

                ax.scatter(df_input['x'], df_input['y'], color = 'red')

                for word, pos in df.iterrows():
                    ax.annotate(word, pos)

                for word, pos in df_input.iterrows():
                    ax.annotate(word, pos)  

                return fig

            else:
                fig = Figure()

                draw_word = 'A Palavra1 não constam no vocabulário\nque possuímos de ' + autor

                word_subplot = fig.add_subplot(1,1,1)

                word_subplot.imshow(text_to_rgba(draw_word, color="black", fontsize=5, dpi=200))

                word_subplot.axis("off")

                return fig

def text_to_rgba(s, *, dpi, **kwargs):
    fig = Figure(facecolor="none")
    fig.text(0, 0, s, **kwargs)
    buf = io.BytesIO()
    fig.savefig(buf, dpi=dpi, format="png", bbox_inches="tight", pad_inches=0)
    buf.seek(0)
    rgba = plt.imread(buf)
    return rgba

def read_input(salve): 
    for i in range(len(salve)):
        yield gensim.utils.simple_preprocess(salve[i])

def train_model(textos, autor, person):
    autor_texts = ''

    texts_number = 0

    textos_list = [value for value in textos.values()]

    i = 0
    while i < len(textos_list):
        if textos_list[i] is None:
            textos_list.pop(i)
            i = i - 1

        # elif textos_list[i]['Autor'] == autor:
        elif textos_list[i]['Autor'] == autor and textos_list[i]['Usuario'] == person['nome']:
            autor_texts = autor_texts + textos_list[i]['Texto']
            texts_number = texts_number + 1
        i = i + 1

    if texts_number > 0:

        sentencas = sent_tokenize(autor_texts)
        palavras = word_tokenize(autor_texts.lower())

        all_words = list(read_input(sentencas))
        stopwords_pt = set(stopwords.words('portuguese') + list(punctuation))

        no_stop_phrase = []
        no_stop_all = []

        for i in range(len(all_words)):
          for k in range(len(all_words[i])):
            if all_words[i][k] not in stopwords_pt:
              no_stop_phrase.append(all_words[i][k])
          no_stop_all.append(no_stop_phrase)
          no_stop_phrase = []

        documents = [x for x in no_stop_all if x != []]

        model = gensim.models.Word2Vec(documents, vector_size = 20, window=10, min_count=2, workers=10)

        model.train(documents, total_examples=len(documents), epochs=300)

        # model = gensim.models.Word2Vec(documents, vector_size = 50, window=10, min_count=2, workers=10)

        # model.train(documents, total_examples=len(documents), epochs=1000)

        # model.save(filename + autor + '.model')

        return model

    else:
        return False;