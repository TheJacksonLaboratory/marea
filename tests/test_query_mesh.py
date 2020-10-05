import unittest
from scripts.query_mesh import get_descendants, get_all_labels, \
    get_preferred_label, merge_descendants


class QueryMeshTestCase(unittest.TestCase):

    def test_get_all_labels(self):
        expected = {'Adenoma, Chromophobe', 'Adenomas, Chromophobe',
                    'Chromophobe Adenomas', 'Chromophobe Adenoma'}
        self.assertEqual(expected, get_all_labels('D000238'),
                         'Labels for Adenoma, Chromophobe')

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

    def test_get_preferred_label(self):
        expected = 'Adrenal Rest Tumor'
        self.assertEqual(expected, get_preferred_label('D000314'),
                         'Preferred label for D000314 should be Adrenal Rest Tumor')
        expected = 'Mammary Analogue Secretory Carcinoma'
        self.assertEqual(expected, get_preferred_label('D000069295'),
                         'Preferred label for D000069295 should be Mammary Analogue Secretory Carcinoma')

    def test_merge_descendants(self):
        ancestors = ['D016543', 'D011118', 'D008175']
        expected = {
            'D000072481',
            'D000077192',
            'D000080443',
            'D001932',
            'D001984',
            'D002282',
            'D002283',
            'D002289',
            'D002528',
            'D002551',
            'D007029',
            'D008175',
            'D008577',
            'D008579',
            'D010178',
            'D010871',
            'D010911',
            'D011088',
            'D011118',
            'D011130',
            'D013120',
            'D015173',
            'D015174',
            'D015192',
            'D016080',
            'D016543',
            'D016545',
            'D018202',
            'D018306',
            'D020288',
            'D020295',
            'D020863',
            'D047868',
            'D054975',
            'D055613',
            'D055752',
            'D055756',
            'D056364'
        }
        actual = merge_descendants(ancestors)
        self.assertEqual(38, len(actual),
                         'Dictionary of descendants for D016543, D011118, D008175 has incorrect length.')
        self.assertEqual(expected, actual.keys(),
                         'Set of descendant descriptors for D016543, D011118, D008175 does not match.')
        expected = {
            'D000077207': {'Chondrosarcoma, Clear Cell'},
            'D002813': {'Chondrosarcoma', 'Chondrosarcomas'},
            'D008444': {'Maxillary Sinus Neoplasm', 'Maxillary Sinus Neoplasms',
                        'Neoplasm, Maxillary Sinus'},
            'D009669': {'Neoplasm, Nose', 'Nose Neoplasm', 'Nose Neoplasms'},
            'D010255': {'Paranasal Sinus Neoplasm', 'Paranasal Sinus Neoplasms',
                        'Neoplasm, Paranasal Sinus'},
            'D018211': {'Chondrosarcoma, Mesenchymal', 'Chondrosarcomas, Mesenchymal',
                        'Mesenchymal Chondrosarcoma', 'Mesenchymal Chondrosarcomas'}
        }
        self.assertEqual(expected, merge_descendants(['D002813', 'D009669']),
                         'Merge of D002813 Chondrosarcoma and D009669 Nose Neoplasms')


if __name__ == '__main__':
    unittest.main()
