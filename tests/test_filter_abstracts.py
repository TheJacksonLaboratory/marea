import unittest
from filter_abstracts import extract_descriptors, get_outfilename, is_relevant, merge_descendants

class FilterAbstractsTestCase(unittest.TestCase):

    def test_extract_descriptors(self):
        descriptor_str = """D000310 Adrenal Gland Neoplasms N | D000311 Adrenal 
        Glands N | D000328 Adult N | D002404 Catheterization Y | D006801 
        Humans N | D006977 Hypertension, Renal N | D010690 Phlebography Y | 
        D012082 Renal Veins Y | D012083 Renin N"""
        expected = {'D000310': False, 'D000311': False, 'D000328': False,
                    'D002404': True, 'D006801': False, 'D006977': False,
                    'D010690': True, 'D012082': True, 'D012083': False}
        self.assertEqual(extract_descriptors(descriptor_str), expected,
                         'Extracted descriptors do not match expected.')

    def test_get_outfilename(self):
        out_filename = get_outfilename('../downloads/pubmed/pubmed20n0007.txt')
        self.assertEqual(out_filename, 'pubmed20n0007_relevant.txt',
                         out_filename + ' does not match expected string.')

    def test_is_relevant(self):
        abs_dict = {'D000855': True, 'D000073496': False, 'D010591': False,
                    'D003638': False, 'D037061': True}
        desired0 = ['D000855', 'D010591', 'D020385', 'D060486']
        desired1 = ['D010591', 'D020385', 'D060486']
        desired2 = ['D020385', 'D060486']
        self.assertIs(is_relevant(abs_dict, desired0, True), True,
                         'Should be relevant with one major topic.')
        self.assertIs(is_relevant(abs_dict, desired0, False), True,
                         'Should be relevant with two topics, one major one not.')
        self.assertIs(is_relevant(abs_dict, desired1, True), False,
                         'Should be not relevant, no matching major topic.')
        self.assertIs(is_relevant(abs_dict, desired1, False), True,
                         'Should be relevant with one topic, not major.')
        self.assertIs(is_relevant(abs_dict, desired2, True), False,
                         'Should be not relevant, no overlap of (major) topics.')
        self.assertIs(is_relevant(abs_dict, desired2, False), False,
                         'Should be not relevant, no overlap of (any) topics.')

    def test_merge_descendants(self):
        ancestors = ['D016543', 'D011118', 'D008175']
        expected = [
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
        ]
        actual = merge_descendants(ancestors)
        self.assertEqual(len(actual), 38, 'List of descendants has incorrect length.')
        self.assertEqual(actual, expected, 'List of descendants does not match.')


if __name__ == '__main__':
    unittest.main()
