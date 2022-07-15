# coding: utf-8

# In[1]:


import csv, pymorphy2, nltk, string, pandas
from nltk.corpus import stopwords
nltk.download('punkt')
nltk.download('stopwords')

# Functions
# Tokenization
def tokenization(text):
    tokens = nltk.word_tokenize(text)
    tokens = [i for i in tokens if (i not in string.punctuation)]  # strip punctuation
    russianStopwords = stopwords.words('russian')  # importing stopwords
    russianStopwords.extend(
        ['что', 'это', 'так', 'вот', 'быть', 'как', 'в', '—', 'к', 'на', 'такое', 'также', 'например', 'либо',
         'который', 'которое', 'из', 'вполне', 'вплоть', 'возможно', 'весь', 'for', 'by'])  # extending stopwords
    tokens = [i for i in tokens if i not in russianStopwords]  # strip stopwords
    tokens = [i.replace('«', '').replace('»', '').replace('/', ' ') for i in tokens]  # strip additional puntuation
    tokens = [i.lower() for i in tokens]  # making lowercase
    return tokens


# Lemmatization
def lemmatization(tokens):
    newTokens = ''
    morph = pymorphy2.MorphAnalyzer()
    for i in tokens:
        try:
            i = morph.parse(i)[0].inflect({'sing', 'nomn'}).word
            newTokens = newTokens + i
        except:
            continue
    return newTokens

# List Normalization and Lemmatization
def normList(iniList):
    newList = []
    for string in iniList:
        string = lemmatization(tokenization(string))
        newList.append(string)
    return newList

# Noun checker
def nounChecker(newlist):
    nounsList = []
    morph = pymorphy2.MorphAnalyzer()
    for i in newlist:
        p = morph.parse(i)[0]
        if 'NOUN' in p.tag:
            nounsList.append(i)
        else:
            continue
    return nounsList

# Plural form
def makePlural(nounsList):
    pluralList = []
    morph = pymorphy2.MorphAnalyzer()
    for i in nounsList:
        try:
            i = morph.parse(i)[0].inflect({'plur'}).word
            pluralList.append(i)
        except:
            pluralList.append('none')
    return pluralList

# Joining results from previous functions in single function that returns list of results from them
def nounAnalysis(feed, output):
    # Open feed
    with open(feed, newline='', encoding='utf-8') as csvfile:
        # saving contents as special object reader
        reader = csv.reader(csvfile)
        # converting reader object into single list
        feedList = list(reader)
        nounsList = []
        # print(feedList)
        # list normalization and noun extraction
        i = 0
        for row in feedList:
            noun = nounChecker(normList(row))
            if noun != []:
                nounsList.append(noun)
            else:
                continue
            i += 1
            print('Выделение существительных ' + str(i))
        # cleaning lists in lists
        i = 0
        for noun in nounsList:
            nounsList[i] = noun[0]
            i += 1
            print('Чистка [] ' + str(i))
        # print(nounsList)
        # creating list of plural nouns
        pluralList = makePlural(nounsList)
        # print(pluralList)
        # zipping lists by columns
        rows = zip(nounsList, pluralList)
        with open(output, mode='w', newline='') as outputcsv:
            outputWriter = csv.writer(outputcsv, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            for row in rows:
                try:
                    outputWriter.writerow(row)
                except:
                    continue

# Working with document

# Tests
# 1. Tokenization and Lemmatization

print('Проверка токенизации: выбрать Как весь выделенные сервер?')
test = 'выбрать Как выделенные сервер?'
test = tokenization(test)
print(test)

print('Проверка лемматизации: Как выбрать весь выделенные сервер?')
test = lemmatization(test)
print(test)
'''
# 2. List Normalization and Lemmatization
'''
test = ['Выделенные', 'СЕРВЕРА', 'ГОТОВЫЕ', 'КОНФИГУРАЦИИ','для', 'электропила']
print('Проверка лемматизированного списка: Выделенные СЕРВЕРА ГОТОВЫЕ КОНФИГУРАЦИИ для электропила')
print(normList(test))
'''
# 3. Noun extraction
'''
test = normList(test)
print('Проверка существительных в списке: Выделенные СЕРВЕРА ГОТОВЫЕ КОНФИГУРАЦИИ для электропила')
print(nounChecker(test))
'''
# 4. Plural form
'''
test = nounChecker(test)
print('Проверка множественного числа для существительных: Выделенные СЕРВЕРА ГОТОВЫЕ КОНФИГУРАЦИИ для электропила')
print(makePlural(test))
'''
# 5. Validating Noun Analysis Result
'''
print('Проверка создания файла')
nounAnalysis('C:\\Users\\NikatorBV\\Downloads\\Feed for py.csv', 'C:\\Users\\NikatorBV\\Downloads\\Feed for py (Result).csv')

print('Done!')