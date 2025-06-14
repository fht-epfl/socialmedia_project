# Analyzing the Impact of Moderation Policies on User Activity in Decentralized Social Networks

## Objective
This study quantitatively examines the relationship between moderation policies and user engagement on decentralized (Mastodon) and centralized (Reddit) social media platforms. We propose a novel metric for moderation stringency based on linguistic analysis of rules. Using datasets comprising moderation policies and user activity metrics, we find Mastodon instances to generally have stricter moderation compared to Reddit subreddits. Topic modeling further reveals distinct moderation themes between platforms. Correlation analysis indicates that moderation strictness positively associates with user engagement, particularly through moderator-related metrics (e.g., number of blacklisted users, moderators). These insights highlight platform-specific dynamics, informing moderation practices in decentralized online communities.

## Research Questions
1. How strict are Mastodon and Reddit on their moderation?
2. What are the different topic clusters among Mastodon and Reddit, and how do they compare?
3. How does the strictness of a server/subreddit associate with the user engagement in Mastodon and Reddit?

## Methodology
1. Data Collection
* User Activity Data (via /api/v2/instance): active users month.
* Moderation Policies (via /api/v2/instance): content restrictions, federation blocking lists.
* Federation Relationships (via /api/v1/instance/domain_blocks): network openness and isolation levels.
2. Data Analysis
* Stringency Score: We define a stringency score based on the lexicon to represent the strictness (word intensity) of moderation rules, and analyze the differences across the two platform
* Topic Modeling: We perform BERTopic modelling in both rules and server level, in order to analyze what are the different topic clusters among Mastodon and Reddit
* Correlation Analysis: Using spearman correlation to analyze the correlation between user engagement and moderation metrics (e.g number of rules, stringency scores)



## Note:
The main results are presented in analysis/statistic_analysis.ipynb and analysis/NLP_analysis_rules.ipynb, with detailed functions available in analysis/utils.

- Stringency Score Analysis & Topic Modeling Analysis: analysis/NLP_analysis_rules.ipynb
- Correlation Analysis: analysis/statistic_analysis.ipynb

## Repository's structure:

**TODO: update the structure to its final state and add comments**

```
│  .gitignore
│  README.md
│  requirements.txt
│  
├─analysis
│  │  lgbtq_safe_servers.csv
│  │  mastodon_clusters_descr.csv
│  │  mastodon_server_strictness.csv
│  │  NLP_analysis_rules.ipynb                                                 # Results of Stringency Analysis and Topic Clustering Analysis
│  │  reddit_clusters_descr.csv
│  │  reddit_server_strictness.csv
│  │  statistic_analysis.ipynb                                                 # Results of Correlation Analysis
│  │  
│  └─utils                                                                     # Detailed Functions
│      │  rule_num_stringency_ma.png
│      │  SocialMediaDataset.py
│      │  SocialMediaDataset_Sa.py
│      │  statistic_analysis.py
│      │  strictness_lexicon.json
│      │  utils.py
│      │  
│      └─__pycache__
│              rules_extractor.cpython-312.pyc
│              SocialMediaDataset.cpython-312.pyc
│              SocialMediaDataset_Sa.cpython-312.pyc
│              statistic_analysis.cpython-312.pyc
│              utils.cpython-312.pyc
│              
├─dataset
│  ├─Mastodon
│  │      complete_data.csv
│  │      eda.ipynb
│  │      mastodon_instance_info.csv                                            # Mastodon Dataset
│  │      test.py                                                               # Code to call Mastodon API
│  │      
│  └─Reddit
│          reddit.py
│          Reddit_subreddits_analysis.ipynb
│          reddit_subreddits_data_NSFW.csv                                      # Reddit Dataset
│          reddit_subreddits_data_top100.csv
```

