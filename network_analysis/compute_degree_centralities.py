"""
Compute unweighted degree and weighted degree (strength) for disease network.

Outputs:
 - degree_centrality_nodes.csv  (disease_id, disease_name, degree, degree_centrality, strength, strength_norm)
"""

import os
import pickle
import networkx as nx
import pandas as pd

def main():
    COHORT_NAME = os.environ.get('COHORT_NAME', 'elderly_75plus')
    SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
    COHORT_DIR = os.path.join(SCRIPT_DIR, COHORT_NAME)
    os.makedirs(COHORT_DIR, exist_ok=True)
    network_path = os.path.join(COHORT_DIR, 'disease_network_main.pkl')
    with open(network_path, 'rb') as f:
        G = pickle.load(f)

    N = G.number_of_nodes()

    # Unweighted degree
    deg_map = dict(G.degree(weight=None))

    # Weighted degree using edge weight attribute
    str_map = dict(G.degree(weight='weight'))
    max_strength = max(str_map.values()) if len(str_map) > 0 else 1

    rows = []
    for node in G.nodes():
        name = G.nodes[node].get('name', '') if isinstance(G, nx.Graph) else G.nodes[node].get('name', '')
        deg = int(deg_map.get(node, 0))
        strength = float(str_map.get(node, 0.0))
        deg_centrality = deg / (N - 1) if N > 1 else 0.0
        strength_norm = strength / max_strength if max_strength > 0 else 0.0
        rows.append({
            'disease_id': node,
            'disease_name': name,
            'degree': deg,
            'degree_centrality': deg_centrality,
            'strength': strength,
            'strength_norm': strength_norm
        })

    df = pd.DataFrame(rows).sort_values('degree', ascending=False).reset_index(drop=True)
    out_csv = os.path.join(COHORT_DIR, 'degree_centrality_nodes.csv')
    df.to_csv(out_csv, index=False)
    # Print summaries and top-10 lists
    print(f"{N} nodes, {G.number_of_edges()} edges")

    print("Degree summary:")
    print(df['degree'].describe().to_string())

    top = min(10, len(df))
    if top > 0:
        print('\nTop nodes by degree:')
        print(df[['disease_id', 'disease_name', 'degree']].head(top).to_string(index=False))
        print('\nTop nodes by strength:')
        print(df[['disease_id', 'disease_name', 'strength']].sort_values('strength', ascending=False).head(top).to_string(index=False))


if __name__ == '__main__':
    main()
