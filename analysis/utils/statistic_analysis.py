import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from sklearn.metrics import r2_score
from scipy.stats import pearsonr, spearmanr, norm, zscore

import shap
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split



def plot_distribution(data,xlabel,ylabel,title,bin):
    plt.figure(figsize=(8, 6))
    plt.hist(data, bins=bin, edgecolor='black', align='left')
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.show()

    return

def plot_scatter(x,y,xlabel,ylabel,title):
    coefficients = np.polyfit(x, y, 1)  # 二次多项式
    poly_eq = np.poly1d(coefficients)
    y_fit = poly_eq(x)

    r_squared = r2_score(y, y_fit)

    plt.figure(figsize=(8, 6))
    plt.scatter(x, y, label='Data points', s=5)
    # 排序绘制拟合曲线（防止线段乱跳）
    sorted_indices = np.argsort(x)
    x_sorted = x.to_numpy()[sorted_indices]
    y_fit_sorted = y_fit[sorted_indices]

    plt.plot(x_sorted, y_fit_sorted, color='red', label=f'Quadratic Fit')

    # 标签和标题
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(title)
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


import numpy as np
from scipy.stats import pearsonr, spearmanr, norm


def fisher_z_test(A1, B1, A2, B2, method='spearman'):
    """
    Compare whether the correlation between A and B is significantly different
    in two datasets using the Fisher z-test.

    Parameters:
        A1, B1: Variables from dataset 1 (array-like)
        A2, B2: Variables from dataset 2 (array-like)
        method: Correlation method, either 'pearson' or 'spearman'

    Returns:
        dict containing:
            - r1, r2: Correlation coefficients in each dataset
            - z_score: Fisher z statistic
            - p_value: Two-tailed p-value
    """
    # Choose correlation method
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
    """
    Run SHAP analysis to interpret how selected features affect the target variable.

    Parameters:
        df (DataFrame): input dataset
        feature_cols (list of str): list of feature column names, e.g., ['A', 'B']
        target_col (str): name of the target variable, e.g., 'C'
        plot_interaction (bool): whether to compute and show SHAP interaction values
        interaction_pair (tuple): specify a pair of features to plot interaction, e.g., ('A', 'B')

    Output:
        SHAP summary plot, and optionally interaction plots
    """
    # 1. Prepare data
    X = zscore(df[feature_cols])
    y = zscore(df[target_col])

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
            shap.dependence_plot(feat1, interaction_values, X_test, interaction_index=feat2)

