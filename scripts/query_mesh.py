import warnings
from collections import defaultdict
from SPARQLWrapper import SPARQLWrapper, RDFXML, JSON
from rdflib import Graph
from typing import Dict, List, Set


def get_descendants(ancestor: str) -> Dict[str, Set[str]]:
    """
    Return all descendants of the specified MeSH descriptor.
    :param ancestor: MeSH identifier (e.g., 'D013568')
    :return: dictionary mapping MeSH identifier of each descendant of ancestor
             to a set containing the preferred label and all synonyms for
             that identifier
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
    descriptor_dict = defaultdict(set)
    for descriptor, label in descriptor_tuples:
        descriptor_dict[descriptor].add(label)
    # for simplicity, convert defaultdict to ordinary dictionary
    return dict(descriptor_dict)


def get_synonyms(descriptor: str) -> Set[str]:
    """
    Return all the labels, preferred and alternate, for specified MeSH descriptor.
    :param descriptor: MeSH identifier (e.g., 'D009918')
    :return: set of strings
    """
    sparql = SPARQLWrapper("http://id.nlm.nih.gov/mesh/sparql")
    sparql.setQuery("""
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX meshv: <http://id.nlm.nih.gov/mesh/vocab#>
        PREFIX mesh: <http://id.nlm.nih.gov/mesh/>
        SELECT DISTINCT ?label
        WHERE {
            mesh:"""
                    + descriptor +
                    """ meshv:preferredTerm ?term .
                    { mesh:""" + descriptor + """ rdfs:label ?label } UNION
                    { ?term meshv:altLabel ?label } .
        }
        """)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()

    resultset = set()
    for result in results["results"]["bindings"]:
        resultset.add(result["label"]["value"])
    return resultset


def merge_descendants(ancestors: List[str]) -> Dict[str, Set[str]]:
    """
    Find all descendants of ancestor descriptors in MeSH classification tree.
    Return dictionary including all ancestors and their descendants.
    :param ancestors: list of MeSH descriptors
    :return: dictionary mapping the MeSH identifier for each ancestor and
             each of its descendants to a set containing the preferred
             label and all synonyms for that identifier
    """
    merge_dict = {}
    for descriptor in ancestors:
        merge_dict.update(get_descendants(descriptor))
        merge_dict[descriptor] = get_synonyms(descriptor)
    return merge_dict


def main():
    # D000238 is for Adenoma, Chromophobe
    print(get_synonyms('D000238'))
    # D009369 is for Neoplasm
    all_descendants = merge_descendants(['D009369'])
    print('\nSize of return set: {}'.format(len(all_descendants)))
    # Print the descriptors sorted by MeSH identifier
    for key, value in sorted(all_descendants.items()):
        print('{}\t'.format(key), end='')
        print(*sorted(value), sep='; ')


if __name__ == '__main__':
    main()
