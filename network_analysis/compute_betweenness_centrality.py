"""
Compute betweenness centrality for disease co-occurrence network.
Betweenness measures how often a node appears on shortest paths between other nodes.
High betweenness indicates "bridge" diseases connecting different disease clusters.
"""
import pandas as pd
import networkx as nx
import pickle
import os

# Load network
COHORT_NAME = 'elderly_75plus'
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
COHORT_DIR = os.path.join(SCRIPT_DIR, COHORT_NAME)

network_path = os.path.join(COHORT_DIR, 'disease_network_main.pkl')

with open(network_path, 'rb') as f:
    G = pickle.load(f)
    
# Compute unweighted betweenness
betweenness = nx.betweenness_centrality(G, normalized=True)

# Compute weighted betweenness 
for u, v, data in G.edges(data=True):
    data['distance'] = 1.0 / data['weight'] if data['weight'] > 0 else 1.0

betweenness_weighted = nx.betweenness_centrality(G, normalized=True, weight='distance')
    
# Create results dataframe
node_names = nx.get_node_attributes(G, 'name')
results = []
for node in G.nodes():
    results.append({
        'disease_id': node,
        'disease_name': node_names.get(node, 'Unknown'),
        'degree': G.degree(node),
        'betweenness_centrality': betweenness[node],
        'betweenness_weighted': betweenness_weighted[node]
    })

df = pd.DataFrame(results).sort_values('betweenness_centrality', ascending=False)

print("\nTop 10 Bridge Diseases (by unweighted betweenness):")
for idx, row in df.head(10).iterrows():
    print(f"  {row['disease_name'][:50]:50s} | Betw: {row['betweenness_centrality']:.4f}")
    
# Save results
output_path = os.path.join(COHORT_DIR, 'betweenness_centrality_nodes.csv')
df.to_csv(output_path, index=False)
print(f"\nSaved: {output_path}")

if __name__ == '__main__':
    pass 
