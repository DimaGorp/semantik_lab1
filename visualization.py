from pathlib import Path

import matplotlib.pyplot as plt
import networkx as nx
from matplotlib.lines import Line2D
from rdflib import Graph
from rdflib.namespace import DCTERMS, FOAF, RDF, RDFS

from config import ONT

# Node color per class and edge color per relation (also used in the legend)
NODE_COLORS = {ONT.Film: "#4C78A8", ONT.Director: "#E45756", ONT.Actor: "#F2A93B",
               ONT.Genre: "#54A24B", ONT.Country: "#9467BD"}
EDGE_COLORS = {ONT.directedBy: "#E45756", ONT.starring: "#F2A93B",
               ONT.hasGenre: "#54A24B", ONT.producedIn: "#9467BD",
               ONT.citizenOf: "#888888"}


# Picks the text to display on a node.
# Input:  g - graph, node - resource URI
# Output: film title, person name or rdfs:label; falls back to the last URI segment
def _label(g: Graph, node) -> str:
    for prop in (DCTERMS.title, FOAF.name, RDFS.label):
        for lit in g.objects(node, prop):
            return str(lit)
    return str(node).rsplit("/", 1)[-1]


# Draws the graph (resources and links only, no literals), saves a PNG, optionally shows a window.
# Input:  g - RDF graph, path - PNG output path, show - open the interactive window if True
# Output: none (writes the image file)
def visualize(g: Graph, path: Path, show: bool = True) -> None:
    # Class of every typed resource; only our five classes are kept
    type_of = {s: o for s, _, o in g.triples((None, RDF.type, None))
               if o in NODE_COLORS}

    # Build a directed multigraph: one edge per relation between two typed resources
    G = nx.MultiDiGraph()
    for s, p, o in g:
        if p in (ONT.directedBy, ONT.starring, ONT.hasGenre, ONT.producedIn) \
                and s in type_of and o in type_of:
            G.add_edge(s, o, pred=p)
    # citizenOf only for directors, to keep the picture readable
    for s, _, o in g.triples((None, ONT.citizenOf, None)):
        if type_of.get(s) == ONT.Director:
            G.add_edge(s, o, pred=ONT.citizenOf)

    # Fixed seed gives the same layout on every run
    pos = nx.spring_layout(G.to_undirected(), seed=7, k=0.9, iterations=200)
    fig, ax = plt.subplots(figsize=(22, 16))

    # Draw edges grouped by relation so each group gets its own color
    for pred, col in EDGE_COLORS.items():
        edges = [(u, v) for u, v, d in G.edges(data=True) if d["pred"] == pred]
        nx.draw_networkx_edges(G, pos, edgelist=edges, edge_color=col, alpha=0.55,
                               width=1.3, arrows=True, arrowsize=12, ax=ax,
                               connectionstyle="arc3,rad=0.05")
    # Draw nodes grouped by class; films are larger than other nodes
    for cls, col in NODE_COLORS.items():
        nodes = [n for n in G.nodes if type_of[n] == cls]
        nx.draw_networkx_nodes(G, pos, nodelist=nodes, node_color=col,
                               node_size=900 if cls == ONT.Film else 450, ax=ax)
    nx.draw_networkx_labels(G, pos, {n: _label(g, n) for n in G.nodes},
                            font_size=8, ax=ax)

    # Legend: colored dots for classes, colored lines for relations
    short = lambda term: str(term).rsplit("#", 1)[-1]
    handles = [Line2D([0], [0], marker="o", color="w", markerfacecolor=c,
                      markersize=12, label=short(k)) for k, c in NODE_COLORS.items()]
    handles += [Line2D([0], [0], color=c, lw=2, label=short(k))
                for k, c in EDGE_COLORS.items()]
    ax.legend(handles=handles, loc="upper left", fontsize=11)
    ax.set_title("RDF-граф: фільми, режисери, актори, жанри, країни", fontsize=16)
    ax.axis("off")
    fig.tight_layout()
    fig.savefig(path, dpi=130)
    if show:
        plt.show()  # zoomable window; close it to let the program exit
    plt.close(fig)