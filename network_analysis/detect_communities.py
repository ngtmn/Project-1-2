"""
Step 2: Community Detection and Visualization

This script:
1. Loads the disease network
2. Detects communities (disease clusters) using Louvain algorithm
3. Visualizes the network with colored communities like the example image
4. Analyzes what diseases are in each community
"""

import pandas as pd
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import pickle
import community.community_louvain as community_louvain

print("="*80)
print("Community Detection in Disease Network")
print("="*80)

# ============================================================================
# STEP 1: Load Network
# ============================================================================
print("\n[STEP 1] Loading disease network...")

with open('disease_network_main.pkl', 'rb') as f:
    G = pickle.load(f)

print(f"  ✓ Loaded network:")
print(f"      Nodes: {G.number_of_nodes()}")
print(f"      Edges: {G.number_of_edges()}")

# ============================================================================
# STEP 2: Detect Communities
# ============================================================================
print("\n[STEP 2] Detecting communities using Louvain algorithm...")

# Use Louvain community detection (optimizes modularity)
partition = community_louvain.best_partition(G, weight='weight')

# Calculate modularity
modularity = community_louvain.modularity(partition, G, weight='weight')

print(f"  ✓ Community detection complete:")
print(f"      Number of communities: {len(set(partition.values()))}")
print(f"      Modularity: {modularity:.4f}")

# Add community to nodes
nx.set_node_attributes(G, partition, 'community')

# ============================================================================
# STEP 3: Analyze Communities
# ============================================================================
print("\n[STEP 3] Analyzing communities...")

# Group nodes by community
communities = {}
for node, comm_id in partition.items():
    if comm_id not in communities:
        communities[comm_id] = []
    communities[comm_id].append(node)

# Sort communities by size
sorted_communities = sorted(communities.items(), key=lambda x: len(x[1]), reverse=True)

print(f"\n  Top 10 Largest Communities:")
for i, (comm_id, nodes) in enumerate(sorted_communities[:10]):
    print(f"    Community {comm_id}: {len(nodes)} diseases")

# Save detailed community analysis
print("\n  Analyzing top communities...")

community_analysis = []
for comm_id, nodes in sorted_communities[:10]:
    # Get disease names and degrees for this community
    diseases = []
    for node in nodes:
        disease_name = G.nodes[node]['name']
        degree = G.degree(node)
        diseases.append((disease_name, degree))
    
    # Sort by degree (most connected first)
    diseases.sort(key=lambda x: x[1], reverse=True)
    
    # Get top 20 diseases in this community
    top_diseases = [d[0] for d in diseases[:20]]
    
    community_analysis.append({
        'community_id': comm_id,
        'size': len(nodes),
        'top_diseases': '; '.join(top_diseases)
    })
    
    print(f"\n  Community {comm_id} ({len(nodes)} diseases):")
    print(f"    Top diseases:")
    for disease, degree in diseases[:10]:
        print(f"      - {disease[:70]}")

# Save to CSV
comm_df = pd.DataFrame(community_analysis)
comm_df.to_csv('community_analysis.csv', index=False)
print(f"\n  ✓ Saved community analysis: community_analysis.csv")

# ============================================================================
# STEP 4: Visualize Network with Communities
# ============================================================================
print("\n[STEP 4] Creating visualizations...")

# For visualization, we'll sample the network to make it readable
# Use top N most connected diseases
TOP_N = 300  # Adjust this to show more/fewer nodes

# Get top nodes by degree
node_degrees = dict(G.degree())
top_nodes = sorted(node_degrees.items(), key=lambda x: x[1], reverse=True)[:TOP_N]
top_node_ids = [node for node, degree in top_nodes]

# Create subgraph
G_viz = G.subgraph(top_node_ids).copy()

print(f"  ✓ Creating visualization with top {TOP_N} most connected diseases...")

# Get positions using spring layout (force-directed)
print("    Computing layout (this may take a minute)...")
pos = nx.spring_layout(G_viz, k=0.5, iterations=50, seed=42, weight='weight')

# Create figure
fig, ax = plt.subplots(figsize=(20, 20))

# Get community colors for visualization
partition_viz = {node: partition[node] for node in G_viz.nodes()}
communities_in_viz = set(partition_viz.values())
num_communities = len(communities_in_viz)

# Create color map
colors = plt.cm.tab20(np.linspace(0, 1, num_communities))
community_to_color = {comm: colors[i] for i, comm in enumerate(sorted(communities_in_viz))}

# Get node colors
node_colors = [community_to_color[partition_viz[node]] for node in G_viz.nodes()]

# Draw network
print("    Drawing network...")
nx.draw_networkx_nodes(G_viz, pos, node_color=node_colors, 
                       node_size=100, alpha=0.8, ax=ax)

# Draw edges (make them lighter and thinner)
nx.draw_networkx_edges(G_viz, pos, alpha=0.1, width=0.5, ax=ax)

# Add labels for top hub nodes only (to avoid clutter)
top_hubs = sorted(G_viz.degree(), key=lambda x: x[1], reverse=True)[:30]
labels = {node: G_viz.nodes[node]['name'][:30] for node, degree in top_hubs}
nx.draw_networkx_labels(G_viz, pos, labels, font_size=8, ax=ax)

ax.set_title(f'Disease Co-occurrence Network - Community Structure\n{G_viz.number_of_nodes()} diseases, {len(communities_in_viz)} communities', 
             fontsize=16, fontweight='bold')
ax.axis('off')

plt.tight_layout()
plt.savefig('disease_network_communities.png', dpi=300, bbox_inches='tight')
print(f"  ✓ Saved visualization: disease_network_communities.png")

# ============================================================================
# STEP 5: Create Community-Level Network
# ============================================================================
print("\n[STEP 5] Creating community-level network...")

# Build network between communities
# Edge weight = sum of edges between communities
community_graph = nx.Graph()

for comm_id, nodes in communities.items():
    community_graph.add_node(comm_id, size=len(nodes))

# Add edges between communities
for u, v, data in G.edges(data=True):
    comm_u = partition[u]
    comm_v = partition[v]
    
    if comm_u != comm_v:  # Only inter-community edges
        if community_graph.has_edge(comm_u, comm_v):
            community_graph[comm_u][comm_v]['weight'] += data['weight']
        else:
            community_graph.add_edge(comm_u, comm_v, weight=data['weight'])

print(f"  ✓ Community network:")
print(f"      Communities: {community_graph.number_of_nodes()}")
print(f"      Inter-community connections: {community_graph.number_of_edges()}")

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
plt.savefig('community_network.png', dpi=300, bbox_inches='tight')
print(f"  ✓ Saved community network: community_network.png")

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

node_df = pd.DataFrame(node_data)
node_df = node_df.sort_values(['community', 'degree'], ascending=[True, False])
node_df.to_csv('diseases_with_communities.csv', index=False)
print(f"  ✓ Saved disease communities: diseases_with_communities.csv")

# Save community summary
comm_summary = []
for comm_id, nodes in communities.items():
    subgraph = G.subgraph(nodes)
    comm_summary.append({
        'community_id': comm_id,
        'num_diseases': len(nodes),
        'internal_edges': subgraph.number_of_edges(),
        'density': nx.density(subgraph),
        'avg_clustering': nx.average_clustering(subgraph)
    })

comm_summary_df = pd.DataFrame(comm_summary)
comm_summary_df = comm_summary_df.sort_values('num_diseases', ascending=False)
comm_summary_df.to_csv('community_summary.csv', index=False)
print(f"  ✓ Saved community summary: community_summary.csv")

print("\n" + "="*80)
print("COMMUNITY DETECTION COMPLETE!")
print("="*80)
print(f"\nKey Findings:")
print(f"  • Detected {len(communities)} disease communities")
print(f"  • Modularity: {modularity:.4f} (strong community structure)")
print(f"  • Average clustering: {nx.average_clustering(G):.4f} (highly clustered)")
print(f"\nFiles created:")
print(f"  1. disease_network_communities.png - Network visualization")
print(f"  2. community_network.png - Community-level view")
print(f"  3. diseases_with_communities.csv - All diseases with community assignments")
print(f"  4. community_summary.csv - Statistics for each community")
print(f"  5. community_analysis.csv - Top diseases in each community")
print("="*80)
