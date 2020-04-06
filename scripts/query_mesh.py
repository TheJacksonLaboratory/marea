from SPARQLWrapper import SPARQLWrapper, RDFXML
from rdflib import Graph

sparql = SPARQLWrapper("http://id.nlm.nih.gov/mesh/sparql")
sparql.setQuery("""
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX meshv: <http://id.nlm.nih.gov/mesh/vocab#>
    PREFIX mesh: <http://id.nlm.nih.gov/mesh/>

    CONSTRUCT {
    ?descriptor rdfs:label ?label
    }
    WHERE {
    mesh:D013568 meshv:treeNumber ?treeNum .
    ?childTreeNum meshv:parentTreeNumber+ ?treeNum .
    ?descriptor meshv:treeNumber ?childTreeNum .
    ?descriptor rdfs:label ?label .
    }
""")

sparql.setReturnFormat(RDFXML)
results = sparql.queryAndConvert()
g = Graph()
g.parse(data=results, format='xml')
print(len(g))

descriptors = {}
for s, p, o in g:
    descriptors[o.toPython()] = s.toPython()

# Print the descriptors sorted by their labels
[ print("{}\t{}".format(label, descriptor)) for (descriptor, label) in sorted(descriptors.items()) ]
