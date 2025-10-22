"""
Step 1: Build Disease-Disease Co-occurrence Network

This script:
1. Loads elderly patient conditions
2. Creates disease co-occurrence matrix (diseases that appear in same patients)
3. Builds weighted network where:
   - Nodes = Diseases
   - Edges = Co-occurrence (weight = number of patients with both diseases)
4. Saves network in multiple formats for analysis
"""

import pandas as pd
import numpy as np
import networkx as nx
from itertools import combinations
from collections import defaultdict
import pickle

print("="*80)
print("Building Disease-Disease Co-occurrence Network")
print("="*80)

# ============================================================================
# STEP 1: Load Data
# ============================================================================
print("\n[STEP 1] Loading elderly patient conditions...")

df = pd.read_csv('../output/elderly_conditions_with_names.csv', low_memory=False)

# Filter to only conditions with valid disease names
df = df[df['concept_name'].notna()].copy()

print(f"  ✓ Loaded {len(df)} condition records")
print(f"  ✓ {df['person_id'].nunique()} unique patients")
print(f"  ✓ {df['condition_concept_id'].nunique()} unique diseases")

# ============================================================================
# STEP 2: Create Patient-Disease Matrix
# ============================================================================
print("\n[STEP 2] Creating patient-disease relationships...")

# Get unique diseases per patient
patient_diseases = df.groupby('person_id')['condition_concept_id'].apply(set).to_dict()
disease_names = df[['condition_concept_id', 'concept_name']].drop_duplicates()
disease_name_map = dict(zip(disease_names['condition_concept_id'], disease_names['concept_name']))

print(f"  ✓ Built disease sets for {len(patient_diseases)} patients")

# ============================================================================
# STEP 3: Calculate Disease Co-occurrence
# ============================================================================
print("\n[STEP 3] Calculating disease co-occurrences...")
print("  (This may take a few minutes...)")

# Count co-occurrences
cooccurrence = defaultdict(int)
total_pairs = 0

for patient_id, diseases in patient_diseases.items():
    if len(diseases) < 2:
        continue
    
    # For each pair of diseases this patient has
    for disease1, disease2 in combinations(sorted(diseases), 2):
        cooccurrence[(disease1, disease2)] += 1
        total_pairs += 1

print(f"  ✓ Found {len(cooccurrence)} unique disease pairs")
print(f"  ✓ Total co-occurrence instances: {total_pairs:,}")

# ============================================================================
# STEP 4: Build NetworkX Graph
# ============================================================================
print("\n[STEP 4] Building network graph...")

G = nx.Graph()

# Add nodes (diseases)
for disease_id, disease_name in disease_name_map.items():
    G.add_node(disease_id, name=disease_name)

# Add edges (co-occurrences)
# Filter to edges with at least 2 patients sharing both diseases (reduce noise)
MIN_COOCCURRENCE = 2

for (disease1, disease2), weight in cooccurrence.items():
    if weight >= MIN_COOCCURRENCE:
        G.add_edge(disease1, disease2, weight=weight)

print(f"  ✓ Network built:")
print(f"      Nodes (diseases): {G.number_of_nodes()}")
print(f"      Edges (co-occurrences): {G.number_of_edges()}")
print(f"      Density: {nx.density(G):.4f}")

# ============================================================================
# STEP 5: Network Statistics
# ============================================================================
print("\n[STEP 5] Computing network statistics...")

# Get largest connected component
if not nx.is_connected(G):
    largest_cc = max(nx.connected_components(G), key=len)
    G_main = G.subgraph(largest_cc).copy()
    print(f"  ✓ Largest connected component: {G_main.number_of_nodes()} nodes, {G_main.number_of_edges()} edges")
else:
    G_main = G
    print(f"  ✓ Graph is fully connected")

# Basic statistics
print(f"\n  Network Metrics:")
print(f"    Average degree: {sum(dict(G_main.degree()).values()) / G_main.number_of_nodes():.2f}")
print(f"    Average clustering coefficient: {nx.average_clustering(G_main):.4f}")

# Top 10 most connected diseases (hubs)
degree_centrality = nx.degree_centrality(G_main)
top_hubs = sorted(degree_centrality.items(), key=lambda x: x[1], reverse=True)[:10]

print(f"\n  Top 10 Hub Diseases (most connections):")
for disease_id, centrality in top_hubs:
    disease_name = disease_name_map[disease_id]
    degree = G_main.degree(disease_id)
    print(f"    {disease_name[:60]:60s} | Degree: {degree:4d} | Centrality: {centrality:.4f}")

# ============================================================================
# STEP 6: Save Network Data
# ============================================================================
print("\n[STEP 6] Saving network files...")

# Save full graph as pickle
with open('disease_network_full.pkl', 'wb') as f:
    pickle.dump(G, f)
print(f"  ✓ Saved full network: disease_network_full.pkl")

# Save main component as pickle
with open('disease_network_main.pkl', 'wb') as f:
    pickle.dump(G_main, f)
print(f"  ✓ Saved main component: disease_network_main.pkl")

# Save as GraphML (can be opened in Gephi, Cytoscape, etc.)
nx.write_graphml(G_main, 'disease_network_main.graphml')
print(f"  ✓ Saved as GraphML: disease_network_main.graphml")

# Save as edge list CSV
edge_list = []
for u, v, data in G_main.edges(data=True):
    edge_list.append({
        'disease1_id': u,
        'disease1_name': disease_name_map[u],
        'disease2_id': v,
        'disease2_name': disease_name_map[v],
        'weight': data['weight']
    })

edge_df = pd.DataFrame(edge_list)
edge_df = edge_df.sort_values('weight', ascending=False)
edge_df.to_csv('disease_cooccurrence_edges.csv', index=False)
print(f"  ✓ Saved edge list: disease_cooccurrence_edges.csv")

# Save node list with basic metrics
node_list = []
for node in G_main.nodes():
    node_list.append({
        'disease_id': node,
        'disease_name': disease_name_map[node],
        'degree': G_main.degree(node),
        'degree_centrality': degree_centrality[node]
    })

node_df = pd.DataFrame(node_list)
node_df = node_df.sort_values('degree', ascending=False)
node_df.to_csv('disease_network_nodes.csv', index=False)
print(f"  ✓ Saved node list: disease_network_nodes.csv")

print("\n" + "="*80)
print("NETWORK CONSTRUCTION COMPLETE!")
print("="*80)
print(f"\nFiles created in 'network_analysis/' folder:")
print(f"  1. disease_network_full.pkl - Full network (Python pickle)")
print(f"  2. disease_network_main.pkl - Main component (Python pickle)")
print(f"  3. disease_network_main.graphml - Main component (GraphML format)")
print(f"  4. disease_cooccurrence_edges.csv - Edge list with weights")
print(f"  5. disease_network_nodes.csv - Node list with metrics")
print("\nNext: Run community detection to find disease clusters!")
print("="*80)
