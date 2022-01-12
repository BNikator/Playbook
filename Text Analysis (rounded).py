
# coding: utf-8

# In[1]:


import csv, pymorphy2, nltk, string, pandas
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
nltk.download('stopwords')

# Functions
# Tokenization
def tokenization(text):
  tokens = nltk.word_tokenize(text)
  tokens = [i for i in tokens if ( i not in string.punctuation )] #strip punctuation
  russianstopwords = stopwords.words('russian') #importing stopwords
  russianstopwords.extend(['что', 'это', 'так', 'вот', 'быть', 'как', 'в', '—', 'к', 'на', 'такое', 'также', 'например', 'либо', 'который', 'которое', 'из', 'вполне', 'вплоть', 'возможно', 'весь', 'for', 'by']) #extending stopwords
  tokens = [i for i in tokens if ( i not in russianstopwords )] #strip stopwords
  tokens = [i.replace('«', '').replace('»', '').replace('/', ' ') for i in tokens] #strip additional puntuation
  tokens = [i.lower() for i in tokens] #making lowercase
  for i in tokens:
    try:
      i = morph.parse(i)[0].inflect({'sing', 'nomn'}).word
    except:
      continue
  return tokens

# lemmatization
def lemmatization(tokens):
  newtokens = ' '
  morph = pymorphy2.MorphAnalyzer()
  for i in tokens:
    try:
      i = morph.parse(i)[0].inflect({'sing', 'nomn'}).word
      newtokens = newtokens + i + ' '
    except:
      i = i
      newtokens = newtokens + i + ' '
  return newtokens

# List Normalization and Lemmatization
def normlist(inilist):
  newlist = []
  #inilist = inilist[1:]
  for string in inilist:
    string = lemmatization(tokenization(string))
    newlist.append(string)
  return newlist

# TF-IDF analysis
def tfidf(corpus, ngram_range=(1,1)):
  global tokenlist
  global tfidfmeanrounded
  corpus = normlist(corpus)
  vect = TfidfVectorizer(ngram_range=ngram_range) #giving parameters to tf-idf module, to replace in __init__
  tfidf = vect.fit_transform(corpus).todense() #in numpy toarray returns an array; todense returns a matrix
  # print(pandas.DataFrame(tfidf, columns=vect.get_feature_names()).T) #prints tf-idf within given documents
  # print(pandas.DataFrame(tfidf.mean(0), columns=vect.get_feature_names()).T) #prints mean tf-idf within given corpus
  tokenlist = vect.get_feature_names()
  tfidfmean = tfidf.mean(0).tolist()[0] #tf-idf means which is matrix converted to list
  tfidfmeanrounded = []
  for i in tfidfmean:
    i = round(i,2)
    tfidfmeanrounded.append(i)
  return tokenlist, tfidfmeanrounded

# Terms from List[0] Per String in List[1] and Number of Strings in List[1] with Term from List[0]
def termsinlists(tokenlist, listofstrings):
  global tokenfreq
  global stringcount  
  tokenfreq = []
  stringcount = []
  for token in tokenlist:
    countokens = 0
    countstrings = 0
    for string in listofstrings:
      countokens = countokens + string.count(token)
      if token in string:
        countstrings = countstrings + 1
      else:
        countstrings = countstrings
    tokenfreq.append(round(countokens / len(listofstrings),2))
    stringcount.append(round(countstrings / len(listofstrings),2))
  return tokenfreq, stringcount

# Joining results from previous functions in single function that returns list of results from them
def textanalysis(feed, output):
  # Open feed
  with open(feed, newline='') as csvfile:
    # saving contents as special object reader
    reader = csv.reader(csvfile)
    # converting reader object into single list
    feedlist = list(reader)
    # giving variables to items in rows
    # hosts = feed[0]
    # mheaders = feed[1]
    # headers = feed[2]
    # fheaders = feed[3]
    # texts = feed[4]
    # anchors = feed[5]
    # alts = feed[6]
    result = []
    for row in feedlist:
      header = row[0]
      row = row[1:]
      for i in range(1,4):
        try:
          termsinlists(tfidf(normlist(row), ngram_range=(i,i))[0],normlist(row))
          rowresult = zip(*[tokenlist, tfidfmeanrounded, tokenfreq, stringcount])
        except ValueError:
          rowresult = zip(*[[],[],[],[]])
        result.append([[header + ' ' + str(i) ,'TF-IDF','Term Frequency','Document Frequency']])
        result.append(rowresult)
    with open(output, mode='w', newline='') as outputcsv:
      outputwriter = csv.writer(outputcsv, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
      outputwriter.writerow(['Текстовый анализ'])
      for container in result:
        for row in container:
          if 'TF-IDF' and 'Term Frequency' and 'Document Frequency' in row:
            outputwriter.writerow([])
            outputwriter.writerow(row)
          else:
            outputwriter.writerow(row)

# Working with document

    


#Tests
#1. Tokenization and Lemmatization
'''
test = 'Как выбрать выделенные сервер?; Аренда выделенных сервера для игр Counter Strike: Global Offensive'
test = tokenization(test)
print(test)
test = lemmatization(test)
print(test)

morph = pymorphy2.MorphAnalyzer()
tokens = ['выделенные', 'серверы', 'аренда']
print([morph.parse(i)[0].inflect({'sing', 'nomn'}).word for i in tokens])
print(lemmatization(tokens))
'''
#2. TF-IDF
'''
documents = [
    'This is a document.',
    'This is another document with slightly more text.',
    'Whereas this is yet another document with even more text than the other ones.',
    'This document is awesome and also rather long.',
    'The car he drove was red.'
]
print(tfidf(documents))
'''
#3. List Normalization and Lemmatization
'''
headers = ['H2-6', 'Выделенные серверы для вашего бизнеса, Условия размещения, Потребление трафика', 'КОНСТРУКТОР СЕРВЕРА, ГОТОВЫЕ КОНФИГУРАЦИИ СЕРВЕРОВ, БЕСПЛАТНО С КАЖДЫМ СЕРВЕРОМ, ДОПОЛНИТЕЛЬНЫЕ УСЛУГИ, УСЛОВИЯ РАЗМЕЩЕНИЯ', 'Как выбрать выделенный сервер?; Аренда выделенного сервера для игр Counter Strike: Global Offensive, Counter Strike 1.6, Minecraft, Arma III, Left for Dead 2, Team Fortress 2; Аренда выделенного сервера для сайтов и интернет-магазинов, порталов; Выделенные серверы для СМИ и медиа-порталов; Аренда выделенного сервера для финансовых операций и онлайн-торговли (forex, бирж, банков, аукционов); Выделенный сервер или VPS/VDS?']
print(normlist(headers))
'''
#4. Validating Feed
'''
print(headers)
'''
#5. Validating Feed Normalization and Lemmatization
'''
print(normlist(headers))
'''
#6. Validating TF-IDF on Feed
'''
headers = ['H2-6', 'Выделенные серверы для вашего бизнеса, Условия размещения, Потребление трафика', 'КОНСТРУКТОР СЕРВЕРА, ГОТОВЫЕ КОНФИГУРАЦИИ СЕРВЕРОВ, БЕСПЛАТНО С КАЖДЫМ СЕРВЕРОМ, ДОПОЛНИТЕЛЬНЫЕ УСЛУГИ, УСЛОВИЯ РАЗМЕЩЕНИЯ', 'Как выбрать выделенный сервер?; Аренда выделенного сервера для игр Counter Strike: Global Offensive, Counter Strike 1.6, Minecraft, Arma III, Left for Dead 2, Team Fortress 2; Аренда выделенного сервера для сайтов и интернет-магазинов, порталов; Выделенные серверы для СМИ и медиа-порталов; Аренда выделенного сервера для финансовых операций и онлайн-торговли (forex, бирж, банков, аукционов); Выделенный сервер или VPS/VDS?']
print(tfidf(normlist(headers), ngram_range=(2,2))
'''
#7. Validating Tokencount on Feed
'''
headers = ['H1', 'Выделенный сервер', 'АРЕНДА ВЫДЕЛЕННОГО СЕРВЕРА В РОССИИ — СКИДКИ НА XEON E3', 'Аренда выделенного сервера']
termsinlists(tfidf(normlist(headers), ngram_range=(2,2))[0],normlist(headers)[1:]) #passing first returned value from tfidf as tokens
print(tokenlist)
print(tfidfmean)
print(tokenfreq)
print(stringcount)
'''
#8. Validating Text Analysis Result

'D:\\Work\\Python Scripts\\Tex_Analysis_Feed.csv' #feed address
textanalysis('D:\\Work\\Python Scripts\\Tex_Analysis_Feed.csv','D:\\Work\\Python Scripts\\Tex_Analysis_Result.csv')

print('Done!')

