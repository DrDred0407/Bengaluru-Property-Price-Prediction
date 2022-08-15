# -*- coding: utf-8 -*-
"""Bengaluru hpp.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1ue_xmJ6gzJYhTGPPT1ivq62XAaPoS2rS

# In this project we will predict prices of houses in Bengaluru.

## Importing useful Libraries
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

"""### Importing the Housing Datasheet"""

data = pd.read_csv('Bengaluru_House_Data.csv')
data.shape

data.info()

"""Since price of the house does not depend on the name of society we can actually drop that feature from our data."""

data_new = data.drop(labels='society' , axis=1)
data_new

plt.figure(figsize=(10,10))
data_new.area_type.value_counts().plot(kind='pie')

data_new.location.value_counts()

data_new.bath.value_counts()

data_new.balcony.value_counts()

plt.figure(figsize=(10,10))
data_new.availability.value_counts().plot.pie()

pd.crosstab(data_new.bath , data_new.balcony).plot.bar(figsize=(10,10) , ylabel='Frequency')

pd.crosstab(data_new.area_type , data_new.balcony).plot.bar(figsize=(8,8))

"""## Since we have missing values in some of our features, we have to resolve them."""

data_new.bath = data_new.bath.fillna(data.bath.median())
data_new.balcony = data_new.balcony.fillna(data.balcony.median())

data_new.isna().sum()

"""### Since remaining missing data points are very small as compared to the total datapoints so we can actually remove those rows,
### it will not cause an effective difference in the data.
"""

data_new = data_new.dropna()
data_new.isna().sum()

# Converting the size column to bhk
# data['bhk'] = data['size'].apply(lambda x: int(x.split(' ')[0]))
# data = data.drop('size', axis='columns')
# data.groupby('bhk')['bhk'].agg('count')

data_new.total_sqft.unique()

# here we have range values so we will filter them out
def isFloat(x):
    try:
        float(x)
    except:
        return False
    return True

data_new[~data_new['total_sqft'].apply(isFloat)]

def convert_sqft_to_num(x):
  val = x.split('-')
  if len(val)==2:
    return (float(val[0])+float(val[1]))/2
  try:
    return float(x)
  except:
    return None

data_new['new_total_sqft'] = data_new.total_sqft.apply(convert_sqft_to_num)
data_new = data_new.drop('total_sqft' , axis='columns')
data_new.head()

#  Since we have returned with certain none values we will try to remove them
data_new.new_total_sqft.isna().sum()

# we have 46 none values 
data_new = data_new.dropna()

# again checking for none values
data_new.new_total_sqft.isna().sum()

# we will once agin check for any null values in our modified data
data_new.isna().sum()

"""### Feature Engineering

While comparing the prices we must have a comparable price and for that we will use price per sqft instead of price.
"""

# Adding a new column price_per_sqft

data_new1 = data_new.copy()
data_new1['price_per_sqft'] = data_new1['price']*100000/data_new1['new_total_sqft']
data_new1.head()

# here we have multiplied 100000 because the price given is in lakhs.

len(data_new1.location.unique())

data_new1.location = data_new1.location.apply(lambda x: x.strip())
lvc = data_new1.location.value_counts()
lvc

data_new1.location = data_new1.location.apply(lambda x: x.strip())
len(lvc[lvc<=10]), len(data_new1.location.unique())

# labelling the locations with less then or equal to 10 occurences to 'other'
locations_less_than_10 = lvc[lvc<=10]

data_new1.location = data_new1.location.apply(lambda x: 'other' if x in locations_less_than_10 else x)
len(data_new1.location.unique())

# checking the unique values in 'availability column'
# data_new1.groupby('availability')['availability'].agg('count').sort_values(ascending=False)
avc = data_new1.availability.value_counts()
avc

# labelling the dates into not ready
dates = data_new1.groupby('availability')['availability'].agg('count').sort_values(ascending=False)

dates_not_ready = dates[dates<10000]
data_new1.availability = data_new1.availability.apply(lambda x: 'Not Ready' if x in dates_not_ready else x)

len(data_new1.availability.unique())

# Checking the unique values in 'area_type' column
data_new1.groupby('area_type')['area_type'].agg('count').sort_values(ascending=False)

# Since the column has only few unique values, we don't perform any operation

# Converting the size column to bhk
data_new1['bhk'] = data_new1['size'].apply(lambda x: int(x.split(' ')[0]))
data_new1 = data_new1.drop('size', axis='columns')
data_new1.groupby('bhk')['bhk'].agg('count')

"""## Removing outliers"""

data_new2 = data_new1[~(data_new1.new_total_sqft/data_new1.bhk<300)]
len(data_new2) , len(data_new1)

data_new2.price_per_sqft.describe()

"""Here we can see that price_per_sqft has a very wide range ranging from 267.8298 to 176470.588.
So we will try to remove such extreme points.
"""

plt.scatter(data_new2.price_per_sqft , data_new2.bhk)
plt.show()

plt.plot(data_new2.price_per_sqft , data_new2.location)
plt.show()

def remove_pps_outliers(data_new2):
  data_out = pd.DataFrame()

  for key, sub_data in data_new2.groupby('location'):
    mean = np.mean(sub_data.price_per_sqft)
    std_dev = np.std(sub_data.price_per_sqft)
    reduce_data = sub_data[(sub_data.price_per_sqft>(mean-std_dev)) & (sub_data.price_per_sqft<(mean+std_dev))]
    data_out = pd.concat([data_out, reduce_data], ignore_index=True)
  return data_out

data_new3 = remove_pps_outliers(data_new2)
len(data_new2) , len(data_new3)

def plot_scatter_chart(data , location):
  bhk2 = data_new1[(data_new1.location== location) & (data_new1.bhk == 2)]
  bhk3 = data_new1[(data_new1.location== location) & (data_new1.bhk == 3)]
  plt.figure(figsize=(15,10))
  plt.scatter(bhk2.new_total_sqft, bhk2.price, color='blue', label='2 BHK', s=50)
  plt.scatter(bhk3.new_total_sqft, bhk3.price, color='green', marker='+', label='3 BHK', s=50)
  plt.xlabel('Total Square feet Area')
  plt.ylabel('Price(in lakhs)')
  plt.title('location')
  plt.legend()
  # print(bhk2)
  # print(bhk3)

plot_scatter_chart(data_new3 , 'Whitefield')

plt.hist(data_new3.price_per_sqft , rwidth=0.5)
plt.show()

plt.hist(data_new3.bath, rwidth=0.5)
plt.show()

"""## Model Building"""

# removing the columns that were added just for preparation of our data
data_new4 = data_new3.drop('price_per_sqft', axis='columns')

data_new4

dummy_cols = pd.get_dummies(data_new4.location).drop('other', axis='columns')
data_new4 = pd.concat([data_new4,dummy_cols], axis='columns')

dummy_cols = pd.get_dummies(data_new4.availability).drop('Not Ready', axis='columns')
data_new4 = pd.concat([data_new4,dummy_cols], axis='columns')

dummy_cols = pd.get_dummies(data_new4.area_type).drop('Super built-up  Area', axis='columns')
data_new4 = pd.concat([data_new4,dummy_cols], axis='columns')

data_new5 = data_new4.drop(['area_type','availability','location'], axis='columns')
data_new5.head()

# Splitting the dataset into features and label
X = data_new5.drop('price', axis='columns')
y = data_new5['price']

from sklearn.model_selection import train_test_split
x_test,x_train,y_test,y_train = train_test_split(X,y)

from sklearn.model_selection import GridSearchCV
from sklearn.model_selection import ShuffleSplit
from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.metrics import r2_score, mean_squared_error, accuracy_score

lin_reg = LinearRegression()
lin_reg.fit(x_train,y_train)

y_pred_1 = lin_reg.predict(x_test)

r2_score(y_test,y_pred_1)

dtr = DecisionTreeRegressor()
dtr.fit(x_train,y_train)

y_pred_2 = dtr.predict(x_test)

r2_score(y_test,y_pred_2)

def find_best_model(X,y):
    models = {
        'linear_regression': {
            'model': LinearRegression(),
            'parameters': {
                'normalize': [True,False]
            }
        },
        
        # 'lasso': {
        #     'model': Lasso(),
        #     'parameters': {
        #         'alpha': [1,2],
        #         'selection': ['random', 'cyclic']
        #     }
        # },
        
        'decision_tree': {
            'model': DecisionTreeRegressor(),
            'parameters': {
                'criterion': ['mse', 'friedman_mse'],
                'splitter': ['best', 'random']
            }
        }
    }
    
    scores = []
    cv_X_y = ShuffleSplit(n_splits=5, test_size=0.20, random_state=0)
    
    for model_name, model_params in models.items():
        gs = GridSearchCV(model_params['model'], model_params['parameters'], cv=cv_X_y, return_train_score=False)
        gs.fit(X,y)
        scores.append({
            'model': model_name,
            'best_parameters': gs.best_params_,
            'accuracy': gs.best_score_
        })
        
    return pd.DataFrame(scores, columns=['model', 'best_parameters', 'accuracy'])

find_best_model(X, y)

"""# **We are getting a good accuracy value for linear regression whereas Decision tree model's accuracy value falls short of Linear Regression.**"""

pd.DataFrame({'Coefficients':lin_reg.coef_})

lin_reg.intercept_

