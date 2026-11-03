import re
import unicodedata

from rdflib import Graph, Literal, URIRef
from rdflib.namespace import DCTERMS, FOAF, RDF, RDFS, XSD

from config import EX, ONT
from data import ACTORS, COUNTRIES, DIRECTORS, FILMS, GENRES


# Turns any human-readable name into a safe ASCII fragment for a URI.
# Input:  text - arbitrary string, e.g. "Amélie" or "Kill Bill: Vol. 1"
# Output: ASCII string with underscores, e.g. "Amelie" or "Kill_Bill_Vol_1"
def slug(text: str) -> str:
    # Decompose accented letters and drop everything that is not ASCII
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    # Collapse runs of other characters into one underscore and trim the edges
    return re.sub(r"[^A-Za-z0-9]+", "_", text).strip("_")


# Builds the URI of a resource inside our own namespace.
# Input:  kind - resource category ("film", "actor", ...), name - its display name
# Output: URIRef like http://example.org/films/actor/Tom_Hardy
def uri(kind: str, name: str) -> URIRef:
    return EX[f"{kind}/{slug(name)}"]


# Adds a minimal ontology to the graph: the five classes and their hierarchy.
# Input:  g - graph to modify in place
# Output: none (graph is changed)
def _add_schema(g: Graph) -> None:
    # Declare each class and give it a human-readable label
    for cls in ("Film", "Director", "Actor", "Genre", "Country"):
        g.add((ONT[cls], RDF.type, RDFS.Class))
        g.add((ONT[cls], RDFS.label, Literal(cls, lang="en")))
    # Reuse FOAF: directors and actors are kinds of foaf:Person
    g.add((ONT.Director, RDFS.subClassOf, FOAF.Person))
    g.add((ONT.Actor, RDFS.subClassOf, FOAF.Person))


# Adds one person (director or actor) with all of their properties.
# Input:  g - graph, name - full name, birth - birth year, country - citizenship name,
#         cls - ONT.Director or ONT.Actor, kind - URI category ("director" / "actor")
# Output: none (graph is changed)
def _add_person(g: Graph, name: str, birth: int, country: str, cls, kind: str) -> None:
    p = uri(kind, name)
    # Typed both as our class and as foaf:Person
    g.add((p, RDF.type, cls))
    g.add((p, RDF.type, FOAF.Person))
    g.add((p, FOAF.name, Literal(name)))
    g.add((p, ONT.birthYear, Literal(birth, datatype=XSD.integer)))
    # Link to the country resource instead of storing a plain string
    g.add((p, ONT.citizenOf, uri("country", country)))


# Builds the complete RDF graph from the dictionaries in data.py.
# Input:  none (reads COUNTRIES, GENRES, DIRECTORS, ACTORS, FILMS)
# Output: rdflib Graph with schema, reference entities, people and films
def build_graph() -> Graph:
    g = Graph()
    # Prefixes make the Turtle output readable
    g.bind("ex", EX)
    g.bind("ont", ONT)
    g.bind("foaf", FOAF)
    g.bind("dcterms", DCTERMS)
    g.bind("rdfs", RDFS)

    _add_schema(g)

    # Reference entities first, so films can link to them
    for c in COUNTRIES:
        g.add((uri("country", c), RDF.type, ONT.Country))
        g.add((uri("country", c), RDFS.label, Literal(c, lang="en")))
    for name in GENRES:
        g.add((uri("genre", name), RDF.type, ONT.Genre))
        g.add((uri("genre", name), RDFS.label, Literal(name, lang="en")))

    # People: directors and actors share the same helper
    for n, (birth, country) in DIRECTORS.items():
        _add_person(g, n, birth, country, ONT.Director, "director")
    for n, (birth, country) in ACTORS.items():
        _add_person(g, n, birth, country, ONT.Actor, "actor")

    # Films with literals (title, year) and links to director, countries, genres, cast
    for title, (year, director, countries, genres, actors) in FILMS.items():
        f = uri("film", title)
        g.add((f, RDF.type, ONT.Film))
        g.add((f, DCTERMS.title, Literal(title, lang="en")))
        g.add((f, ONT.releaseYear, Literal(year, datatype=XSD.integer)))
        g.add((f, ONT.directedBy, uri("director", director)))
        # One triple per country / genre / actor (many-to-many relations)
        for c in countries:
            g.add((f, ONT.producedIn, uri("country", c)))
        for gn in genres:
            g.add((f, ONT.hasGenre, uri("genre", gn)))
        for a in actors:
            g.add((f, ONT.starring, uri("actor", a)))
    return g