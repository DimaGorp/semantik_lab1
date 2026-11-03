from rdflib import Graph, Namespace
from rdflib.namespace import OWL

from config import OUTPUT_DIR, TURTLE_PATH
from graph_builder import uri
from sparql_queries import PREFIXES, _console_table

# Wikidata entity namespace and the public SPARQL endpoint
WD = Namespace("http://www.wikidata.org/entity/")
WIKIDATA_ENDPOINT = "https://query.wikidata.org/sparql"
# Output: our graph plus the owl:sameAs links
LINKED_PATH = OUTPUT_DIR / "films_linked.ttl"

# Own resource -> the same real-world entity in Wikidata (used with owl:sameAs)
LINKS = {
    uri("director", "Christopher Nolan"): WD.Q25191,
    uri("film", "Inception"): WD.Q25188,
}

# Federated query: film and director from the local graph, joined with Wikidata data
# (IMDb id of the film, birth date and birthplace of the director).
# The word ENDPOINT is replaced with the real URL in run()
QUERY = PREFIXES + """PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX wdt: <http://www.wikidata.org/prop/direct/>

SELECT ?title ?director ?ownBirthYear ?wdBirth ?imdb
       (GROUP_CONCAT(DISTINCT ?pl; SEPARATOR=", ") AS ?birthPlace) WHERE {
  ?f a ont:Film ;
     dcterms:title ?title ;
     owl:sameAs ?wdf ;
     ont:directedBy ?d .
  ?d foaf:name ?director ;
     ont:birthYear ?ownBirthYear ;
     owl:sameAs ?wdd .
  SERVICE <ENDPOINT> {
    ?wdf wdt:P345 ?imdb .
    ?wdd wdt:P569 ?wdBirth ;
         wdt:P19 ?place .
    ?place rdfs:label ?pl .
    FILTER (LANG(?pl) = "en")
  }
}
GROUP BY ?title ?director ?ownBirthYear ?wdBirth ?imdb"""


# Adds the owl:sameAs links, saves the linked graph and runs the federated query.
# Input:  endpoint - SPARQL endpoint URL (default: Wikidata)
# Output: none (writes films_linked.ttl, prints links and query result)
def run(endpoint: str = WIKIDATA_ENDPOINT) -> None:
    # Load the saved graph and attach the links to Wikidata
    g = Graph()
    g.parse(TURTLE_PATH, format="turtle")
    for own, wd in LINKS.items():
        g.add((own, OWL.sameAs, wd))
    g.serialize(destination=str(LINKED_PATH), format="turtle")

    # Show each created link: both URIs and the predicate
    print("[5] Зв'язки:")
    for own, wd in LINKS.items():
        print(f"    {own}\n      owl:sameAs {wd}")

    # Run the federated query; the network may be down, so errors are caught
    try:
        res = g.query(QUERY.replace("ENDPOINT", endpoint))
        rows = list(res)
    except Exception as e:  # network or endpoint unavailable
        print(f"[5] Запит до Wikidata не вдався: {e}")
        return
    # Print the combined result (own data + Wikidata)
    print("\nДані власного графу + Wikidata")
    print(_console_table([str(v) for v in res.vars], rows) if rows
          else "(порожній результат)")