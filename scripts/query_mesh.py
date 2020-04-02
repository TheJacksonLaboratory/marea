from SPARQLWrapper import SPARQLWrapper, JSON

sparql = SPARQLWrapper("http://id.nlm.nih.gov/mesh/sparql")
sparql.setQuery("""
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX meshv: <http://id.nlm.nih.gov/mesh/vocab#>
    PREFIX mesh: <http://id.nlm.nih.gov/mesh/>
    
    SELECT DISTINCT ?descriptor ?label
    FROM <http://id.nlm.nih.gov/mesh>

    WHERE {
    mesh:D009369 meshv:treeNumber ?treeNum .
    ?childTreeNum meshv:parentTreeNumber+ ?treeNum .
    ?descriptor meshv:treeNumber ?childTreeNum .
    ?descriptor rdfs:label ?label .
    }

    ORDER BY ?label
""")

sparql.setReturnFormat(JSON)
results = sparql.query().convert()
# print(results.serialize(format='xml'))
for result in results["results"]["bindings"]:
    print("{}\t{}".format(result["descriptor"]["value"], result["label"]["value"]))
