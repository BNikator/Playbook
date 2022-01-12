# coding: utf-8

import csv, nltk, string, pandas
from nltk.corpus import stopwords
from nltk.corpus import wordnet
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer

nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('averaged_perceptron_tagger')

lemmatizer = WordNetLemmatizer()

# Functions
# POS tagging
def get_wordnet_pos(word):
  """Map POS tag to first character lemmatize() accepts"""
  tag = nltk.pos_tag([word])[0][1][0].upper()
  tag_dict = {"J": wordnet.ADJ,
              "N": wordnet.NOUN,
              "V": wordnet.VERB,
              "R": wordnet.ADV}
  return tag_dict.get(tag, wordnet.NOUN)

# Tokenization
def tokenization(text):
  tokens = nltk.word_tokenize(text)
  tokens = [i for i in tokens if ( i not in string.punctuation )] #strip punctuation
  english_stopwords = stopwords.words('english') #importing stopwords
  english_stopwords.extend(['—', 'for', 'by']) #extending stopwords
  tokens = [i for i in tokens if ( i not in english_stopwords )] #strip stopwords
  tokens = [i.replace('«', '').replace('»', '').replace('/', ' ').replace('_', ' ') for i in tokens] #strip additional puntuation
  tokens = [i.lower() for i in tokens] #making lowercase
  for i in tokens:
    try:
      i = lemmatizer.lemmatize(i, get_wordnet_pos(i))
    except:
      i = i
  return tokens

# lemmatization
def lemmatization(tokens):
  newtokens = ' '
  for i in tokens:
    try:
      i = lemmatizer.lemmatize(i, get_wordnet_pos(i))
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
  with open(feed, newline='', encoding='utf-8') as csvfile:
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
      outputwriter.writerow(['Text Analysis'])
      for container in result:
        for row in container:
          if 'TF-IDF' and 'Term Frequency' and 'Document Frequency' in row:
            outputwriter.writerow([])
            outputwriter.writerow(row)
          else:
            outputwriter.writerow(row)

# Running the script
'D:\\Work\\Python Scripts\\Text_Analysis_Feed.csv' #feed address

textanalysis('D:\\Work\\Python Scripts\\Text_Analysis_Feed.csv','D:\\Work\\Python Scripts\\Text_Analysis_Result.csv')

print('Done!')

