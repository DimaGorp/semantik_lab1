from pathlib import Path

from rdflib import Namespace

# Custom namespace for resources (instances: films, people, genres, countries)
EX = Namespace("http://example.org/films/")
# Custom namespace for ontology terms (classes and properties)
ONT = Namespace("http://example.org/films/ontology#")

# Project root and the folder where all generated files are written
BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "output"
# Main graph in Turtle and its rendered picture
TURTLE_PATH = OUTPUT_DIR / "films.ttl"
GRAPH_IMAGE_PATH = OUTPUT_DIR / "graph.png"