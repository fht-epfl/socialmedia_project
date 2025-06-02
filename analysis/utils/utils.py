import pandas as pd
from langdetect import detect
from nltk.stem import WordNetLemmatizer


def compare_languages(df_mastodon, df_reddit):

    s1 = df_mastodon.languages.apply(lambda x: ', '.join(x) if isinstance(x, list) else str(x)).value_counts()
    s2 = df_reddit.languages.apply(str).value_counts()

    # Convert to formatted strings like "'en' : 234"
    formatted_1 = [f"'{lang}' : {count}" for lang, count in s1.items()]
    formatted_2 = [f"'{lang}' : {count}" for lang, count in s2.items()]

    # Pad shorter lists with empty strings
    max_len = max(len(formatted_1), len(formatted_2))
    formatted_1 += [''] * (max_len - len(formatted_1))
    formatted_2 += [''] * (max_len - len(formatted_2))

    # Create DataFrame
    df_display = pd.DataFrame({
        'mastodon': formatted_1,
        'reddit': formatted_2
    })

    return df_display


def is_english(text):
    try:
        return detect(text) == 'en'
    except:
        return False 
    

def contains_strict_words(text):
    contains_no = True if 'no' in text else False
    contains_do_not = True if ['do', 'not'] in text else False
    return contains_no or contains_do_not


def lemmatize(x): 
    if isinstance(x, list):
        return [WordNetLemmatizer().lemmatize(word) for word in x]  
    else:
        return x
    
    
def create_document(row):
    if isinstance(row["text"], list) and isinstance(row["hint"], list):
        return row["text"] + row["hint"]
    return row["text"]