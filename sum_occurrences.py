import pandas as pd

df = pd.read_csv('output/disease_prevalence_elderly.csv')
print(f'Total occurrences: {df["num_occurrences"].sum():,}')
print(f'Total unique patients affected: {df["num_patients"].sum():,}')
