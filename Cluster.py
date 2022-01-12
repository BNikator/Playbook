
# coding: utf-8

# In[ ]:


# Add volume to list

import pandas, numpy
from scipy import spatial
from multiprocessing import Pool

'''-----'''
# Initial setup
'''-----'''

# Creating dictionary of TOP form Excel list
df = pandas.read_excel('D:\\Keyword Clustering\\Feed_Yandex.xlsx' , usecols = 'A,H:R')
dictionary = df.set_index('Feed').T.to_dict('list')
print('Dictionary len: ' + str(len(dictionary))) # test
print('--------------')

# Creating dictionary of volumes from Excel list
df = pandas.read_excel('D:\\Keyword Clustering\\Feed_Yandex.xlsx' , usecols = 'A:G')
volume_dict = df.set_index('Feed').T.to_dict('list')
print(volume_dict) # test
print('--------------')

# Creating immutable initial dictionary
ini_dictionary = dictionary.copy()
# print(ini_dictionary)

# Creating dimensions list (vector space) (not cleaned yet)
dimensions = []
for key in dictionary:
  for url_list in dictionary[key]:
    dimensions.append(url_list)

# Cleaning nan in dimensions
dimensions = [url for url in dimensions if url is not numpy.nan]

# Loop to clean outliers
counter = 0
outliers = [] # list of outliers
while True:
  counter += 1
  # print('round ' + str(counter)) # test
  
  # Finding URLs that are repeated across collection
  multiple_urls = [] 
  for url in dimensions:
    if dimensions.count(url) > 1:
      multiple_urls.append(url)
    else:
      continue
  multiple_urls = list(set(multiple_urls))
  
  # Finding keys from dictionary that have less than 3 repeated urls
  keys_to_delete = []
  for key in dictionary:
    i = 0
    for url in multiple_urls:
      if url in dictionary[key]:
        i += 1
    if i < 3:
      # print(i) # test
      # print('key is:') # test
      # print(key) # test
      keys_to_delete.append(key)
      outliers.append(key)
        
  # print('keys_to_delete are:') # test
  # print(keys_to_delete) # test
  
  # Removing keys from list keys_to_delete from dictionary
  for key in keys_to_delete:
    del dictionary[key]
    
  # Creating dimensions list (vector space)
  dimensions = []
  for key in dictionary:
    for url_list in dictionary[key]:
      dimensions.append(url_list)
      
  # Cleaning nan in dimensions
  dimensions = [url for url in dimensions if url is not numpy.nan]
    
  # Exiting loop if no more outliers left
  if keys_to_delete == []:
    # print('Outliers are:') # test
    # print('--------------') # test
    # print(outliers) # test
    break

'''
print('Cleaned dictionary')
print(dictionary) # test
print('--------------') # test
'''

# Cleaning duplicates in dimesions
dimensions = list(set(dimensions))

'''
print('Dimensions')
print(dimensions) #test
'''

# One hot encoding (creating vectors in vector space) for keys in dictionary according to dimensions (vector space)
vectors = {}
for key in dictionary:
  vector = []
  for dimension in dimensions:
    if dimension in dictionary[key]:
      vector.append(1)
    else:
      vector.append(0)
  vectors.update({key: vector})

'''
print('Vectors')
print(vectors) # test
'''

# Creating immutable initial vectors
ini_vectors = vectors.copy()

'''-----'''
# Functions that are needed
'''-----'''

# Calculating cosine similarities for keys vectors
def cosine_similarities(vectors):
  similarities = {}
  for key1 in vectors:
    key_similarities = {} # creates dictionary with similarities for one key with other keys
    for key2 in vectors:
      if key1 != key2:
        key_similarities.update({key2: 1 - spatial.distance.cosine(vectors[key1], vectors[key2])})
      else:
        continue
    # print(key_similarities) # test
    similarities.update({key1: key_similarities})
  # print(similarities) # test
  return similarities

# Updating similarities with using initial cosine similarities in order not to recalculate them
def cosine_similarities_update(similarities, new_vectors):
  new_similarities = {}
  keys_to_delete = []
  key_similarities = {}
  for key in similarities:
    if key in new_vectors:
      new_similarities[key] = similarities[key]
    if key not in new_vectors:
      keys_to_delete.append(key)
  for key in new_similarities:
    for delete_key in keys_to_delete:
      try:
        del new_similarities[key][delete_key]
      except:
        continue
  for key1 in new_vectors:
    if key1 not in new_similarities:
      # print(key1)
      for key2 in new_vectors:
        # print(key2)
        if key2 == key1:
          continue
        key_similarities.update({key2: 1 - spatial.distance.cosine(new_vectors[key1], new_vectors[key2])})
        if key1 != key2:
          new_similarities[key2].update({key1: key_similarities[key2]})
      new_similarities[key1] = key_similarities
      break
    else:
      continue
  # print(new_similarities)
  return new_similarities
        
'''
We shall make so that we can combine multiple values at the same step if those values are not intersected.
So we find MAX similarity across matrix, and IF two queries with MAX similarity AND it is >=0.5 then we assume 
them as a cluster, and make them unclusterable, then we find next MAX value and if it is not using queries from the previous step AND it is 
>=0.5 then we assume them as the next cluster, if it is using unclusterable queries, then CONTINUE. 
After non left — Break, calculate new clusters. Make step 2 with the new clusters.
'''

# Finding maximum value in similarities
def max_similar(similarities):
  pd = pandas.DataFrame(similarities) # Converting to dataframe in order to find initial max similarity value
  maximum_rows = pd.max()
  absolute_maximum = maximum_rows.max() # returns array
  absolute_maximum = numpy.asscalar(absolute_maximum) # converting array to scalar
  # print(absolute_maximum) # test
  return absolute_maximum

# Finding maximum indices in vectors
def max_keys(similarities, absolute_maximum):
  for key1 in similarities:
    for key2 in similarities[key1]:
      if similarities[key1][key2] == absolute_maximum:
        absolute_maximum_keys = [key1, key2]
        return absolute_maximum_keys
      else:
        continue

# Adding new cluster to clusters (for 0.5)
def add_cluster(clusters, key1, key2):
  if key1 in clusters and key2 in clusters:
    for index in range(len(clusters[key2])):
      clusters[key1].append(clusters[key2][index])
    del clusters[key2]
    cluster_index = key1
    new_cluster = [clusters, cluster_index]
    # print('New Cluster')
    # print(new_cluster) # test
    return new_cluster
  
  elif key1 in clusters:
    clusters[key1].append(key2)
    cluster_index = key1
    new_cluster = [clusters, cluster_index]
    # print('New Cluster')
    # print(new_cluster) # test
    return new_cluster
  
  elif key2 in clusters:
    clusters[key2].append(key1)
    cluster_index = key2
    new_cluster = [clusters, cluster_index]
    # print('New Cluster')
    # print(new_cluster) # test
    return new_cluster
  
  else:
    clusters.update({key1 + ' ' + str(len(key1) + len(key2)) : [key1, key2]})
    cluster_index = key1 + ' ' + str(len(key1) + len(key2))
    new_cluster = [clusters, cluster_index]
    # print('New Cluster')
    # print(new_cluster) # test
    return new_cluster

# Function that calculates centroid of vectors
def center(cluster_index):
  centroid = []
  for index in range(len(dimensions)):
    listi = []
    sumi = 0
    for key in clusters[cluster_index]:
      # print('key in ' + str(cluster_index) + ' ' + str(key)) # test
      listi.append(ini_vectors[key][index])
    for item in listi:
      sumi += item
    centroid.append(sumi / len(clusters[cluster_index]))
  # print(centroid) # test
  return centroid

# Updating vectors
def vectors_update(vectors, cluster_index, centroid, key1, key2):
  del vectors[key1]
  del vectors[key2]
  vectors.update({cluster_index : centroid})
  return vectors

'''-----'''
# Building loop with clusters creation
'''-----'''

# Creating dictionary of clusters
clusters = {}

# Iterations counter
round_counter = 1

# Giving base absolute_maximum to start loop
absolute_maximum = 0.5

# Clustering Loop
similarities = cosine_similarities(vectors) # initial cosine similarities

'''
print('Initial Similarities') # test
print(similarities) # test
'''

while True:
  print('--------------')
  print('Round ' + str(round_counter)) # test
  loop_must_break = False
  absolute_maximum = max_similar(similarities)
  if absolute_maximum >= 0.3:
    print(absolute_maximum) #test
    
    # Finding keys of absolute_maximum
    absolute_maximum_keys = max_keys(similarities, absolute_maximum)
    # print(absolute_maximum_keys) #test
    key1 = absolute_maximum_keys[0]
    print('key1') #test
    print(key1) #test
    key2 = absolute_maximum_keys[1]
    print('key2') #test
    print(key2) #test
    
    # Checking if keys are clusters already
    if key1 in clusters and key2 in clusters:
      print('If both in clusters')
      # Calculating similarities between keys in clusters
      count_similarities = []
      for key_a in clusters[key1]:
        for key_b in clusters[key2]:
          i = 0
          for url in dictionary[key_a]:
            if url in dictionary[key_b]:
              i += 1
          count_similarities.append(i)
      print('count_similarities')
      print(count_similarities)
      
      # Checking if >= 3 similarities between keys in clusters  
      for i in count_similarities:
        if i >= 3:
          continue
        else:
          print('Similarities < 3 for each key')
          while True:
            similarities_to_loop_and_strip = similarities
            print('Similarities in loop before strip')
            print(similarities_to_loop_and_strip)
            del similarities_to_loop_and_strip[key1][key2]
            del similarities_to_loop_and_strip[key2][key1]
            print('Similarities in loop after strip')
            print(similarities_to_loop_and_strip)
            absolute_maximum = max_similar(similarities_to_loop_and_strip)
            print('Absolute Maximum')
            print(absolute_maximum)
            if absolute_maximum >= 0.3:
              
              # Finding keys of absolute_maximum
              absolute_maximum_keys = max_keys(similarities, absolute_maximum)
              # print(absolute_maximum_keys) #test
              key1 = absolute_maximum_keys[0]
              print('key1') #test
              print(key1) #test
              key2 = absolute_maximum_keys[1]
              print('key2') #test
              print(key2) #test
       
              # Checking if keys are clusters already
              if key1 in clusters and key2 in clusters:
                print('If both in clusters')
                # Calculating similarities between keys in clusters
                count_similarities = []
                for key_a in clusters[key1]:
                  for key_b in clusters[key2]:
                    i = 0
                    for url in dictionary[key_a]:
                      if url in dictionary[key_b]:
                        i += 1
                    count_similarities.append(i)
                print('Similarities')
                print(count_similarities)
                
              # Checking if only first key is in clusters already
              elif key1 in clusters:
                print('If key1 in clusters')
                # Calculating similarities between keys in clusters
                count_similarities = []
                for key_a in clusters[key1]:
                  i = 0
                  for url in dictionary[key_a]:
                    if url in dictionary[key2]:
                        i += 1
                  count_similarities.append(i)
                print('Similarities')
                print(count_similarities)  
                  
              # Checking if only second key is in clusters already
              elif key2 in clusters:
                print('If key2 in clusters')
                # Calculating similarities between keys in clusters
                count_similarities = []
                for key_a in clusters[key2]:
                  i = 0
                  for url in dictionary[key_a]:
                    if url in dictionary[key1]:
                        i += 1
                  count_similarities.append(i)
                print('Similarities')
                print(count_similarities)
                              
              # Checking if both keys are not in clusters
              else:
                print('If both not in clusters')
                # Calculating similarities between keys in clusters
                count_similarities = []
                i = 0
                for url in dictionary[key2]:
                  if url in dictionary[key1]:
                    i += 1
                count_similarities.append(i)
                print('Similarities')
                print(count_similarities)  
            
            else:
              print('Absolute Maximum < 0.3')
              loop_must_break = True
              break            
      
            # Checking if >= 3 similarities between keys in clusters
            three_similarities = 0
            for i in count_similarities:
              if i < 3:
                break
              else:
                three_similarities += 1
            print('Three Similarities')
            print(three_similarities)
            if len(count_similarities) == three_similarities:
              print('Similarities >= 3 for each key')
              # Adding cluster
              new_cluster = add_cluster(clusters, key1, key2)
              clusters = new_cluster[0]
              print('Clusters')
              print(clusters) # test
              cluster_index = new_cluster[1]
              print('Cluster Index')
              print(cluster_index) # test
              # print(clusters[cluster_index]) # test
               
              # Calculating Centroid
              centroid = center(cluster_index)
                
              # Updating vector space
              new_vectors = vectors_update(vectors, cluster_index, centroid, key1, key2)
                
              # Recalculating new similarities for updated vector space
              similarities = cosine_similarities_update(similarities, new_vectors)
              # print(similarities) # test
              # print(vectors) # test
              # print('--------------') # test
              round_counter += 1
              loop_must_break = True
              break
            else:
              print('Similarities < 3 for each key')
          if loop_must_break == True:
            break
      
      if loop_must_break == True:
        continue
      
      print('MAX similarity OK')
      # Adding cluster
      new_cluster = add_cluster(clusters, key1, key2)
      clusters = new_cluster[0]
      # print(clusters) # test
      cluster_index = new_cluster[1]
      print('Cluster Index')
      print(cluster_index) # test
      print('Clusters')
      print(clusters) # test
      # print(clusters[cluster_index]) # test
        
      # Calculating Centroid
      centroid = center(cluster_index)
       
      # Updating vector space
      new_vectors = vectors_update(vectors, cluster_index, centroid, key1, key2)
        
      # Recalculating new similarities for updated vector space
      similarities = cosine_similarities_update(similarities, new_vectors)
      # print(similarities) # test
      # print(vectors) # test
      # print('--------------') # test
      round_counter += 1

    elif key1 in clusters:
      print('If key1 in clusters')
      # Calculating similarities between keys in clusters
      count_similarities = []
      for key_a in clusters[key1]:
        i = 0
        for url in dictionary[key_a]:
          if url in dictionary[key2]:
            i += 0
        count_similarities.append(i)
      print('count_similarities')
      print(count_similarities)
      
      # Checking if >= 3 similarities between keys in clusters  
      for i in count_similarities:
        if i >= 3:
          continue
        else:
          print('Similarities < 3 for each key')
          while True:
            similarities_to_loop_and_strip = similarities
            print('Similarities in loop before strip')
            print(similarities_to_loop_and_strip)
            del similarities_to_loop_and_strip[key1][key2]
            del similarities_to_loop_and_strip[key2][key1]
            print('Similarities in loop after strip')
            print(similarities_to_loop_and_strip)
            absolute_maximum = max_similar(similarities_to_loop_and_strip)
            print('Absolute Maximum')
            print(absolute_maximum)
            if absolute_maximum >= 0.3:
              
              # Finding keys of absolute_maximum
              absolute_maximum_keys = max_keys(similarities, absolute_maximum)
              # print(absolute_maximum_keys) #test
              key1 = absolute_maximum_keys[0]
              print('key1') #test
              print(key1) #test
              key2 = absolute_maximum_keys[1]
              print('key2') #test
              print(key2) #test
       
              # Checking if keys are clusters already
              if key1 in clusters and key2 in clusters:
                print('If both in clusters')
                # Calculating similarities between keys in clusters
                count_similarities = []
                for key_a in clusters[key1]:
                  for key_b in clusters[key2]:
                    i = 0
                    for url in dictionary[key_a]:
                      if url in dictionary[key_b]:
                        i += 1
                    count_similarities.append(i)
                print('Similarities')
                print(count_similarities)
                
              # Checking if only first key is in clusters already
              elif key1 in clusters:
                print('If key1 in clusters')
                # Calculating similarities between keys in clusters
                count_similarities = []
                for key_a in clusters[key1]:
                  i = 0
                  for url in dictionary[key_a]:
                    if url in dictionary[key2]:
                        i += 1
                  count_similarities.append(i)
                print('Similarities')
                print(count_similarities)  
                  
              # Checking if only second key is in clusters already
              elif key2 in clusters:
                print('If key2 in clusters')
                # Calculating similarities between keys in clusters
                count_similarities = []
                for key_a in clusters[key2]:
                  i = 0
                  for url in dictionary[key_a]:
                    if url in dictionary[key1]:
                        i += 1
                  count_similarities.append(i)
                print('Similarities')
                print(count_similarities)
                              
              # Checking if both keys are not in clusters
              else:
                print('If both not in clusters')
                # Calculating similarities between keys in clusters
                count_similarities = []
                i = 0
                for url in dictionary[key2]:
                  if url in dictionary[key1]:
                    i += 1
                count_similarities.append(i)
                print('Similarities')
                print(count_similarities)  
            
            else:
              print('Absolute Maximum < 0.3')
              loop_must_break = True
              break            
      
            # Checking if >= 3 similarities between keys in clusters
            three_similarities = 0
            for i in count_similarities:
              if i < 3:
                break
              else:
                three_similarities += 1
            print('Three Similarities')
            print(three_similarities)
            if len(count_similarities) == three_similarities:
              print('Similarities >= 3 for each key')
              # Adding cluster
              new_cluster = add_cluster(clusters, key1, key2)
              clusters = new_cluster[0]
              print('Clusters')
              print(clusters) # test
              cluster_index = new_cluster[1]
              print('Cluster Index')
              print(cluster_index) # test
              # print(clusters[cluster_index]) # test
               
              # Calculating Centroid
              centroid = center(cluster_index)
                
              # Updating vector space
              new_vectors = vectors_update(vectors, cluster_index, centroid, key1, key2)
                
              # Recalculating new similarities for updated vector space
              similarities = cosine_similarities_update(similarities, new_vectors)
              # print(similarities) # test
              # print(vectors) # test
              # print('--------------') # test
              round_counter += 1
              loop_must_break = True
              break
            else:
              print('Similarities < 3 for each key')
          if loop_must_break == True:
            break
      
      if loop_must_break == True:
        continue
      
      print('MAX similarity OK')
      # Adding cluster
      new_cluster = add_cluster(clusters, key1, key2)
      clusters = new_cluster[0]
      # print(clusters) # test
      cluster_index = new_cluster[1]
      print('Cluster Index')
      print(cluster_index) # test
      print('Clusters')
      print(clusters) # test
      # print(clusters[cluster_index]) # test
        
      # Calculating Centroid
      centroid = center(cluster_index)
       
      # Updating vector space
      new_vectors = vectors_update(vectors, cluster_index, centroid, key1, key2)
        
      # Recalculating new similarities for updated vector space
      similarities = cosine_similarities_update(similarities, new_vectors)
      # print(similarities) # test
      # print(vectors) # test
      # print('--------------') # test
      round_counter += 1
      
    elif key2 in clusters:
      print('If key2 in clusters')
      # Calculating similarities between keys in clusters
      count_similarities = []
      for key_a in clusters[key2]:
        i = 0
        for url in dictionary[key_a]:
          if url in dictionary[key1]:
            i += 1
        count_similarities.append(i)
      print('count_similarities')
      print(count_similarities)
      
      # Checking if >= 3 similarities between keys in clusters  
      for i in count_similarities:
        if i >= 3:
          continue
        else:
          print('Similarities < 3 for each key')
          while True:
            similarities_to_loop_and_strip = similarities
            print('Similarities in loop before strip')
            print(similarities_to_loop_and_strip)
            del similarities_to_loop_and_strip[key1][key2]
            del similarities_to_loop_and_strip[key2][key1]
            print('Similarities in loop after strip')
            print(similarities_to_loop_and_strip)
            absolute_maximum = max_similar(similarities_to_loop_and_strip)
            print('Absolute Maximum')
            print(absolute_maximum)
            if absolute_maximum >= 0.3:
              
              # Finding keys of absolute_maximum
              absolute_maximum_keys = max_keys(similarities, absolute_maximum)
              # print(absolute_maximum_keys) #test
              key1 = absolute_maximum_keys[0]
              print('key1') #test
              print(key1) #test
              key2 = absolute_maximum_keys[1]
              print('key2') #test
              print(key2) #test
       
              # Checking if keys are clusters already
              if key1 in clusters and key2 in clusters:
                print('If both in clusters')
                # Calculating similarities between keys in clusters
                count_similarities = []
                for key_a in clusters[key1]:
                  for key_b in clusters[key2]:
                    i = 0
                    for url in dictionary[key_a]:
                      if url in dictionary[key_b]:
                        i += 1
                    count_similarities.append(i)
                print('Similarities')
                print(count_similarities)
                
              # Checking if only first key is in clusters already
              elif key1 in clusters:
                print('If key1 in clusters')
                # Calculating similarities between keys in clusters
                count_similarities = []
                for key_a in clusters[key1]:
                  i = 0
                  for url in dictionary[key_a]:
                    if url in dictionary[key2]:
                        i += 1
                  count_similarities.append(i)
                print('Similarities')
                print(count_similarities)  
                  
              # Checking if only second key is in clusters already
              elif key2 in clusters:
                print('If key2 in clusters')
                # Calculating similarities between keys in clusters
                count_similarities = []
                for key_a in clusters[key2]:
                  i = 0
                  for url in dictionary[key_a]:
                    if url in dictionary[key1]:
                        i += 1
                  count_similarities.append(i)
                print('Similarities')
                print(count_similarities)
                              
              # Checking if both keys are not in clusters
              else:
                print('If both not in clusters')
                # Calculating similarities between keys in clusters
                count_similarities = []
                i = 0
                for url in dictionary[key2]:
                  if url in dictionary[key1]:
                    i += 1
                count_similarities.append(i)
                print('Similarities')
                print(count_similarities)  
            
            else:
              print('Absolute Maximum < 0.3')
              loop_must_break = True
              break            
      
            # Checking if >= 3 similarities between keys in clusters
            three_similarities = 0
            for i in count_similarities:
              if i < 3:
                break
              else:
                three_similarities += 1
            print('Three Similarities')
            print(three_similarities)
            if len(count_similarities) == three_similarities:
              print('Similarities >= 3 for each key')
              # Adding cluster
              new_cluster = add_cluster(clusters, key1, key2)
              clusters = new_cluster[0]
              print('Clusters')
              print(clusters) # test
              cluster_index = new_cluster[1]
              print('Cluster Index')
              print(cluster_index) # test
              # print(clusters[cluster_index]) # test
               
              # Calculating Centroid
              centroid = center(cluster_index)
                
              # Updating vector space
              new_vectors = vectors_update(vectors, cluster_index, centroid, key1, key2)
                
              # Recalculating new similarities for updated vector space
              similarities = cosine_similarities_update(similarities, new_vectors)
              # print(similarities) # test
              # print(vectors) # test
              # print('--------------') # test
              round_counter += 1
              loop_must_break = True
              break
            else:
              print('Similarities < 3 for each key')
          if loop_must_break == True:
            break
      
      if loop_must_break == True:
        continue
      
      print('MAX similarity OK')
      # Adding cluster
      new_cluster = add_cluster(clusters, key1, key2)
      clusters = new_cluster[0]
      # print(clusters) # test
      cluster_index = new_cluster[1]
      print('Cluster Index')
      print(cluster_index) # test
      print('Clusters')
      print(clusters) # test
      # print(clusters[cluster_index]) # test
        
      # Calculating Centroid
      centroid = center(cluster_index)
       
      # Updating vector space
      new_vectors = vectors_update(vectors, cluster_index, centroid, key1, key2)
        
      # Recalculating new similarities for updated vector space
      similarities = cosine_similarities_update(similarities, new_vectors)
      # print(similarities) # test
      # print(vectors) # test
      # print('--------------') # test
      round_counter += 1
        
    else:
      print('If both not in clusters')      
      # Calculating similarities between keys in clusters
      count_similarities = []
      i = 0
      for url in dictionary[key2]:
        if url in dictionary[key1]:
          i += 1
      count_similarities.append(i)
        
      print('count_similarities')
      print(count_similarities)
        
      # Checking if >= 3 similarities between keys in clusters  
      for i in count_similarities:
        if i >= 3:
          continue
        else:
          print('Similarities < 3 for each key')
          while True:
            similarities_to_loop_and_strip = similarities
            print('Similarities in loop before strip')
            print(similarities_to_loop_and_strip)
            del similarities_to_loop_and_strip[key1][key2]
            del similarities_to_loop_and_strip[key2][key1]
            print('Similarities in loop after strip')
            print(similarities_to_loop_and_strip)
            absolute_maximum = max_similar(similarities_to_loop_and_strip)
            print('Absolute Maximum')
            print(absolute_maximum)
            if absolute_maximum >= 0.3:
              
              # Finding keys of absolute_maximum
              absolute_maximum_keys = max_keys(similarities, absolute_maximum)
              # print(absolute_maximum_keys) #test
              key1 = absolute_maximum_keys[0]
              print('key1') #test
              print(key1) #test
              key2 = absolute_maximum_keys[1]
              print('key2') #test
              print(key2) #test
       
              # Checking if keys are clusters already
              if key1 in clusters and key2 in clusters:
                print('If both in clusters')
                # Calculating similarities between keys in clusters
                count_similarities = []
                for key_a in clusters[key1]:
                  for key_b in clusters[key2]:
                    i = 0
                    for url in dictionary[key_a]:
                      if url in dictionary[key_b]:
                        i += 1
                    count_similarities.append(i)
                print('Similarities')
                print(count_similarities)
                
              # Checking if only first key is in clusters already
              elif key1 in clusters:
                print('If key1 in clusters')
                # Calculating similarities between keys in clusters
                count_similarities = []
                for key_a in clusters[key1]:
                  i = 0
                  for url in dictionary[key_a]:
                    if url in dictionary[key2]:
                        i += 1
                  count_similarities.append(i)
                print('Similarities')
                print(count_similarities)  
                  
              # Checking if only second key is in clusters already
              elif key2 in clusters:
                print('If key2 in clusters')
                # Calculating similarities between keys in clusters
                count_similarities = []
                for key_a in clusters[key2]:
                  i = 0
                  for url in dictionary[key_a]:
                    if url in dictionary[key1]:
                        i += 1
                  count_similarities.append(i)
                print('Similarities')
                print(count_similarities)
                              
              # Checking if both keys are not in clusters
              else:
                print('If both not in clusters')
                # Calculating similarities between keys in clusters
                count_similarities = []
                i = 0
                for url in dictionary[key2]:
                  if url in dictionary[key1]:
                    i += 1
                count_similarities.append(i)
                print('Similarities')
                print(count_similarities)  
            
            else:
              print('Absolute Maximum < 0.3')
              loop_must_break = True
              break            
      
            # Checking if >= 3 similarities between keys in clusters
            three_similarities = 0
            for i in count_similarities:
              if i < 3:
                break
              else:
                three_similarities += 1
            print('Three Similarities')
            print(three_similarities)
            if len(count_similarities) == three_similarities:
              print('Similarities >= 3 for each key')
              # Adding cluster
              new_cluster = add_cluster(clusters, key1, key2)
              clusters = new_cluster[0]
              print('Clusters')
              print(clusters) # test
              cluster_index = new_cluster[1]
              print('Cluster Index')
              print(cluster_index) # test
              # print(clusters[cluster_index]) # test
               
              # Calculating Centroid
              centroid = center(cluster_index)
                
              # Updating vector space
              new_vectors = vectors_update(vectors, cluster_index, centroid, key1, key2)
                
              # Recalculating new similarities for updated vector space
              similarities = cosine_similarities_update(similarities, new_vectors)
              # print(similarities) # test
              # print(vectors) # test
              # print('--------------') # test
              round_counter += 1
              loop_must_break = True
              break
            else:
              print('Similarities < 3 for each key')
          if loop_must_break == True:
            break
      
      if loop_must_break == True:
        continue
      
      print('MAX similarity OK')
      # Adding cluster
      new_cluster = add_cluster(clusters, key1, key2)
      clusters = new_cluster[0]
      # print(clusters) # test
      cluster_index = new_cluster[1]
      print('Cluster Index')
      print(cluster_index) # test
      print('Clusters')
      print(clusters) # test
      # print(clusters[cluster_index]) # test
        
      # Calculating Centroid
      centroid = center(cluster_index)
       
      # Updating vector space
      new_vectors = vectors_update(vectors, cluster_index, centroid, key1, key2)
        
      # Recalculating new similarities for updated vector space
      similarities = cosine_similarities_update(similarities, new_vectors)
      # print(similarities) # test
      # print(vectors) # test
      # print('--------------') # test
      round_counter += 1
  else:
    print('Clustering Done!')
    break
# print(clusters) # test
    
'''-----'''
# Writing results to new list in Excel
'''-----'''

# Creating new dictionary that will combine ini_dictionary and clusters
cluster_dictionary = {}
for cluster in clusters:
  keys_dictionary = {}
  for key in clusters[cluster]:
    keys_dictionary.update({key : ini_dictionary[key]})
  cluster_dictionary.update({cluster : keys_dictionary})
print(cluster_dictionary)

# Creating dictionary of unclustered queries
clustered_queries_nested = list(clusters.values())
clustered_queries = []
# print(clustered_queries_nested) # test
for i in clustered_queries_nested:
  for query in i:
    clustered_queries.append(query)
# print(clustered_queries) # test
unclustered_dictionary = {query : top for query, top in ini_dictionary.items() if query not in clustered_queries and query not in outliers}
# print('--------------') # test
# print(unclustered_dictionary.keys()) # test

# Creating dictionary of outliers
outliers_dictionary = {query : top for query, top in ini_dictionary.items() if query in outliers}
# print('--------------') # test
# print(outliers_dictionary.keys()) # test

# Writing clusters from cluster_dictionary as dataframes into excel
row = 0
writer = pandas.ExcelWriter('D:\\Keyword Clustering\\Clusters_Yandex.xlsx', engine = 'xlsxwriter')

for cluster in cluster_dictionary:
  # print(volume_dict) # test
  # print(cluster_dictionary[cluster]) # test
  cluster_vol_dict = {}
  for i in cluster_dictionary[cluster]:
    cluster_vol_dict[i] =  volume_dict[i] + cluster_dictionary[cluster][i]
  # print(cluster_vol_dict)
  # print('--------------')
  df = pandas.DataFrame.from_dict(cluster_vol_dict)
  df = df.transpose()
  # print(df) # test
  df = df.sort_values(by=[5], ascending=False)
  #print(len(cluster_dictionary[cluster].values())) # test
  df.to_excel(writer, index_label = str(len(cluster_dictionary[cluster].values())), sheet_name = 'Сlusters', startrow = row , startcol = 0, header = ['WS','"!WS"','r"!WS"','Adwords','Ahrefs','"!WS" + Ahrefs','Difficulty','1','1','1','0.85','0.6','0.5','0.5','0.3','0.3','0.2'])
  row += len(cluster_vol_dict) + 2
  # print(row) # test
  
# Writing unclustered
cluster_vol_dict = {}
for i in unclustered_dictionary:
  cluster_vol_dict[i] =  volume_dict[i] + unclustered_dictionary[i]
df = pandas.DataFrame.from_dict(cluster_vol_dict)
df = df.transpose()
df = df.sort_values(by=[5], ascending=False)
df.to_excel(writer, index_label = 'Unclustered' + str(len(unclustered_dictionary.values())), sheet_name = 'Сlusters', startrow = row , startcol = 0, header = ['WS','"!WS"','r"!WS"','Adwords','Ahrefs','"!WS" + Ahrefs','Difficulty','1','1','1','0.85','0.6','0.5','0.5','0.3','0.3','0.2'])
row += len(unclustered_dictionary.values()) + 2

# Writing outliers
cluster_vol_dict = {}
for i in outliers_dictionary:
  cluster_vol_dict[i] =  volume_dict[i] + outliers_dictionary[i]
df = df.sort_values(by=[5], ascending=False)
df = pandas.DataFrame.from_dict(cluster_vol_dict)
df = df.transpose()
df = df.sort_values(by=[5], ascending=False)
df.to_excel(writer, index_label = 'Outlier' + str(len(outliers_dictionary.values())), sheet_name = 'Сlusters', startrow = row , startcol = 0, header = ['WS','"!WS"','r"!WS"','Adwords','Ahrefs','"!WS" + Ahrefs','Difficulty','1','1','1','0.85','0.6','0.5','0.5','0.3','0.3','0.2'])
row += len(outliers_dictionary.values()) + 2

# Writing similarities
df = pandas.DataFrame.from_dict(similarities)
df.to_excel(writer, sheet_name = 'Сlusters', startrow = row , startcol = 0)

writer.save()

print('--------------')
print('Done!')

