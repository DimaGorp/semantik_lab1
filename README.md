# Lab 1: Semantic Web, RDF and SPARQL

An RDF graph for the "films" domain built with Python and RDFLib, queried with SPARQL and linked to Wikidata.

Course: Principles and Methods of Data Linking in Semantic Web Applications, Taras Shevchenko National University of Kyiv.

## What it does

1. Builds an RDF graph from hand-written data (14 films, 7 directors, 30 actors, 11 genres, 9 countries).
2. Validates the graph against the lab requirements (classes, instances, relations, triples).
3. Saves the graph as Turtle and RDF/XML, reads it back, edits it, prints selected triples and everything connected to one entity.
4. Runs 6 SPARQL queries (FILTER, ORDER BY, COUNT/AVG/MIN/MAX, HAVING, a 3-hop path).
5. Links own resources to Wikidata with `owl:sameAs` and runs a federated query (`SERVICE`).
6. Draws the graph and saves it as a PNG.

## Graph model

| Class | Description |
| --- | --- |
| `ont:Film` | a film |
| `ont:Director` | a director (subclass of `foaf:Person`) |
| `ont:Actor` | an actor (subclass of `foaf:Person`) |
| `ont:Genre` | a genre |
| `ont:Country` | a country |

Relations: `ont:directedBy`, `ont:starring`, `ont:hasGenre`, `ont:producedIn`, `ont:citizenOf`.
Literal properties: `ont:releaseYear`, `ont:birthYear`.
Reused vocabularies: FOAF, Dublin Core (`dcterms:title`), RDFS.

Resource URIs look like `http://example.org/films/film/Inception`; ontology terms live in `http://example.org/films/ontology#`.

## Project structure

| File | Purpose |
| --- | --- |
| `main.py` | entry point, runs all steps in order |
| `config.py` | namespaces and file paths |
| `data.py` | source data for the domain |
| `graph_builder.py` | builds the RDF graph (step 2) |
| `validation.py` | checks the graph against the lab requirements |
| `graph_ops.py` | serialization, editing, triple output (step 3) |
| `sparql_queries.py` | SPARQL queries to the local graph (step 4) |
| `external_link.py` | Wikidata links and federated query (step 5) |
| `visualization.py` | graph drawing with NetworkX and Matplotlib |

## Requirements

- Python 3.9+
- packages from `requirements.txt`: `rdflib`, `networkx`, `matplotlib`, `SPARQLWrapper`
- internet connection for the Wikidata query (step 5); without it the step prints an error and the rest still works

## Run

```bash
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux / macOS
pip install -r requirements.txt
python main.py
```

The last step opens a Matplotlib window with the graph. Close it to let the program finish.

## Output

All generated files are written to `output/`:

| File | Content |
| --- | --- |
| `films.ttl` | the graph in Turtle |
| `films.rdf` | the graph in RDF/XML |
| `films_edited.ttl` | the graph after adding the film Tenet and the actor Robert Pattinson |
| `films_linked.ttl` | the graph with `owl:sameAs` links to Wikidata |
| `graph.png` | visualization of the graph |

## Wikidata links

| Own resource | Wikidata |
| --- | --- |
| `ex:film/Inception` | `wd:Q25188` |
| `ex:director/Christopher_Nolan` | `wd:Q25191` |

`owl:sameAs` is used because both URIs identify the same real-world entity.
