"""
Build disease co-occurrence network from patient condition records.
Nodes = diseases, Edges = co-occurrence in same patient (weighted by frequency).
Filters edges with weight < 2 to focus on meaningful comorbidity patterns.
"""
import pandas as pd
import networkx as nx
import os
import random
import pickle
from itertools import combinations
from collections import defaultdict

# Load data
COHORT_NAME = os.environ.get('COHORT_NAME', 'elderly_75plus')
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
os.makedirs(os.path.join(SCRIPT_DIR, COHORT_NAME), exist_ok=True)

df_path = os.path.join(PROJECT_ROOT, f'output_{COHORT_NAME}', f'{COHORT_NAME}_conditions_with_names.csv')
df = pd.read_csv(df_path, low_memory=False)
df = df[df['concept_name'].notna()].copy()

# Create patient-disease relationships
patient_diseases = df.groupby('person_id')['condition_concept_id'].apply(set).to_dict()
disease_names = df[['condition_concept_id', 'concept_name']].drop_duplicates()
disease_name_map = dict(zip(disease_names['condition_concept_id'], disease_names['concept_name']))

# Calculate disease co-occurrences
cooccurrence = defaultdict(int)
total_pairs = 0

for patient_id, diseases in patient_diseases.items():
    if len(diseases) < 2:
        continue
    for disease1, disease2 in combinations(sorted(diseases), 2):
        cooccurrence[(disease1, disease2)] += 1
        total_pairs += 1

print(f"Unique disease pairs: {len(cooccurrence):,}")
print(f"Total co-occurrences: {total_pairs:,}")

# Build network graph
G = nx.Graph()

for disease_id, disease_name in disease_name_map.items():
    G.add_node(disease_id, name=disease_name)

for (disease1, disease2), weight in cooccurrence.items():
    if weight >= 2:
        G.add_edge(disease1, disease2, weight=weight)

print(f"Network Statistics:")
print(f"Nodes: {G.number_of_nodes()}")
print(f"Edges: {G.number_of_edges()}")

# Get main component and compute metrics
largest_cc = max(nx.connected_components(G), key=len)
G_main = G.subgraph(largest_cc).copy()
print(f"Main component: {G_main.number_of_nodes()} nodes, {G_main.number_of_edges()} edges")

print(f"Average degree: {sum(dict(G_main.degree()).values()) / G_main.number_of_nodes():.2f}")

degree_centrality = nx.degree_centrality(G_main)
top_hubs = sorted(degree_centrality.items(), key=lambda x: x[1], reverse=True)[:10]

print(f"Top 10 Hub Diseases:")
for disease_id, centrality in top_hubs:
    disease_name = disease_name_map[disease_id]
    degree = G_main.degree(disease_id)
    print(f"  {disease_name[:60]:60s} | Deg: {degree:4d} | Cent: {centrality:.4f}")

print(f"  {disease_name[:60]:60s} | Deg: {degree:4d} | Cent: {centrality:.4f}")

# Save network files
print("\nSaving outputs...")
OUTPUT_DIR = os.path.join(SCRIPT_DIR, COHORT_NAME)

with open(os.path.join(OUTPUT_DIR, 'disease_network_full.pkl'), 'wb') as f:
    pickle.dump(G, f)

with open(os.path.join(OUTPUT_DIR, 'disease_network_main.pkl'), 'wb') as f:
    pickle.dump(G_main, f)

nx.write_graphml(G_main, os.path.join(OUTPUT_DIR, 'disease_network_main.graphml'))

edge_list = []
for u, v, data in G_main.edges(data=True):
    edge_list.append({
        'disease1_id': u,
        'disease1_name': disease_name_map[u],
        'disease2_id': v,
        'disease2_name': disease_name_map[v],
        'weight': data['weight']
    })

edge_df = pd.DataFrame(edge_list).sort_values('weight', ascending=False)
edge_df.to_csv(os.path.join(OUTPUT_DIR, 'disease_cooccurrence_edges.csv'), index=False)

node_list = []
for node in G_main.nodes():
    node_list.append({
        'disease_id': node,
        'disease_name': disease_name_map[node],
        'degree': G_main.degree(node),
        'degree_centrality': degree_centrality[node]
    })

node_df = pd.DataFrame(node_list).sort_values('degree', ascending=False)
node_df.to_csv(os.path.join(OUTPUT_DIR, 'disease_network_nodes.csv'), index=False)

print()
print(f"Files saved to: network_analysis/{COHORT_NAME}/")

if __name__ == '__main__':
    pass  # Script runs on import for this project
