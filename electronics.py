# -*- coding: utf-8 -*-
"""Electronics.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1ppGWQZl_kQMqSkiHa9syz0sYfR3Jn_oM
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.cluster import KMeans
from sklearn import neighbors
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler

df = pd.read_csv("/content/drive/MyDrive/Capgemini/electronics.csv")
df.head()

df.shape

df.info()

df.isnull().sum()

df['brand'].unique()

df.drop(['user_attr'],axis = 'columns' ,inplace=True)

df["brand"].fillna( method ='ffill', inplace = True)

df.info()

df.corr()

sns.countplot(x ='rating', data = df)
plt.show()

rating_count = pd.DataFrame(df.groupby('item_id')['rating'].count())
df1 = rating_count.sort_values('rating', ascending=False).head(10)
df1

"""#These are the top 10 highest rated items."""

ax = df1.plot.bar(stacked=True)

"""#Recommendation based on Brand """

most_items = df.groupby('brand')['item_id'].count().reset_index().sort_values('item_id', ascending=False).head(10).set_index('brand')
plt.figure(figsize=(15,10))
ax = sns.barplot(most_items['item_id'], most_items.index, palette='inferno')
ax.set_title("Top 10 most rated Brands")
ax.set_xlabel("Total number of items")
totals = []
for i in ax.patches:
    totals.append(i.get_width())
total = sum(totals)
for i in ax.patches:
    ax.text(i.get_width()+.2, i.get_y()+.2,str(round(i.get_width())), fontsize=15,color='black')

"""#Recommendations based on correlations"""

average_rating = pd.DataFrame(df.groupby('item_id')['rating'].mean())
average_rating['ratingCount'] = pd.DataFrame(df.groupby('item_id')['rating'].count())
df2 = average_rating.sort_values('ratingCount',ascending=False).head(10)
df2

ax = df2.plot.bar(stacked=True)

"""# Category based Recommendation"""

most_items1 = df.groupby('category')['item_id'].count().reset_index().sort_values('item_id', ascending=False).head(10).set_index('category')
plt.figure(figsize=(15,10))
ax = sns.barplot(most_items1['item_id'], most_items1.index, palette='inferno')
ax.set_title("Top 10 most rated Category")
ax.set_xlabel("Total number of items")
totals = []
for i in ax.patches:
    totals.append(i.get_width())
total = sum(totals)
for i in ax.patches:
    ax.text(i.get_width()+.2, i.get_y()+.2,str(round(i.get_width())), fontsize=15,color='black')

combine_item_rating = df.copy()
columns = ['timestamp', 'model_attr','brand', 'year', 'split']
combine_item_rating = combine_item_rating.drop(columns, axis=1)
combine_item_rating.head(10)

combine_item_rating = combine_item_rating.dropna(axis = 0, subset = ['category'])

item_ratingCount = (combine_item_rating.groupby(by = ['category'])['rating'].count().reset_index().rename(columns = {'rating': 'totalRatingCount'})[['category', 'totalRatingCount']])
item_ratingCount.head(10)

rating_with_totalRatingCount = combine_item_rating.merge(item_ratingCount, left_on = 'category', right_on = 'category', how = 'left')
rating_with_totalRatingCount.head()

df3 = rating_with_totalRatingCount.join(df, lsuffix="DROP").filter(regex="^(?!.*DROP)")
df3.head()

df3.info()

"""#Recommendation Using **Nearst Neighbors**"""

from scipy.sparse import csr_matrix
from sklearn.neighbors import NearestNeighbors
user_rating = df3.drop_duplicates(['user_id','category'])
user_rating_pivot = user_rating.pivot(index = 'category', columns = 'user_id', values = 'rating').fillna(0)
user_rating_matrix = csr_matrix(user_rating_pivot.values)

model_knn = NearestNeighbors(metric = 'cosine', algorithm = 'brute')
model_knn.fit(user_rating_matrix)

query_index = np.random.choice(user_rating_pivot.shape[0])
print(query_index)
distances, indices = model_knn.kneighbors(user_rating_pivot.iloc[query_index,:].values.reshape(1, -1), n_neighbors = 5)

user_rating_pivot.index[query_index]

for i in range(0, len(distances.flatten())):
    if i == 0:
        print('Recommendations for {0}:\n'.format(user_rating_pivot.index[query_index]))
    else:
        print('{0}: {1}, with distance of {2}:'.format(i, user_rating_pivot.index[indices.flatten()[i]], distances.flatten()[i]))