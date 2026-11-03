from rdflib import Graph

from config import TURTLE_PATH

# Prefixes prepended to every query
PREFIXES = """PREFIX ont:     <http://example.org/films/ontology#>
PREFIX foaf:    <http://xmlns.com/foaf/0.1/>
PREFIX dcterms: <http://purl.org/dc/terms/>
PREFIX rdfs:    <http://www.w3.org/2000/01/rdf-schema#>
"""

# Each item: (question, what the query demonstrates, query body)
# Queries 1-6 cover: join across types, FILTER, COUNT, 3-hop path, AVG/MIN/MAX + HAVING, ORDER BY
QUERIES = [
    ("Які фільми зняв Christopher Nolan?",
     "зв'язок між типами сутностей (Film -> Director), сортування",
     """SELECT ?title ?year WHERE {
  ?f dcterms:title ?title ;
     ont:releaseYear ?year ;
     ont:directedBy ?d .
  ?d foaf:name "Christopher Nolan" .
}
ORDER BY ?year"""),

    ("Які фільми вийшли після 2020 року і хто їх зняв?",
     "FILTER, сортування",
     """SELECT ?title ?year ?director WHERE {
  ?f dcterms:title ?title ;
     ont:releaseYear ?year ;
     ont:directedBy ?d .
  ?d foaf:name ?director .
  FILTER (?year > 2020)
}
ORDER BY DESC(?year) ?title"""),

    ("Який режисер має найбільше фільмів у графі?",
     "агрегатна функція COUNT, GROUP BY, сортування",
     """SELECT ?director (COUNT(?f) AS ?films) WHERE {
  ?f ont:directedBy ?d .
  ?d foaf:name ?director .
}
GROUP BY ?director
ORDER BY DESC(?films) ?director"""),

    ("Які актори грали у фільмах жанру Science Fiction і в скількох?",
     "зв'язки Film-Genre та Film-Actor, COUNT, сортування",
     """SELECT ?actor (COUNT(DISTINCT ?f) AS ?sf_films) WHERE {
  ?f ont:hasGenre ?g .
  ?g rdfs:label "Science Fiction"@en .
  ?f ont:starring ?a .
  ?a foaf:name ?actor .
}
GROUP BY ?actor
ORDER BY DESC(?sf_films) ?actor"""),

    ("Які актори грали у фільмах режисерів-громадян США і з якої вони країни?",
     "перехід через 3 зв'язки: Country <- citizenOf - Director <- directedBy - Film - starring -> Actor",
     """SELECT DISTINCT ?director ?film ?actor ?actorCountry WHERE {
  ?dc rdfs:label "USA"@en .
  ?d  ont:citizenOf ?dc ;
      foaf:name ?director .
  ?f  ont:directedBy ?d ;
      dcterms:title ?film ;
      ont:starring ?a .
  ?a  foaf:name ?actor ;
      ont:citizenOf ?ac .
  ?ac rdfs:label ?actorCountry .
}
ORDER BY ?director ?film ?actor"""),

    ("Який середній рік народження акторів за країнами (де акторів не менше двох)?",
     "агрегати AVG, MIN, MAX, COUNT, HAVING",
     """SELECT ?country (COUNT(?a) AS ?actors) (ROUND(AVG(?birth)) AS ?avgBirth)
       (MIN(?birth) AS ?oldest) (MAX(?birth) AS ?youngest) WHERE {
  ?a a ont:Actor ;
     ont:birthYear ?birth ;
     ont:citizenOf ?c .
  ?c rdfs:label ?country .
}
GROUP BY ?country
HAVING (COUNT(?a) >= 2)
ORDER BY ?avgBirth"""),
]


# Renders query results as a column-aligned plain-text table.
# Input:  vars_ - column names, rows - iterable of result rows (None = unbound value)
# Output: multi-line string: header, dashed separator, data rows
def _console_table(vars_, rows) -> str:
    # Header row followed by data rows, all converted to strings
    data = [[str(v) for v in vars_]] + [["" if c is None else str(c) for c in r]
                                         for r in rows]
    # Width of each column = longest cell in it
    widths = [max(len(r[i]) for r in data) for i in range(len(vars_))]
    # Pad every cell to its column width, drop trailing spaces
    line = lambda r: "  ".join(c.ljust(w) for c, w in zip(r, widths)).rstrip()
    return "\n".join([line(data[0]), "  ".join("-" * w for w in widths),
                      *map(line, data[1:])])


# Loads the Turtle graph and runs every query from QUERIES, printing the results.
# Input:  none (reads TURTLE_PATH)
# Output: none (prints a numbered table per query)
def run() -> None:
    # Fresh graph from the file, so queries run on what was actually saved
    g = Graph()
    g.parse(TURTLE_PATH, format="turtle")

    for i, (question, demo, body) in enumerate(QUERIES, 1):
        # Prefixes + body = complete query; result is iterable of rows
        res = g.query(PREFIXES + body)
        vars_ = [str(v) for v in res.vars]
        rows = list(res)
        print(f"\nЗапит {i}. {question}\n{_console_table(vars_, rows)}")