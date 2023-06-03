from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize
from tkinter import *
from tkinter import scrolledtext
from tkinter import messagebox
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import ujson

stemmer = PorterStemmer()
stop_words = stopwords.words('english')
tfidf = TfidfVectorizer()

with open('publication_list_stemmed.json', 'r') as file:
    pub_list_first_stem = ujson.load(file)
with open('publication_indexed_dictionary.json', 'r') as file:
    pub_index = ujson.load(file)
with open('publication_list_stemmed2.json', 'r') as file:
    pub_list_first_stem2 = ujson.load(file)
with open('publication_indexed_dictionary2.json', 'r') as file:
    pub_index2 = ujson.load(file)
with open('publication_name.json', 'r') as file:
    pub_name = ujson.load(file)
with open('publication_url.json', 'r') as file:
    pub_url = ujson.load(file)
with open('publication_cu_author.json', 'r') as file:
    pub_cu_author = ujson.load(file)
with open('publication_date.json', 'r') as file:
    pub_date = ujson.load(file)


def publication_data(input=None):
    outputData.delete(1.0, END)
    outcome.delete(0, END)
    inputText = inputBar.get()
    abc = {}
    if operator.get() == 2:
        outputData.configure(fg='white')
        inputText = inputText.lower().split()
        pointer = []
        for token in inputText:
            if len(inputText) < 2:
                messagebox.showinfo(title="Hello!!!", message="Please enter at least 2 words to apply operator.")
                break
            if len(token) <= 3:
                messagebox.showinfo("Error!!!", "Please enter more than 4 characters.")
                break
            stem_temp = ""
            stem_word_file = []
            temp_file = []
            word_list = word_tokenize(token)

            for x in word_list:
                if x not in stop_words:
                    stem_temp += stemmer.stem(x) + " "
            stem_word_file.append(stem_temp)

            indexed_from = 1
            if pub_index.get(stem_word_file[0].strip()):
                pointer = pub_index.get(stem_word_file[0].strip())
            else:
                # stem_word_file = []
                if len(inputText) == 1:
                    pointer = []

            if len(pointer) == 0:
                if pub_index2.get(stem_word_file[0].strip()):
                    pointer = pub_index2.get(stem_word_file[0].strip())
                indexed_from = 2

            if len(pointer) == 0:
                abc = {}
            else:
                if indexed_from == 1:
                    for j in pointer:
                        temp_file.append(pub_list_first_stem[j])
                if indexed_from == 2:
                    for j in pointer:
                        temp_file.append(pub_list_first_stem2[j])
                temp_file = tfidf.fit_transform(temp_file)
                cosine_output = cosine_similarity(temp_file, tfidf.transform(stem_word_file))

                if indexed_from == 1:
                    if pub_index.get(stem_word_file[0].strip()):
                        for j in pointer:
                            abc[j] = cosine_output[pointer.index(j)]

                if indexed_from == 2:
                    if pub_index2.get(stem_word_file[0].strip()):
                        print("writing")
                        for j in pointer:
                            abc[j] = cosine_output[pointer.index(j)]

    else:
        outputData.configure(fg='brown')
        inputText = inputText.lower().split()

        indexed_from = 1
        pointer = []
        match_word = []
        for token in inputText:
            if len(inputText) < 2:
                messagebox.showinfo("Error!!!", "Please enter at least 2 words to apply operator.")
                break
            if len(token) <= 3:
                messagebox.showinfo("Error!!!", "Please enter more than 4 characters.")
                break
            temp_file = []
            set2 = set()
            stem_word_file = []
            word_list = word_tokenize(token)
            stem_temp = ""
            for x in word_list:
                if x not in stop_words:
                    stem_temp += stemmer.stem(x) + " "
            stem_word_file.append(stem_temp)

            if pub_index.get(stem_word_file[0].strip()):
                set1 = set(pub_index.get(stem_word_file[0].strip()))
                pointer.extend(list(set1))

                if match_word == []:
                    match_word = list({z for z in pointer if z in set2 or (set2.add(z) or False)})
                else:
                    match_word.extend(list(set1))
                    match_word = list({z for z in match_word if z in set2 or (set2.add(z) or False)})
                indexed_from = 1
            else:
                if pub_index2.get(stem_word_file[0].strip()):
                    set1 = set(pub_index2.get(stem_word_file[0].strip()))
                    pointer.extend(list(set1))

                    if match_word == []:
                        match_word = list({z for z in pointer if z in set2 or (set2.add(z) or False)})
                    else:
                        match_word.extend(list(set1))
                        match_word = list({z for z in match_word if z in set2 or (set2.add(z) or False)})
                else:
                    pointer = []
                indexed_from = 2

        if len(inputText) > 1:
            match_word = {z for z in match_word if z in set2 or (set2.add(z) or False)}

            if len(match_word) == 0:
                abc = {}
            else:
                if indexed_from == 1:
                    for j in list(match_word):
                        temp_file.append(pub_list_first_stem[j])
                if indexed_from == 2:
                    for j in list(match_word):
                        temp_file.append(pub_list_first_stem2[j])

                temp_file = tfidf.fit_transform(temp_file)
                cosine_output = cosine_similarity(temp_file, tfidf.transform(stem_word_file))

                for j in list(match_word):
                    abc[j] = cosine_output[list(match_word).index(j)]
        else:
            if len(pointer) == 0:
                abc = {}
            else:
                if indexed_from == 1:
                    for j in pointer:
                        temp_file.append(pub_list_first_stem[j])
                if indexed_from == 2:
                    for j in pointer:
                        temp_file.append(pub_list_first_stem2[j])

                temp_file = tfidf.fit_transform(temp_file)
                cosine_output = cosine_similarity(temp_file, tfidf.transform(stem_word_file))

                for j in pointer:
                    abc[j] = cosine_output[pointer.index(j)]

    aa = 0
    rank_sorting = sorted(abc.items(), key=lambda z: z[1], reverse=True)
    for a in rank_sorting:
        outputData.insert(INSERT, "Rank: ")
        outputData.insert(INSERT, "{:.2f}".format(a[1][0]))
        outputData.insert(INSERT, "\n")
        outputData.insert(INSERT, 'Title: ' + pub_name[a[0]] + "\n")
        outputData.insert(INSERT, 'URL: ' + pub_url[a[0]] + "\n")
        outputData.insert(INSERT, 'Date: ' + pub_date[a[0]] + "\n")
        outputData.insert(INSERT, 'Cov_Uni_Author: ' + pub_cu_author[a[0]] + "\n")
        outputData.insert(INSERT, "\n")

        aa = aa + 1
    if aa == 0:
        messagebox.showinfo("Error!!!", "No results found. TRY AGAIN!!!")
    outcome.insert(END, aa)


# GUI build steps
window = Tk()
print(window)
window.configure(bg='#ffffff')
window.geometry('1920x1080')
label = Label(window, width=100, text="Search Engine", bg="#f3f3f3", fg="black", font="'Arial' 24 bold")
label.config(anchor=CENTER)
label.pack()
apply = Label(window, text='LOGIC:')
count = Label(window, text='TOTAL SEARCHED RESULTS :')
outcome = Entry(window, width=7)
inputBar = Entry(window, width=30)
inputBar.pack()
inputBar.place(x=50, y=110)
count.place(x=50, y=80)
outcome.place(x=255, y=80)
outputData = scrolledtext.ScrolledText(window, width=190, height=47)
outputData.place(x=50, y=150)
search = Button(window, text='SEARCH', bg="#ffffff", fg="#ffffff", font="'Arial' 10", command=publication_data).place(x=350, y=110)
operator = IntVar()
operator.set(2)
rb_and = Radiobutton(window, text='AND', value=1, variable=operator, command=publication_data)
rb_or = Radiobutton(window, text='OR', value=2, variable=operator, command=publication_data)
apply.place(x=620, y=50)
rb_and.place(x=680, y=50)
rb_or.place(x=750, y=50)
window.bind('<Return>', publication_data)
window.mainloop()
