import cv2
import pytesseract
import Levenshtein
import pandas as pd
import pytesseract
from tqdm import tqdm_notebook
import os
import re
import sys
from datetime import date, datetime
import time
from dateutil.parser import parse
#from tesserocr import PyTessBaseAPI,PSM,Image

month_strings = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December', 'Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec', 'JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']

def closest_month(word):
    df = pd.DataFrame({'month': month_strings})
    df['dist'] = df['month'].apply(lambda month: Levenshtein.distance(word, month))
    idxmin = df['dist'].idxmin()
    return (idxmin+1, df.loc[idxmin, 'dist'])

# print(closest_month('Cet'))

def find_dates(df_complete):
    # With spaces
    mask_year = df_complete['text'].str.match(r'^\d{4}$')
    df_dates = df_complete[mask_year]
    df_dates = df_dates.assign(month=0, day=0)
    # print(df_dates.index.values)
    for idx in df_dates.index.values:
        df_months = df_complete.loc[idx-2:idx-1].copy()
        # print(df_months)
        if idx-2 not in df_complete.index.values:
            continue
        if idx-1 not in df_complete.index.values:
            continue
        df_months['month'] = df_months['text'].apply(lambda x: closest_month(x)[0])
        df_months['distance'] = df_months['text'].apply(lambda x: closest_month(x)[1])
        # print(df_months)
        df_months = df_months[df_months['distance'] <= 2]
        # print(df_months)
        if not df_months.empty:
            idx_month = df_months['distance'].idxmin()
            # print(idx_month)
            month = df_months.loc[idx_month, 'month']
            while(month > 12):
                df_months.loc[idx_month, 'month'] = month-12
                month = df_months.loc[idx_month, 'month']
            # print(df_months['month'])
            df_dates.loc[idx, 'month'] = df_months.loc[idx_month, 'month']
            idx_day = [idx-2, idx-1]
            idx_day.remove(idx_month)
            idx_day = idx_day[0]
            match_digits = re.search(r'\d+', df_complete.loc[idx_day, 'text'])
            # print(match_digits)
            #Todo - clean up the digits
            if match_digits is not None:
                df_dates.loc[idx, 'day'] = match_digits.group()
    df_dates = df_dates[df_dates['month'] > 0]

    # without spaces
    # Todo calculate the distance
    # date_string = ['\d{2}[./-]\d{2}[./-]\d{2}', '\d{2}[./-]\d{2}[./-]\d{4}', '\d{6}', '\d{8}']
    date_string = ['(0[1-9]|1[012])[./-](0[1-9]|[12][0-9]|3[01])[./-]\d\d', '(0[1-9]|1[012])[./-](0[1-9]|[12][0-9]|3[01])[./-]\d\d\d\d', '(0[1-9]|[12][0-9]|3[01])[./-](0[1-9]|1[012])[./-]\d\d', '(0[1-9]|[12][0-9]|3[01])[./-](0[1-9]|1[012])[./-]\d\d\d\d', '\d\d\d\d[./-](0[1-9]|[12][0-9]|3[01])[./-](0[1-9]|1[012])', '(0[1-9]|1[012])(0[1-9]|[12][0-9]|3[01])\d\d', '(0[1-9]|1[012])(0[1-9]|[12][0-9]|3[01])\d\d\d\d', '(0[1-9]|[12][0-9]|3[01])(0[1-9]|1[012])\d\d', '(0[1-9]|[12][0-9]|3[01])(0[1-9]|1[012])\d\d\d\d', '\d\d\d\d[./-](0[1-9]|[12][0-9]|3[01])[./-](0[1-9]|1[012])']
    date_mmddyy = None
    for d in date_string:
        date_mmddyy = df_complete['text'].str.match(d)
        df_dates_mmddyy = df_complete[date_mmddyy]
        df_dates_mmddyy = df_dates_mmddyy.assign(month=0,day=0)
        df_dates = pd.concat([df_dates_mmddyy,df_dates])
        df_dates.drop_duplicates(inplace=True)

    # calculating 10APR14 dates
    # date_match = df_complete['text'].str.match(d)
    for i,j in df_complete.iterrows():
        if(re.match(r"^\d\d[a-zA-Z]{3}\d\d$",str(j["text"])) or re.match(r"^\d\d[a-zA-Z]{3}\d{4}$",str(j["text"]))):
            day = str(j["text"])[:2]
            month_name = str(j["text"])[2:5]
            month = 0
            mon=0
            minDist=sys.maxsize
            while mon < len(month_strings):
                dist = Levenshtein.distance(month_name, month_strings[mon])
                if(minDist > dist):
                    minDist = dist
                    month = mon
                mon += 1
            # print(month_strings[month])
            month += 1
            while month>12:
                month = month-12
            year = str(j["text"])[5:]
            lst = ['0','0','0','0','0','0','0','0','0','0','0',year,str(month),day]
            lst_series = pd.Series(lst, index=df_dates.columns)
            df_dates = df_dates.append(lst_series, ignore_index=True)

    return df_dates

def cal_bestbefore(df_complete):
    months=0
    for a,b in df_complete.iterrows():
        if(Levenshtein.ratio(str(b['text']), "Best")>=0.9):
            col_names = ["text"]
            best_before_df = pd.DataFrame(columns=col_names)
            best_before_df.text = df_complete.loc[a+1:a+3].text.copy()
            isbestBefore=False
            # months = 0
            for i,j in best_before_df.iterrows():
                if(Levenshtein.ratio(str(j['text']), "Before")>=0.9 or Levenshtein.ratio(str(j['text']), "By")>=0.9):
                    isbestBefore = True
                if(isbestBefore):
                    if(str(j["text"]).isdigit()):
                        months = int(j["text"])
    return months

def givetext(path):
    image=cv2.imread(path)
    # text = pytesseract.image_to_data(image, lang='eng')
    text=pytesseract.image_to_data(image, config='--psm 6 -l Transit_FT_500')
    return text

def compare_dates(a,b):
    date2 = parse(b)
    if(a>date2):
        return a
    else:
        return date2


def imagedetection(path):
    text_table = givetext(path)
    with open("text.tsv", "wt") as tsv_file:
        tsv_file.write(text_table)
    df = pd.read_csv("text.tsv", sep=r'\t', dtype={'text': str}, engine='python')
    df = df[df.conf>-1]  # remove empty words
    df.dropna(subset=['text'], inplace=True)
    list=[None,None,0]
    exp_date = None
    mfg_date = None
    bestbefore =0
    if df.empty:
        return list
    else:
        dates_found = find_dates(df)
        dates_found.drop(['level','page_num','block_num','par_num','line_num','word_num','left','top','width','height','conf'], axis = 1, inplace=True)
        if(dates_found.size>0):
            for i,j in dates_found.iterrows():
                if(int(j["day"])>0):
                    dates_found.at[i,"text"]=str(j["day"])+"/"+str(j["month"])+"/"+str(j["text"])
                    dates_found.at[i,"day"]=0
                    dates_found.at[i,"month"]=0
                elif(int(j["month"])>0):
                    dates_found.at[i,"text"]=str(j["month"])+"/"+str(j["text"])
                    dates_found.at[i,"month"]=0
            # print(dates_found)
            date_list = dates_found["text"].tolist()
            # print(date_list)
            max_date = parse(date_list[0])
            date_list.pop(0)
            for i in date_list:
                max_date = compare_dates(max_date,i)
            print(max_date)
            bestbefore=cal_bestbefore(df)
            present_date = datetime.now()
            print(present_date)
            if(max_date>present_date):
                exp_date = max_date
                for i in date_list:
                    if(parse(i)>present_date):
                        date_list.remove(i)
                max_date=parse(date_list[0])
                date_list.pop(0)
                for i in date_list:
                    max_date = compare_dates(max_date,i)
                mfg_date = max_date
            else:
                if(len(date_list)>=2 and bestbefore==0):
                    exp_date=max_date
                    for i in date_list:
                        if (parse(i) > present_date):
                            date_list.remove(i)
                    max_date = parse(date_list[0])
                    date_list.pop(0)
                    for i in date_list:
                        max_date = compare_dates(max_date, i)
                    mfg_date = max_date
                else:
                    mfg_date = max_date
        format_str = '%Y-%m-%d %H:%M:%S'
        if mfg_date != None:
            mfg_date = datetime.strptime(str(mfg_date), format_str).date()
        if exp_date != None:
            exp_date = datetime.strptime(str(exp_date), format_str).date()
        elif bestbefore != 0:
            exp_date = mfg_date + timedelta(days=bestbefore)
        list=[mfg_date,exp_date,1]
        print(list)
        return list
