import warnings
from collections import defaultdict
from SPARQLWrapper import SPARQLWrapper, RDFXML
from rdflib import Graph


def get_descendants(ancestor):
    """
    Return all descendants of the specified MeSH descriptor (e.g.,
    'D013568').
    :param ancestor:  MeSH descriptor for which we want all descendants
    :return: dictionary mapping from MeSH identifier to the corresponding
             label for all descendants of ancestor
    """
    sparql = SPARQLWrapper("http://id.nlm.nih.gov/mesh/sparql")
    sparql.setQuery("""
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX meshv: <http://id.nlm.nih.gov/mesh/vocab#>
        PREFIX mesh: <http://id.nlm.nih.gov/mesh/>

        CONSTRUCT {
            ?descriptor meshv:altLabel ?label
        }
        WHERE {
            SELECT DISTINCT ?descriptor ?label
            WHERE {
                mesh:"""
                    + ancestor +
                    """ meshv:treeNumber ?treeNum .
                    ?childTreeNum meshv:parentTreeNumber+ ?treeNum .
                    ?descriptor meshv:treeNumber ?childTreeNum .
                    ?descriptor meshv:preferredTerm ?term .
                    { ?descriptor rdfs:label ?label } UNION
                    { ?term meshv:altLabel ?label } .
            }
        }
        """)

    sparql.setReturnFormat(RDFXML)
    # Suppress the warning
    # "RuntimeWarning: unknown response content type 'text/plain' returning raw response..."
    # that occurs when the result of the query is returned from NLM; I think
    # there is an error in the content type field of the response that cannot
    # be fixed from client side.
    warnings.simplefilter("ignore")
    results = sparql.queryAndConvert()
    # Re-enable warnings.
    warnings.simplefilter("default")
    g = Graph()
    g.parse(data=results, format='xml')

    # Create dictionary mapping from MeSH identifier to label for each descriptor.
    # Use the split function to chop off the prefix 'http://id.nlm.nih.gov/mesh/'
    # from each identifier.
    descriptor_tuples = {(s.toPython().split('/')[-1], o.toPython()) for s, p, o in g}
    # print(len(descriptors))
    # i = 0
    # for (identifier, label) in sorted(descriptors):
    #     if i > 100:
    #         break
    #     print('{}\t{}'.format(identifier, label))
    #     i += 1
    descriptor_dict = defaultdict(set)
    for descriptor, label in descriptor_tuples:
        descriptor_dict[descriptor].add(label)

    # for d in descriptors:
    #     descriptor_labels[d.toPython().split('/')[-1]] = {o.toPython() for o, p, o in g}
    return descriptor_dict


def main():
    # D009369 is for Neoplasm
    all_descendants = get_descendants('D009369')
    print('Size of return set: {}'.format(len(all_descendants)))
    # Print the descriptors sorted by their labels
    # for (identifier, label) in sorted(all_descendants.items(),
    #                                   key=lambda item: item[1]):
    for key, value in sorted(all_descendants.items()):
        print('{}\t{}'.format(key, value))


if __name__ == '__main__':
    main()
