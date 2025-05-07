# Analyzing the Impact of Moderation Policies on User Activity in Decentralized Social Networks

## Objective
This study aims to investigate how different moderation policies on Mastodon servers influence user activity and engagement. By analyzing server-level federation relationships, moderation rules, and user behavior, we seek to understand which policies contribute to a more active and healthy online community and which may have negative effects.

## Research Questions
1. How do different moderation policies correlate with user activity levels (e.g., number of users)?
2. Does server federation openness (e.g., number of blocked/allowed servers) impact user engagement?
3. Are strict moderation rules associated with increased or decreased user retention?
4. What policy patterns emerge among the most active and least active servers?

## Methodology
1. Data Collection
* User Activity Data (via /api/v2/instance): active users month.
* Moderation Policies (via /api/v2/instance): content restrictions, federation blocking lists.
* Federation Relationships (via /api/v1/instance/domain_blocks): network openness and isolation levels.
2. Data Analysis
* Correlation Analysis: Compare moderation strictness vs. user engagement.
* Network Analysis: Study server-to-server federation structures.
* Regression Models: Predict the impact of policies on user retention.
* Cluster Analysis: Identify groups of servers with similar policies and activity patterns.
3. Expected Outcomes
* Insights into which policies encourage or discourage engagement.
* Identification of federation openness as a factor in community health.
* A framework to help server admins optimize moderation strategies.

## Note:
For example, we can have the user activity (the new register users of month, how many active users on the server) and moderation policy
Both are high-level data, so we can get rid of the profiling issue Victor mentioned.
Then for the analysis of how users in different servers form their own public sphere we can see
1. the number of monthly active user VS the strictness of the moderation policy
2.  the number of monthly active user VS the number of servers this server blocked 
3. the number of moderation policy VS the number of servers this server blocked
….
Many can be analyzed

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
