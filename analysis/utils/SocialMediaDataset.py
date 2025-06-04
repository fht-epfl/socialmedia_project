import pandas as pd
import ast

from langdetect import detect
from transformers.pipelines import pipeline
lang_recognition = pipeline("text-classification", model="spolivin/lang-recogn-model")
        


class SocialMediaDataset:
    """Superclass for handling social media datasets, specifically Mastodon and Reddit.
    This class provides methods to load and preprocess the data, focusing on common columns
    between the two platforms.
    Attributes:
        df (pd.DataFrame): DataFrame containing social media data.
        col_equiv_mas_to_red (dict): Dictionary mapping Mastodon column names to Reddit equivalents.
        col_equiv_red_to_mas (dict): Dictionary mapping Reddit column names to Mastodon equivalents.
        col_in_common (list): List of columns that are common between Mastodon and Reddit.
    """
    @staticmethod
    def load_instance(data_path: str, cols_to_keep: list) -> pd.DataFrame:
        df = pd.read_csv(data_path, usecols=cols_to_keep)
        return df  
    
    def __init__(self, data_path: str, cols_to_keep: list) -> None:

        self.df = self.load_instance(data_path, cols_to_keep)
        self.col_equiv_mas_and_red = {"domain": "domain", 
                                    "title": "title", 
                                    "description": "description",
                                    "languages": "languages", 
                                    "total_users": "total_users", 
                                    "active_month": "active_month", 
                                    "rules": "rules",
                                    "name": "domain", 
                                    "language": "languages", 
                                    "subscribers": "total_users", 
                                    "active_user_count": "active_month"}
        self.cleaned = False

        self.df_en = None
        self.rules_df = None
        self.std_rules_df = None

    
    
    #####################################################
    ################### Data cleaning ###################
    #####################################################
    

    def clean(self) -> None:
        if not self.cleaned:
            self._format_col_names()
            print("\nStarting data cleaning process... 🧹🧼")
            for column in self.df.columns:
                method_name = f"_clean_{column}"
                if hasattr(self, method_name):
                    print(f"Cleaning column: {column}")
                    method = getattr(self, method_name)
                    self.df[column] = method()
            self.cleaned = True
        print("Data is all clean and shiny! ✨🫧")
        
    def _format_col_names(self) -> None:
        self.df.rename(columns=self.col_equiv_mas_and_red, inplace=True)
       
    def _clean_description(self) -> pd.Series:
        return self.df["description"].apply(lambda x: x if isinstance(x, str) else str(x))
       
    def _clean_total_users(self) -> pd.Series:
        return pd.to_numeric(self.df["total_users"], errors='coerce').fillna(0).astype(int)
    
    def _clean_active_month(self) -> pd.Series:
        return pd.to_numeric(self.df["active_month"], errors='coerce').fillna(0).astype(int)
    



    @staticmethod
    def _remove_empty(x):
        if isinstance(x, list) and len(x) > 0:
            return [item for item in x if item != '']
        return x
    
    def _standardize_text(self, df_column):
        df_column = df_column.apply(lambda x: x.strip() if isinstance(x, str) else x)
        df_column = df_column.str.lower()
        df_column = df_column.str.replace(r"[^a-zA-Z0-9\s]", " ", regex=True)
        df_column = df_column.str.replace(r"\s+", " ", regex=True).str.strip()
        df_column = df_column.str.split(" ")
        df_column = df_column.apply(self._remove_empty)
        return df_column  
    
    def take_english_servers_only(self) -> pd.DataFrame:
        self.df_en = self.df[self.df["languages"].apply(self.is_english_server)]
        return self.df_en
    
    def is_english_server(self, lang, en_symbol="en"): 
        if en_symbol == "en":
            print("Taking the default 'en' as English language symbol.")
        return lang == "en" if isinstance(lang, type(en_symbol)) else False
    
    @staticmethod
    def detect_english(text):
        try:
            
            return lang_recognition(text)[0]["label"] == 'English'
        except:
            return False 
    
    ###################################################
    ########### Rules strictness evlauation ###########
    ###################################################
    
    def compute_strictness(self):
        # TODO: Implement strictness computation
        def contains_strict_words(text):
            contains_no = True if 'no' in text else False
            contains_do_not = True if ['do', 'not'] in text else False
            return contains_no or contains_do_not
        def contains_soft_words(text):
            return None



class MastodonDataset(SocialMediaDataset):
    def __init__(self, 
                 mast_path="../dataset/Mastodon/complete_data.csv",
                 cols_to_keep_mastodon = ["domain", # common with reddit
                                          "title", # common with reddit
                                          "description", # common with reddit
                                          "languages", # common with reddit
                                          "total_users", # common with reddit
                                          "active_month", # common with reddit
                                          "rules", # common with reddit
                                          "top_5_trends", 
                                          "total_posts", 
                                          "blacklist", 
                                          "source_url"],
                 keep_common_col_only = True) -> None:
        self.col_in_common = ["domain", 
                        "title", 
                        "description", 
                        "languages",
                        "total_users", 
                        "active_month", 
                        "rules"]
        if keep_common_col_only:
            cols_to_keep_mastodon = self.col_in_common
        super().__init__(mast_path, cols_to_keep_mastodon)
        self.col_mast_specific = ["top_5_trends", 
                                  "total_posts", 
                                  "blacklist", 
                                  "source_url"]
    
    def _clean_rules(self) -> pd.Series:
        @staticmethod
        def parse_rules(x):
            if pd.isna(x):
                return []
            try:
                parsed = ast.literal_eval(x)
                if isinstance(parsed, list) and all(isinstance(item, dict) for item in parsed):
                    return parsed
                return []
            except Exception:
                return []
        return self.df["rules"].apply(parse_rules)

    def _clean_languages(self) -> pd.Series:
        def parse_list_lang(x):
            try:
                return ast.literal_eval(x) if isinstance(x, str) else []
            except Exception:
                return []
        return self.df["languages"].fillna("[]").apply(parse_list_lang)
 
# TODO: test efficiency of this cleaning for top_5_trends   
    def _clean_top_5_trends(self) -> pd.Series:
        @staticmethod
        def parse_trends(x):
            if pd.isna(x):
                return []
            try:
                parsed = ast.literal_eval(x)
                if isinstance(parsed, list) and all(isinstance(ast.literal_eval(item), int) for item in parsed):
                    return parsed
                return []
            except Exception:
                return []
        return self.df["top_5_trends"].apply(parse_trends)

    def _clean_total_posts(self) -> pd.Series:
        return pd.to_numeric(self.df["total_posts"], errors='coerce').fillna(0).astype(int)

    def _clean_blacklist(self) -> pd.Series:
        # TODO: implement better cleaning for blacklist (here is an example, commented)
        # Count number of blacklisted items if stored as list-like strings
        # def safe_count(x):
        #     try:
        #         return len(ast.literal_eval(x)) if isinstance(x, str) else 0
        #     except Exception:
        #         return 0
        return self.df['blacklist'].apply(lambda x: len(str(x).split("|")) if x else 0) #.apply(safe_count)

# TODO: implement more precise cleaning for source_url
    def _clean_source_url(self) -> pd.Series:
        return self.df["source_url"].fillna("").astype(str)




    #######################################################
    ################# Extraction of rules #################
    #######################################################
    
    def extract_rules(self) -> pd.DataFrame:
        if self.df_en is None:
            rules = self.df[['rules']].explode('rules').reset_index(drop=False)
        else:
            rules = self.df_en[['rules']].explode('rules').reset_index(drop=False)
        rules = rules.rename(columns={"index": "server_id"})
        rules = rules.dropna()
        rules = pd.concat([rules.drop(['rules'], axis=1), rules['rules'].apply(pd.Series)], axis=1)
        rules = rules.rename(columns={'id': "rule_id"})
        self.rules_df = rules
        return self.rules_df  

    @staticmethod
    def create_document(row):
        if isinstance(row["text"], list) and isinstance(row["hint"], list):
            return row["text"] + row["hint"]
        return row["text"]

    def standardize_rules(self) -> pd.DataFrame:
        if self.rules_df is None:
            raise ValueError("You must run self.extract_rules() before standardizing.")
        self.std_rules_df =  self.rules_df.copy()
        self.std_rules_df["text"] = self._standardize_text(self.std_rules_df["text"])
        self.std_rules_df["hint"] = self._standardize_text(self.std_rules_df["hint"])
        self.std_rules_df["rules"] = self.std_rules_df.apply(self.create_document, axis=1)
        return self.std_rules_df

    
    def predicts_english_rules(self) -> pd.DataFrame:
        if self.rules_df is None:
            raise ValueError("You must run extract_rules() before filtering English rules.")
        else:
            doc = self.rules_df.apply(lambda row: row["text"] + " " + row["hint"] if isinstance(row["text"], list) and isinstance(row["hint"], list) else row["text"], axis=1)
            english_rules_prediction = doc.apply(self.detect_english)
            self.rules_df["is_english_pred"] = english_rules_prediction
        return self.rules_df
    
    def keep_english_rules_only(self) -> pd.DataFrame:
        if self.rules_df is None:
            raise ValueError("You must run extract_rules() before filtering English rules.")
        if self.rules_df["is_english_pred"].isnull().any():
            raise ValueError("You must run predicts_english_rules() before filtering English rules.")
        english_pred_rate = self.rules_df.groupby("server_id")[["server_id", "is_english_pred"]].apply(lambda server: server["is_english_pred"].sum() / server["server_id"].count()).reset_index(name='is_english_pred_rate')
        print(f"Started with {self.rules_df.shape[0]} rules…")
        
        mastodon_rules_english = self.rules_df[self.rules_df["server_id"].isin(english_pred_rate[english_pred_rate["is_english_pred_rate"] > 0]["server_id"])]
        print(f"Removed {self.rules_df.shape[0] - mastodon_rules_english.shape[0]} rules from servers with 0% of rules predicted to be in english…")
        
        mastodon_rules_english_93 = mastodon_rules_english[(mastodon_rules_english["server_id"] != 93) | (mastodon_rules_english["is_english_pred"] == True)]
        print(f"Removed {mastodon_rules_english.shape[0] - mastodon_rules_english_93.shape[0]} rules from server 93 that were not predicted to be in english…")
        
        non_english_rules_pourcentage = 100 * (self.rules_df.shape[0] - mastodon_rules_english.shape[0]) / self.rules_df.shape[0]
        print(f"In total, we removed {self.rules_df.shape[0] - mastodon_rules_english_93.shape[0]} of the {self.rules_df.shape[0]} rules ({non_english_rules_pourcentage:.0f}%) that were not detected to be in english.")
        print(f"Final total number of english rules: {mastodon_rules_english_93.shape[0]}")
        
        self.rules_df = mastodon_rules_english_93.reset_index(drop=True)
        return self.rules_df




class RedditDataset(SocialMediaDataset):
    def __init__(self, 
                 redd_path="../dataset/Reddit/reddit_subreddits_data_top100.csv", 
                 cols_to_keep_reddit=["name", # common with mastodon
                                      "title", # common with mastodon
                                      "description", # common with mastodon
                                      "language",# common with mastodon
                                      "subscribers", # common with mastodon
                                      "active_user_count",# common with mastodon
                                      "rules",# common with mastodon
                                      "over18",
                                      "quarantine", 
                                      "is_restricted", 
                                      "moderators_count"],
                 keep_common_col_only = True) -> None:
        self.col_in_common = ["name", 
                        "title", 
                        "description", 
                        "language",
                        "subscribers", 
                        "active_user_count", 
                        "rules"]
        if keep_common_col_only:
            cols_to_keep_reddit = self.col_in_common
        super().__init__(redd_path, cols_to_keep_reddit)
        self.col_redd_specific = ["over18",
                                  "quarantine", 
                                  "is_restricted", 
                                  "moderators_count"]

    def _clean_languages(self) -> pd.Series:
        return self.df["languages"].fillna("").astype(str)

    def _clean_rules(self) -> pd.Series:
        return self.df["rules"].apply(lambda x : x.split(";") if isinstance(x, str) else [])
    
    def _clean_over18(self) -> pd.Series:
        return self.df["over18"].fillna(False).astype(bool)

    def _clean_quarantine(self) -> pd.Series:
        return self.df["quarantine"].fillna(False).astype(bool)

    def _clean_is_restricted(self) -> pd.Series:
        return self.df["is_restricted"].fillna(False).astype(bool)

    def _clean_moderators_count(self) -> pd.Series:

        return pd.to_numeric(self.df["moderators_count"], errors='coerce').fillna(0).astype(int)

    
    def is_english_server(self, lang, en_symbol="en"): 
        return lang == en_symbol if isinstance(lang, str) else False

    def predicts_english_rules(self) -> pd.DataFrame:
        if self.rules_df is None:
            raise ValueError("You must run extract_rules() before filtering English rules.")
        else:
            english_rules_prediction = self.rules_df["rules"].apply(self.detect_english)
            self.rules_df["is_english_pred"] = english_rules_prediction
        return self.rules_df
    
    
    #######################################################
    ################# Extraction of rules #################
    #######################################################
    
    def extract_rules(self) -> pd.DataFrame:
        rules_df = self.df['rules'].explode().reset_index(drop=False)
        rules_df = rules_df.rename(columns={"index": "server_id"})
        # We add an index to the rules
        rules_df["rule_id"] = rules_df.groupby("server_id").cumcount()
        rules_df = rules_df.dropna()
        self.rules_df = rules_df[["server_id", "rule_id", "rules"]].reset_index(drop=True)
        return self.rules_df
    
    def standardize_rules(self):
        if self.rules_df is None:
            raise ValueError("You must run extract_rules() before standardizing.")
        self.std_rules_df = self.rules_df.copy()
        self.std_rules_df["rules"] = self._standardize_text(self.std_rules_df["rules"])
        return self.std_rules_df
    
    def keep_english_rules_only(self) -> pd.DataFrame:
        raise NotImplementedError("This method is not implemented for RedditDataset. Use predicts_english_rules() to filter English rules.")
        # if self.rules_df is None:
        #     raise ValueError("You must run extract_rules() before filtering English rules.")
        # if self.rules_df["is_english_pred"].isnull().any():
        #     raise ValueError("You must run predicts_english_rules() before filtering English rules.")
        # english_pred_rate = self.rules_df.groupby("server_id")[["server_id", "is_english_pred"]].apply(lambda server: server["is_english_pred"].sum() / server["server_id"].count()).reset_index(name='is_english_pred_rate')
        # mastodon_rules_english = self.rules_df[self.rules_df["server_id"].isin(english_pred_rate[english_pred_rate["is_english_pred_rate"] > 0]["server_id"])]
        # mastodon_rules_english = mastodon_rules_english[(mastodon_rules_english["server_id"] != 93) | (mastodon_rules_english["is_english_pred"] == True)]
        # self.rules_df = mastodon_rules_english.reset_index(drop=True)
        # return self.rules_df

