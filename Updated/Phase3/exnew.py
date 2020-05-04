import spacy
import pandas as pd
import Levenshtein as lev

def predict_exp(prod):
      nlp = spacy.load("en_core_web_lg")  # make sure to use larger model!
      df = pd.read_csv('Expiration_Dataset - Sheet1.csv', delimiter=',')
      df.Proudct_Name=df.Proudct_Name.astype(str)
      column_names = ["Proudct_Name1", "Proudct_Name2", "similarity"]
      df1 = pd.DataFrame(columns=column_names)
      unique_prodNames = pd.unique(df["Proudct_Name"])
      unique_words = prod.split(" ")
      maxval=0
      max=""
      for st in unique_prodNames:
          Ratio = lev.ratio(prod.lower(), st.lower())
          if Ratio > maxval:
              maxval=Ratio
              max=st
      print(max,maxval)
      if max!="" and maxval>0.8:
         df.where(df["Proudct_Name"]==max, inplace=True)
         duration = df["Duration (in days)"].mean(axis=0)
         return duration
      else:
          unique_prodNames = ' '.join(unique_prodNames)
          tokens = nlp(unique_prodNames)
          prod = nlp(prod)
          cols = ['Proudct_Name1', 'Proudct_Name2', 'similarity']
          df1 = pd.DataFrame(columns=cols)
          for token1 in tokens:
              for token2 in prod:
                  lst_series = pd.Series([token2.text, token1.text, token1.similarity(token2)], index=df1.columns)
                  df1 = df1.append(lst_series, ignore_index=True)

          df1.where(df1["similarity"] >= 0.40, inplace=True)
          column_names = ["result"]
          df4 = pd.DataFrame(columns=column_names)
          df4.result = df1.where(df1["Proudct_Name1"] == unique_words[0]).Proudct_Name2
          # print(df4)
          intersect = pd.unique(df4.result)
          #unique_words.pop(0)
          for st in unique_words:
              df4.result = df1.where(df1["Proudct_Name1"] == st).Proudct_Name2
              # print(df4)
              intersect = set(intersect).intersection(set(pd.unique(df4["result"])))
          del list(intersect)[0]
          print(intersect)
          if len(intersect) > 0:
              df3 = df[df['Proudct_Name'].isin(intersect)]
          else:
              print("No Intersection!")
              df3 = df[df['Proudct_Name'].isin(df1)]  # union
          print(df3)
          return df3.mean(axis=0).iloc[0]
