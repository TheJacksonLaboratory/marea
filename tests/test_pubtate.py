import unittest
from scripts.pubtate import fix_concept_ids


class MyTestCase(unittest.TestCase):

    def test_fix_concept_ids(self):
        self.assertEqual(' NCBIGene_1019  NCBIGene_1021 ',
                         fix_concept_ids('Gene', '1019;1021'),
                         'Unexpected result for multiple gene ids separated by semicolon.')
        self.assertEqual(' MESH_D012175 ', fix_concept_ids('Disease', 'MESH:D012175'),
                         'Unexpected result for MeSH id.')


if __name__ == '__main__':
    unittest.main()
