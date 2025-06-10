import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from sklearn.metrics import r2_score
from scipy.stats import pearsonr, spearmanr, norm, zscore,kendalltau,ttest_ind

import shap
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from tqdm import tqdm



def plot_distribution(data,xlabel,ylabel,title,bin):
    plt.figure(figsize=(8, 6))
    plt.hist(data, bins=bin, edgecolor='black', align='left')
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.show()

    return

def plot_scatter(x,y,xlabel,ylabel,title,cluster=None):
    coefficients = np.polyfit(x, y, 1)  # 二次多项式
    poly_eq = np.poly1d(coefficients)
    y_fit = poly_eq(x)

    r_squared = r2_score(y, y_fit)

    if cluster is not None:
        unique_clusters = np.unique(cluster)
        for c in unique_clusters:
            mask = (cluster == c)
            plt.scatter(x[mask], y[mask], label=f'Cluster {c}', s=8)
    else:
        plt.scatter(x, y, label='Data points', s=8)
    # 排序绘制拟合曲线（防止线段乱跳）

    if cluster is None:
        sorted_indices = np.argsort(x)
        x_sorted = x.to_numpy()[sorted_indices]
        y_fit_sorted = y_fit[sorted_indices]

        plt.plot(x_sorted, y_fit_sorted, color='red', label=f'Quadratic Fit')

    # 标签和标题
    plt.xlabel(xlabel,size=18)
    plt.ylabel(ylabel,size=18)
    plt.title(title,size=18)
    plt.legend()
    plt.show()
    print(f"r2={r_squared}")

    return

def pearsonr_correlation(x,y):
    corr, p_value = pearsonr(x, y)
    print(f"Pearson correlation coefficient: {corr}")
    print(f"P-value: {p_value}")
    return

def spearmanr_correlation(x,y):
    corr, p_value = spearmanr(x, y)
    print(f"Spearmanr correlation coefficient: {corr}")
    print(f"P-value: {p_value}")
    return

def kendalltau_correlation(x,y):
    corr, p_value = kendalltau(x, y)
    print(f"Kendall-tau correlation coefficient: {corr}")
    print(f"P-value: {p_value}")
    return





def fisher_z_test(A1, B1, A2, B2, method='spearman'):

    if method == 'pearson':
        r1, _ = pearsonr(A1, B1)
        r2, _ = pearsonr(A2, B2)
    elif method == 'spearman':
        r1, _ = spearmanr(A1, B1)
        r2, _ = spearmanr(A2, B2)
    else:
        raise ValueError("method must be 'pearson' or 'spearman'")

    # Fisher r-to-z transformation (clip to avoid ±1 leading to infinity)
    def fisher_z(r):
        r = np.clip(r, -0.999999, 0.999999)
        return 0.5 * np.log((1 + r) / (1 - r))

    z1 = fisher_z(r1)
    z2 = fisher_z(r2)

    n1 = len(A1)
    n2 = len(A2)
    se = np.sqrt(1 / (n1 - 3) + 1 / (n2 - 3))  # Standard error of difference

    z_score = (z1 - z2) / se
    p_value = 2 * (1 - norm.cdf(abs(z_score)))  # Two-tailed p-value

    print(f"r1 = {r1:.3f}, r2 = {r2:.3f}")
    print(f"z = {z_score:.3f}, p = {p_value:.4f}")

    return


def shap_analysis(df, feature_cols, target_col, plot_interaction=True, interaction_pair=None):

    X_raw = df[feature_cols]
    y_raw = df[target_col]

    X = pd.DataFrame(zscore(X_raw), columns=feature_cols, index=X_raw.index)
    y = pd.Series(zscore(y_raw), name=target_col, index=y_raw.index)

    # 2. Train model
    X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=42)
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    # 3. Explain with SHAP
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X_test)

    # 4. SHAP summary plot
    print("🔍 SHAP Summary Plot (feature importance):")
    shap.summary_plot(shap_values, X_test)

    # 5. Optional: SHAP interaction
    if plot_interaction:
        print("🔍 SHAP Interaction Summary Plot:")
        interaction_values = explainer.shap_interaction_values(X_test)
        shap.summary_plot(interaction_values, X_test)

        if interaction_pair:
            feat1, feat2 = interaction_pair
            print(f"🔍 SHAP Dependence Plot for interaction: {feat1} × {feat2}")
            shap.dependence_plot(feat1, shap_values, X_test, interaction_index=feat2)


def run_t_test(sample1, sample2, equal_var=False):

    t_stat, p_value = ttest_ind(sample1, sample2, equal_var=equal_var)
    significant = p_value < 0.05

    print(f"t = {t_stat:.3f}, p = {p_value:.4f} → {'显著差异' if significant else '无显著差异'}")
    return


def bootstrap_spearman_diff(x1, y1, x2, y2, n_iter=10000, random_state=42):
    rng = np.random.default_rng(random_state)
    n1 = len(x1)
    n2 = len(x2)

    diffs = []

    for _ in tqdm(range(n_iter)):
        # 重抽样（有放回）
        idx1 = rng.choice(n1, size=n1, replace=True)
        idx2 = rng.choice(n2, size=n2, replace=True)

        r1, _ = spearmanr(x1[idx1], y1[idx1])
        r2, _ = spearmanr(x2[idx2], y2[idx2])
        diffs.append(r1 - r2)

    diffs = np.array(diffs)

    # 原始相关系数差
    r1_obs, _ = spearmanr(x1, y1)
    r2_obs, _ = spearmanr(x2, y2)
    diff_obs = r1_obs - r2_obs

    # 计算双尾 p 值
    p_value = np.mean(np.abs(diffs) >= np.abs(diff_obs))

    # 输出结果
    print(f"Observed Spearman r1: {r1_obs:.4f}")
    print(f"Observed Spearman r2: {r2_obs:.4f}")
    print(f"Observed difference: {diff_obs:.4f}")
    print(f"Bootstrap p-value: {p_value:.4f}")

    return


def bootstrap_kendall_diff(x1, y1, x2, y2, n_iter=10000, random_state=42):

    rng = np.random.default_rng(random_state)
    n1 = len(x1)
    n2 = len(x2)

    diffs = []

    for _ in tqdm(range(n_iter), desc="Bootstrapping"):
        # 重采样
        idx1 = rng.choice(n1, size=n1, replace=True)
        idx2 = rng.choice(n2, size=n2, replace=True)

        tau1, _ = kendalltau(x1[idx1], y1[idx1])
        tau2, _ = kendalltau(x2[idx2], y2[idx2])
        diffs.append(tau1 - tau2)

    diffs = np.array(diffs)

    # 原始差值
    tau1_obs, _ = kendalltau(x1, y1)
    tau2_obs, _ = kendalltau(x2, y2)
    diff_obs = tau1_obs - tau2_obs

    # 双尾 p 值
    p_value = np.mean(np.abs(diffs) >= np.abs(diff_obs))

    # 打印结果
    print(f"Observed Kendall tau1: {tau1_obs:.4f}")
    print(f"Observed Kendall tau2: {tau2_obs:.4f}")
    print(f"Observed difference: {diff_obs:.4f}")
    print(f"Bootstrap p-value: {p_value:.4f}")

    return
