"""
Community Detection and Visualization
Detects disease clusters using Louvain algorithm and creates visualizations
"""

import pandas as pd
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import pickle
import os
import community.community_louvain as community_louvain

print("="*80)
print("Community Detection in Disease Network")
print("="*80)

# Load network
COHORT_NAME = os.environ.get('COHORT_NAME', 'elderly_75plus')
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
COHORT_DIR = os.path.join(SCRIPT_DIR, COHORT_NAME)
os.makedirs(COHORT_DIR, exist_ok=True)

network_path = os.path.join(COHORT_DIR, 'disease_network_main.pkl')
print(f"\nLoading: {network_path}")
with open(network_path, 'rb') as f:
    G = pickle.load(f)

print(f"Network: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")

# Detect communities
print("\nDetecting communities (Louvain)...")
partition = community_louvain.best_partition(G, weight='weight')
modularity = community_louvain.modularity(partition, G, weight='weight')

print(f"\nCommunity Statistics:")
print(f"  Communities: {len(set(partition.values()))}")
print(f"  Modularity: {modularity:.4f}")

nx.set_node_attributes(G, partition, 'community')

# Analyze communities
communities = {}
for node, comm_id in partition.items():
    if comm_id not in communities:
        communities[comm_id] = []
    communities[comm_id].append(node)

sorted_communities = sorted(communities.items(), key=lambda x: len(x[1]), reverse=True)

print(f"\nTop Communities:")
for comm_id, nodes in sorted_communities[:10]:
    print(f"  Community {comm_id}: {len(nodes)} diseases")

print("\nTop diseases per community:")
community_analysis = []
for comm_id, nodes in sorted_communities[:10]:
    diseases = [(G.nodes[node]['name'], G.degree(node)) for node in nodes]
    diseases.sort(key=lambda x: x[1], reverse=True)
    top_diseases = [d[0] for d in diseases[:20]]
    
    community_analysis.append({
        'community_id': comm_id,
        'size': len(nodes),
        'top_diseases': '; '.join(top_diseases)
    })
    
    print(f"\n  Community {comm_id} ({len(nodes)} diseases):")
    for disease, degree in diseases[:10]:
        print(f"    - {disease[:70]}")

comm_df = pd.DataFrame(community_analysis)
comm_df.to_csv(os.path.join(COHORT_DIR, 'community_analysis.csv'), index=False)

# Create visualizations
print("\nCreating visualizations...")
TOP_N = 300
node_degrees = dict(G.degree())
top_nodes = sorted(node_degrees.items(), key=lambda x: x[1], reverse=True)[:TOP_N]
top_node_ids = [node for node, degree in top_nodes]
G_viz = G.subgraph(top_node_ids).copy()

pos = nx.spring_layout(G_viz, k=0.5, iterations=50, seed=42, weight='weight')
fig, ax = plt.subplots(figsize=(20, 20))

partition_viz = {node: partition[node] for node in G_viz.nodes()}
communities_in_viz = set(partition_viz.values())
colors = plt.cm.tab20(np.linspace(0, 1, len(communities_in_viz)))
community_to_color = {comm: colors[i] for i, comm in enumerate(sorted(communities_in_viz))}
node_colors = [community_to_color[partition_viz[node]] for node in G_viz.nodes()]

nx.draw_networkx_nodes(G_viz, pos, node_color=node_colors, node_size=100, alpha=0.8, ax=ax)
nx.draw_networkx_edges(G_viz, pos, alpha=0.1, width=0.5, ax=ax)

top_hubs = sorted(G_viz.degree(), key=lambda x: x[1], reverse=True)[:30]
labels = {node: G_viz.nodes[node]['name'][:30] for node, degree in top_hubs}
nx.draw_networkx_labels(G_viz, pos, labels, font_size=8, ax=ax)

ax.set_title(f'Disease Co-occurrence Network - Community Structure\n{G_viz.number_of_nodes()} diseases, {len(communities_in_viz)} communities', 
             fontsize=16, fontweight='bold')
ax.axis('off')
plt.tight_layout()
plt.savefig(os.path.join(COHORT_DIR, 'disease_network_communities.png'), dpi=300, bbox_inches='tight')

# Create community-level network
community_graph = nx.Graph()
for comm_id, nodes in communities.items():
    community_graph.add_node(comm_id, size=len(nodes))

for u, v, data in G.edges(data=True):
    comm_u, comm_v = partition[u], partition[v]
    if comm_u != comm_v:
        if community_graph.has_edge(comm_u, comm_v):
            community_graph[comm_u][comm_v]['weight'] += data['weight']
        else:
            community_graph.add_edge(comm_u, comm_v, weight=data['weight'])

# Visualize community-level network
fig, ax = plt.subplots(figsize=(12, 12))

# Size nodes by community size
node_sizes = [community_graph.nodes[node]['size'] * 5 for node in community_graph.nodes()]

# Position using spring layout
pos_comm = nx.spring_layout(community_graph, k=2, iterations=50, seed=42)

# Draw
nx.draw_networkx_nodes(community_graph, pos_comm, node_size=node_sizes, 
                       node_color=range(len(community_graph.nodes())), 
                       cmap=plt.cm.tab20, alpha=0.7, ax=ax)

nx.draw_networkx_edges(community_graph, pos_comm, alpha=0.3, width=2, ax=ax)

# Add labels
labels = {node: f"C{node}" for node in community_graph.nodes()}
nx.draw_networkx_labels(community_graph, pos_comm, labels, font_size=12, 
                        font_weight='bold', ax=ax)

ax.set_title('Community-Level Network\n(Node size = number of diseases in community)', 
             fontsize=14, fontweight='bold')
ax.axis('off')

plt.tight_layout()
plt.savefig(os.path.join(COHORT_DIR, 'community_network.png'), dpi=300, bbox_inches='tight')
print(f"  ✓ Saved community network: {os.path.join(COHORT_DIR, 'community_network.png')}")

# ============================================================================
# STEP 6: Save Results
# ============================================================================
print("\n[STEP 6] Saving final results...")

# Save node data with communities
node_data = []
for node in G.nodes():
    node_data.append({
        'disease_id': node,
        'disease_name': G.nodes[node]['name'],
        'community': partition[node],
        'degree': G.degree(node),
        'clustering': nx.clustering(G, node)
    })
print(f"\nCommunity network: {community_graph.number_of_nodes()} communities, {community_graph.number_of_edges()} inter-community connections")

pos_comm = nx.spring_layout(community_graph, k=2, iterations=50, seed=42, weight='weight')
fig, ax = plt.subplots(figsize=(12, 10))

sizes = [community_graph.nodes[n]['size'] * 20 for n in community_graph.nodes()]
colors_comm = plt.cm.tab20(np.linspace(0, 1, len(community_graph.nodes())))

nx.draw_networkx_nodes(community_graph, pos_comm, node_color=colors_comm, node_size=sizes, alpha=0.8, ax=ax)
nx.draw_networkx_edges(community_graph, pos_comm, alpha=0.5, width=2, ax=ax)

labels = {n: f"C{n}\n({community_graph.nodes[n]['size']} diseases)" for n in community_graph.nodes()}
nx.draw_networkx_labels(community_graph, pos_comm, labels, font_size=10, ax=ax)

ax.set_title('Community-Level Network\nNode size = number of diseases', fontsize=14, fontweight='bold')
ax.axis('off')
plt.tight_layout()
plt.savefig(os.path.join(COHORT_DIR, 'community_network.png'), dpi=300, bbox_inches='tight')

# Save results
node_df = pd.DataFrame(node_data).sort_values(['community', 'degree'], ascending=[True, False])
node_df.to_csv(os.path.join(COHORT_DIR, 'diseases_with_communities.csv'), index=False)

comm_summary = [{
    'community_id': comm_id,
    'num_diseases': len(nodes),
    'internal_edges': G.subgraph(nodes).number_of_edges(),
    'density': nx.density(G.subgraph(nodes)),
    'avg_clustering': nx.average_clustering(G.subgraph(nodes))
} for comm_id, nodes in communities.items()]

comm_summary_df = pd.DataFrame(comm_summary).sort_values('num_diseases', ascending=False)
comm_summary_df.to_csv(os.path.join(COHORT_DIR, 'community_summary.csv'), index=False)

print(f"\nCommunity detection complete:")
print(f"  • {len(communities)} communities detected")
print(f"  • Modularity: {modularity:.4f}")
print(f"  • Average clustering: {nx.average_clustering(G):.4f}")
