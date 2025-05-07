import pandas as pd
import ast

# Data loading
def load_instances_data(cols_to_keep_mastodon = ["domain", "title", "source_url", "description", 
                              "active_month", "languages", "rules", "top_5_trends", 
                              "total_users", "total_posts", "blacklist"],
              cols_to_keep_reddit = ["name", "title", "description", "language",
                                     "subscribers", "active_user_count", "over18",
                                     "quarantine", "is_restricted", "moderators_count", "rules"]):
    """
    Load the data from the CSV file and return a DataFrame with selected columns.
    Args:
        cols_to_keep (list, optional): List of columns to keep from the CSV files. Defaults to all.
    """
    df_mas_1 = pd.read_csv("../dataset/Mastodon/mastodon_instance_info.csv", usecols=cols_to_keep_mastodon)
    df_mas_2 = pd.read_csv("../dataset/Mastodon/complete_data.csv", usecols=cols_to_keep_mastodon)
    df_reddit = pd.read_csv("../dataset/Reddit/reddit_subreddits_data_top100.csv", usecols=cols_to_keep_reddit)
    
    return df_mas_1, df_mas_2, df_reddit


# Data cleaning
class DataCleaner:
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()

    def clean(self) -> pd.DataFrame:
        for column in self.df.columns:
            method_name = f"_clean_{column}"
            if hasattr(self, method_name):
                print(f"Cleaning column: {column}")
                method = getattr(self, method_name)
                self.df[column] = method(self.df[column])
        return self.df

    # ===== Mastodon & Reddit shared/specific column cleaners =====

    def _clean_rules(self, series: pd.Series) -> pd.Series:
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
        return series.apply(parse_rules)

    def _clean_languages(self, series: pd.Series) -> pd.Series:
        def safe_parse(x):
            try:
                return ast.literal_eval(x) if isinstance(x, str) else []
            except Exception:
                return []
        return series.fillna("[]").apply(safe_parse)

    def _clean_description(self, series: pd.Series) -> pd.Series:
        return series.apply(lambda x: x if isinstance(x, str) else str(x))

    def _clean_blacklist(self, series: pd.Series) -> pd.Series:
        # TODO: implement cleaning for blacklist (here is an example, commented)
        # Count number of blacklisted items if stored as list-like strings
        # def safe_count(x):
        #     try:
        #         return len(ast.literal_eval(x)) if isinstance(x, str) else 0
        #     except Exception:
        #         return 0
        return series.fillna("[]") #.apply(safe_count)

    def _clean_total_users(self, series: pd.Series) -> pd.Series:
        return pd.to_numeric(series, errors='coerce').fillna(0).astype(int)

    def _clean_total_posts(self, series: pd.Series) -> pd.Series:
        return pd.to_numeric(series, errors='coerce').fillna(0).astype(int)

    def _clean_subscribers(self, series: pd.Series) -> pd.Series:
        return pd.to_numeric(series, errors='coerce').fillna(0).astype(int)

    def _clean_active_user_count(self, series: pd.Series) -> pd.Series:
        return pd.to_numeric(series, errors='coerce').fillna(0).astype(int)

    def _clean_over18(self, series: pd.Series) -> pd.Series:
        return series.fillna(False).astype(bool)

    def _clean_quarantine(self, series: pd.Series) -> pd.Series:
        return series.fillna(False).astype(bool)

    def _clean_is_restricted(self, series: pd.Series) -> pd.Series:
        return series.fillna(False).astype(bool)

    def _clean_moderators_count(self, series: pd.Series) -> pd.Series:
        return pd.to_numeric(series, errors='coerce').fillna(0).astype(int)

# Example usage:
# ```
# cleaner = DataCleaner(df)
# cleaned_df = cleaner.clean()
# ````
# OR
# ````
# cleaned_df = DataCleaner(df).clean()
# ````