import pandas as pd
import ast

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