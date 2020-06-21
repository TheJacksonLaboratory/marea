import unittest
from scripts.query_mesh import get_descendants, get_synonyms


class QueryMeshTestCase(unittest.TestCase):

    def test_get_descendants(self):
        expected = {
            'D005266': {'Femoral Neoplasm', 'Femoral Neoplasms',
                        'Neoplasm, Femoral', 'Neoplasms, Femoral'},
            'D007573': {'Jaw Neoplasm', 'Jaw Neoplasms', 'Neoplasm, Jaw'},
            'D008339': {'Mandibular Neoplasm', 'Mandibular Neoplasms',
                        'Neoplasm, Mandibular', 'Neoplasms, Mandibular'},
            'D008441': {'Maxillary Neoplasm', 'Maxillary Neoplasms',
                        'Neoplasm, Maxillary', 'Neoplasms, Maxillary'},
            'D009669': {'Neoplasm, Nose', 'Nose Neoplasm', 'Nose Neoplasms'},
            'D009918': {'Neoplasm, Orbital', 'Neoplasms, Orbital',
                        'Orbital Neoplasm', 'Orbital Neoplasms'},
            'D010157': {'Neoplasm, Palatal', 'Neoplasms, Palatal',
                        'Palatal Neoplasm', 'Palatal Neoplasms'},
            'D012888': {'Skull Neoplasms'},
            'D013125': {'Neoplasm, Spinal', 'Neoplasms, Spinal',
                        'Spinal Neoplasm', 'Spinal Neoplasms'},
            'D019292': {'Skull Base Neoplasms'},
            'D050398': {'Adamantinoma', 'Adamantinomas'}
        }
        self.assertEqual(expected, get_descendants('D001859'),
                         'Descendants of Bone Neoplasms')

    def test_get_synonyms(self):
        expected = {'Adenoma, Chromophobe', 'Adenomas, Chromophobe',
                    'Chromophobe Adenomas', 'Chromophobe Adenoma'}
        self.assertEqual(expected, get_synonyms('D000238'),
                         'Labels for Adenoma, Chromophobe')


if __name__ == '__main__':
    unittest.main()
