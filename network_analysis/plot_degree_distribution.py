"""
Plot degree distribution histograms and save outputs.

Generates:
 - degree_hist_linear.png   (linear bins histogram)
"""

import os
import pandas as pd
import matplotlib.pyplot as plt


def load_degree_df(cohort_dir):
    path = os.path.join(cohort_dir, 'degree_centrality_nodes.csv')
    return pd.read_csv(path)

def plot_linear_hist(degrees, out_png):
    plt.figure(figsize=(8, 5))
    plt.hist(degrees, bins=50, color='#3182bd', edgecolor='black', alpha=0.8)
    plt.xlabel('Degree')
    plt.ylabel('Count')
    plt.title('Degree distribution (linear bins)')
    plt.tight_layout()
    plt.savefig(out_png, dpi=200)
    plt.close()

def main():
    cohort = os.environ.get('COHORT_NAME', 'elderly_75plus')
    script_dir = os.path.dirname(os.path.abspath(__file__))
    cohort_dir = os.path.join(script_dir, cohort)
    os.makedirs(cohort_dir, exist_ok=True)
    df = load_degree_df(cohort_dir)
    degrees = df['degree'].astype(int)
    plot_linear_hist(degrees, os.path.join(cohort_dir, 'degree_hist_linear.png'))
    print('Saved linear histogram to:', os.path.join(cohort_dir, 'degree_hist_linear.png'))

if __name__ == '__main__':
    main()
