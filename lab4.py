# -*- coding: utf-8 -*-
import operator

import nltk
import sqlite3
import spacy

from tkinter import ttk
from tkinter import *

from deep_translator import GoogleTranslator

db = sqlite3.connect('db.sqlite3')
cursor = db.cursor()

nlp = spacy.load('de_core_news_md')

translator = GoogleTranslator(source='de', target='en')

grammar = r"""
        V: {<V.*>}
        N: {<NN.*|PRP>}
        P: {<IN>}
        NP: {<N|PP>+<DT|CD|PR.*|JJ|CC>}
        NP: {<DT|CD|PR.*|JJ|CC><N|PP>+}
        NP: {<DT><NP>}
        PP: {<P><NP>}
        VP: {<NP|N><V.*>}
        VP: {<V.*><NP|N>}
        VP: {<VP><PP>}
        """


def draw_tree(text):
    nltk.download('averaged_perceptron_tagger_eng')


    if text != '':
        doc = nltk.word_tokenize(text)
        doc = nltk.pos_tag(doc)
        new_doc = []
        for item in doc:
            if item[0] not in [',', '.', '-', ':', ';', '?', '!']:
                new_doc.append(item)
        cp = nltk.RegexpParser(grammar)
        result = cp.parse(new_doc)
        result.draw()


def google_translate(text):
    sentence = []
    new_text = ''
    for sent in nltk.sent_tokenize(text):
        translate = translator.translate(sent)
        sentence.append(translate)
        new_text += translate + ' '
    return sentence


def grammar_text(sent):
    word = {}
    text = ''.join(sent)
    list_word = text.split(' ')
    for item in list_word:
        if item not in word:
            word.update({item: 1})
        else:
            word[item] += 1
    sorted_word = sorted(word.items(), key=operator.itemgetter(1))
    new_list_word = []
    for item, _ in sorted_word:
        if item:
            parse_word = nlp(item)
            tag = parse_word[0].pos_
            new_list_word.append((item, _, str(tag)))
    with open('translate.txt', 'w', encoding='utf-8') as f:
        f.write(str(new_list_word))


def db_and_google_translate(text):
    phrase = []
    sentence = []
    new_text = ''
    for word in cursor.execute("SELECT * FROM Dict"):
        word = tuple([word[0], word[1]])
        phrase.append(word)
    for sent in nltk.sent_tokenize(text):
        new_sent = ''
        i = 0
        while i < len(phrase):
            if phrase[i][1] in sent:
                sent.replace(phrase[i][1], phrase[i][0])
            i += 1
        new_sent += translator.translate(sent)
        sentence.append(new_sent)
        new_text += new_sent + ' '
    return sentence


def print_sentence(translator_name):
    child_window = Toplevel(root)
    child_window.title("Перевод")
    if translator_name == 'google':
        sentence = google_translate(text=calculated_text.get(1.0, END))
    else:
        sentence = db_and_google_translate(text=calculated_text.get(1.0, END))
    grammar_text(sentence)
    i = 0
    k = 0
    new_dict = {}
    while i < len(sentence):
        label_item = Label(child_window, text=str(i + 1) + '. ' + sentence[i])
        label_item.grid(row=i, column=1)
        new_dict.update({i + 1: sentence[i]})
        i += 1
        k = i
    number = Text(child_window, height=1, width=3)
    number.grid(row=k + 1, column=1, sticky='nsew', rowspan=1, columnspan=1)
    button_draw = Button(child_window, text="Дерево", width=15,
                         command=lambda: draw_tree(new_dict[int(number.get(1.0, END))]))
    button_draw.grid(row=k + 2, column=1)


def add_trans_to_db(eng, de):
    sql = 'INSERT INTO Dict(english, german) VALUES("' + str(eng.replace('\n', '')) \
          + '", "' + str(de.replace('\n', '')) + '")'
    cursor.execute(sql)
    db.commit()


root = Tk()
root.title("Перевод")
ttk.Separator(root).place(x=0, y=14, relwidth=1)
label = Label(root, text='Введите текст')
label.grid(row=0, column=1)
calculated_text = Text(root, height=15, width=70)
calculated_text.grid(row=1, column=0, sticky='nsew', rowspan=3, columnspan=4)
button1 = Button(text="Перевод бд+google", width=15, command=lambda: print_sentence('bd'))
button1.grid(row=1, column=4)
button2 = Button(text="Перевод google", width=15, command=lambda: print_sentence('google'))
button2.grid(row=2, column=4)
ttk.Separator(root).place(x=0, y=280, relwidth=1)
label = Label(root, text='Добавить в бд')
label.grid(row=4, column=1)
label_de = Label(root, text='немецкое слово:')
label_de.grid(row=5, column=2)
label_eng = Label(root, text='английское слово:')
label_eng.grid(row=6, column=2)
text_eng = Text(root, height=1, width=20)
text_eng.grid(row=6, column=3)
text_de = Text(root, height=1, width=20)
text_de.grid(row=5, column=3)
button_add = Button(root, text="Добавить", width=15,
                    command=lambda: add_trans_to_db(text_eng.get(1.0, END),
                                                    text_de.get(1.0, END)))
button_add.grid(row=6, column=4)
root.mainloop()
