from rdflib import Graph, Literal
from rdflib.namespace import DCTERMS, FOAF, RDF, XSD

from config import ONT, OUTPUT_DIR, TURTLE_PATH
from graph_builder import uri

# Second serialization format and the file with manual edits
RDFXML_PATH = OUTPUT_DIR / "films.rdf"
EDITED_PATH = OUTPUT_DIR / "films_edited.ttl"


# Formats one triple as a readable Turtle-like line with prefixes.
# Input:  g - graph (for its prefixes), t - (subject, predicate, object) tuple
# Output: string such as "ex:film/Tenet rdf:type ont:Film ."
def _fmt(g: Graph, t) -> str:
    return " ".join(x.n3(g.namespace_manager) for x in t) + " ."


# Saves the graph in two formats: Turtle and RDF/XML.
# Input:  g - graph to serialize
# Output: none (writes films.ttl and films.rdf)
def save_formats(g: Graph) -> None:
    g.serialize(destination=str(TURTLE_PATH), format="turtle")
    g.serialize(destination=str(RDFXML_PATH), format="xml")
    print(f"[3.1] Saved: {TURTLE_PATH.name}, {RDFXML_PATH.name}")


# Reads the Turtle file back, adds a new actor and a new film, saves the result.
# Input:  none (reads TURTLE_PATH)
# Output: edited Graph (also written to films_edited.ttl)
def read_and_edit() -> Graph:
    # Parse the saved file into a fresh graph, remember the original size
    g = Graph()
    g.parse(TURTLE_PATH, format="turtle")
    before = len(g)

    # New actor with the same set of properties as the others
    p = uri("actor", "Robert Pattinson")
    g.add((p, RDF.type, ONT.Actor))
    g.add((p, RDF.type, FOAF.Person))
    g.add((p, FOAF.name, Literal("Robert Pattinson")))
    g.add((p, ONT.birthYear, Literal(1986, datatype=XSD.integer)))
    g.add((p, ONT.citizenOf, uri("country", "United Kingdom")))

    # New film: literals first, then links to existing resources
    f = uri("film", "Tenet")
    g.add((f, RDF.type, ONT.Film))
    g.add((f, DCTERMS.title, Literal("Tenet", lang="en")))
    g.add((f, ONT.releaseYear, Literal(2020, datatype=XSD.integer)))
    g.add((f, ONT.directedBy, uri("director", "Christopher Nolan")))
    g.add((f, ONT.producedIn, uri("country", "USA")))
    g.add((f, ONT.producedIn, uri("country", "United Kingdom")))
    g.add((f, ONT.hasGenre, uri("genre", "Action")))
    g.add((f, ONT.hasGenre, uri("genre", "Science Fiction")))
    # Cast: the new actor plus an actor that already exists in the graph
    g.add((f, ONT.starring, p))
    g.add((f, ONT.starring, uri("actor", "Michael Caine")))

    g.serialize(destination=str(EDITED_PATH), format="turtle")
    print(f"[3.2] Read {before} triples, {len(g)} after edit -> {EDITED_PATH.name}")
    return g


# Prints the first triples of the graph and a pattern-based selection of film titles.
# Input:  g - graph, limit - how many triples to show in the first part
# Output: none (prints to console)
def print_selected(g: Graph, limit: int = 10) -> None:
    # Part 1: first N triples in whatever order the graph yields them
    print(f"[3.3] First {limit} triples out of {len(g)}:")
    for i, t in enumerate(g):
        if i >= limit:
            break
        print("   ", _fmt(g, t))

    # Part 2: pattern (None, dcterms:title, None) matches every film title; sort by title
    print("[3.3] Selection (None, dcterms:title, None):")
    for s, _, o in sorted(g.triples((None, DCTERMS.title, None)), key=lambda t: str(t[2])):
        print("   ", _fmt(g, (s, DCTERMS.title, o)))


# Shows every triple connected to one entity, in both directions.
# Input:  g - graph, name - entity name, kind - URI category ("director", "film", ...)
# Output: none (prints outgoing and incoming triples)
def describe(g: Graph, name: str, kind: str) -> None:
    node = uri(kind, name)
    print(f"[3.4] Entity {node.n3(g.namespace_manager)}")
    # Entity as subject: its own properties and outgoing links
    print("  Outgoing (entity = subject):")
    for t in g.triples((node, None, None)):
        print("   ", _fmt(g, t))
    # Entity as object: who points at it (e.g. films it directed)
    print("  Incoming (entity = object):")
    for t in g.triples((None, None, node)):
        print("   ", _fmt(g, t))


# Runs the whole of step 3 in order.
# Input:  g - the freshly built graph
# Output: none
def run(g: Graph) -> None:
    save_formats(g)
    edited = read_and_edit()
    print_selected(edited)
    describe(edited, "Christopher Nolan", "director")