#%%
import praw
import pandas as pd
import time
reddit = praw.Reddit(
    client_id='1kk02sMYFXThMwBy-ozi8Q',
    client_secret='nQHzk9LRkF-JCa2y7Em6PkYcQzsfpg',
    user_agent='mastodon_reddit_compare_script',
    username='Adorable-Row-1331',
    password='EPFLsocialmedia',
)

# # 获取前 100 个热门 subreddit
# top_subreddits = reddit.subreddits.popular(limit=100)
# subreddit_names = [sub.display_name for sub in top_subreddits]

# 打印 subreddit 名称和订阅者数量
# for subreddit in top_subreddits:
#     print(f"{subreddit.display_name} - {subreddit.subscribers} subscribers")

#%%
# 示例 subreddits，可替换为你需要的列表

# 手动添加一些已知的 NSFW 或 Quarantine 子版块进行测试
subreddits_to_check = ['NSFW', 'porn', 'sex', 'Conspiracy', 'anime_titties', 'WTF', 'MensRights', 'PoliticalHumor', 'Coronavirus', 'NSFW_GIF', 'NSFW_Snapchat']

data = []

for name in subreddits_to_check:
    try:
        sub = reddit.subreddit(name)

        # 获取 subreddit 的相关字段
        subreddit_data = {
            'name': sub.display_name,
            'title': sub.title,
            'description': sub.public_description,
            'language': sub.lang,  # 可能为空
            'subscribers': sub.subscribers,
            'active_user_count': sub.accounts_active,  # 近似活跃用户（非准确 MAU）
            'over18': sub.over18,
            'quarantine': sub.quarantine,
            'is_restricted': sub.subreddit_type != 'public',
            'moderators_count': len(list(sub.moderator())),
            'rules': '; '.join([rule.short_name for rule in sub.rules])
        }

        data.append(subreddit_data)
        time.sleep(1)  # 避免过快请求
    except Exception as e:
        print(f"Error processing subreddit {name}: {e}")

# 转为 DataFrame 并保存
df = pd.DataFrame(data)
df.to_csv('reddit_subreddits_data.csv', index=False)
print("Saved reddit_subreddits_data.csv")


