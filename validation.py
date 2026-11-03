from rdflib import Graph
from rdflib.namespace import RDF

from config import ONT

# Relations and classes that the lab requirements are checked against
RELATION_PREDICATES = (ONT.directedBy, ONT.starring, ONT.hasGenre,
                       ONT.producedIn, ONT.citizenOf)
CLASSES = (ONT.Film, ONT.Director, ONT.Actor, ONT.Genre, ONT.Country)


# Prints the graph statistics next to the minimum values required by the lab.
# Input:  g - graph to check
# Output: none (prints to console)
def print_report(g: Graph) -> None:
    # Instances = distinct subjects typed with one of our five classes
    instances = {s for s, _, o in g.triples((None, RDF.type, None)) if o in CLASSES}
    # Only count relations that actually occur in the data
    used_relations = {p for p in RELATION_PREDICATES if (None, p, None) in g}

    print(f"Entity types (classes):          {len(CLASSES)}  (need >= 5)")
    print(f"Entity instances:                {len(instances)}  (need >= 20)")
    print(f"Relation types between entities: {len(used_relations)}  (need >= 5)")
    print(f"RDF triples:                     {len(g)}  (need >= 50)")
    print("Existing vocabularies: FOAF (foaf:name, foaf:Person), "
          "Dublin Core (dcterms:title), RDFS (rdfs:label)")