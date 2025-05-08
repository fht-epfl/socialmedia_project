import pandas as pd


class RulesProcessor:
    def __init__(self, df):
        self.df = df
        self.rules_df = None

    def extract_rules(self):
        rules = self.df[['rules']].explode('rules').reset_index(drop=False)
        rules = rules.rename(columns={"index": "server_id"})
        rules = rules.dropna()
        rules = pd.concat([rules.drop(['rules'], axis=1), rules['rules'].apply(pd.Series)], axis=1)
        rules = rules.rename(columns={'id': "rule_id"})
        self.rules_df = rules
        return self.rules_df

    def standardize_rules(self):
        if self.rules_df is None:
            raise ValueError("You must run extract_rules() before standardizing.")
        self.rules_df["text"] = self._standardize_text(self.rules_df["text"])
        self.rules_df["hint"] = self._standardize_text(self.rules_df["hint"])
        return self.rules_df

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
    
    def compute_strictness(self):
        def contains_strict_words(text):
            contains_no = True if 'no' in text else False
            contains_do_not = True if ['do', 'not'] in text else False
            return contains_no or contains_do_not
        def contains_soft_words(text):
            return None

# Example usage:
# processor = RulesProcessor(df)
# rules_df = processor.extract_rules()
# standardized_df = processor.standardize_rules()
