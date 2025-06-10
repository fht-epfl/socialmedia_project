# Analyzing the Impact of Moderation Policies on User Activity in Decentralized Social Networks

## Objective
This study aims to investigate how different moderation policies on Mastodon servers influence user activity and engagement. 

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
The main results are shown in

## Repository's structure:

**TODO: update the structure to its final state and add comments**

```
decentralized-social-media
.
├── NLP_analysis_rules.ipynb
├── README.md
├── data_preprocesser.py
├── dataset
│   ├── Mastodon
│   │   ├── complete_data.csv
│   │   ├── eda.ipynb
│   │   ├── mastodon_instance_info.csv
│   │   └── test.py
│   └── Reddit
│       ├── Reddit_subreddits_analysis.ipynb
│       ├── reddit.py
│       ├── reddit_subreddits_data_NSFW.csv
│       └── reddit_subreddits_data_top100.csv
└── results.ipynb
```

## Milestone:
M1: project pitch - Week 5: Fri 21.03.2025
M2: project progress presentation - Week 11: Fri 02.05.2025
M3: final project presentation -  Fri 06.06.2025
M4: final project - Tue 10.06.2025
