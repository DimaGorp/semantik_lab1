from config import GRAPH_IMAGE_PATH, OUTPUT_DIR, TURTLE_PATH
from graph_builder import build_graph
from graph_ops import run as run_point3
from sparql_queries import run as run_point4
from external_link import run as run_point5
from validation import print_report
from visualization import visualize


# Entry point: runs lab steps 2-5 and the visualization one after another.
# Input:  none
# Output: none (creates files in output/ and prints results)
def main() -> None:
    OUTPUT_DIR.mkdir(exist_ok=True)

    # Step 2: build the graph, save it, check it against the requirements
    graph = build_graph()
    graph.serialize(destination=str(TURTLE_PATH), format="turtle")
    print_report(graph)
    print("==================================================================================================================")
    # Step 3: two formats, read + edit, triple output, entity description
    run_point3(graph)
    print("==================================================================================================================")
    # Step 4: SPARQL queries against the saved Turtle file
    run_point4()
    print("==================================================================================================================")
    # Step 5: owl:sameAs links to Wikidata and the federated query
    run_point5()

    # Last: save the PNG and open the interactive window
    visualize(graph, GRAPH_IMAGE_PATH)
    print(f"Saved: {TURTLE_PATH.name}, {GRAPH_IMAGE_PATH.name} (folder {OUTPUT_DIR.name}/)")


if __name__ == "__main__":
    main()