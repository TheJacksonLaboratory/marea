import unittest
from os import makedirs
from scripts.filter_abstracts import PMID_INDEX, extract_descriptors, extract_keywords, \
    find_relevant_abstracts, is_relevant
from scripts.query_mesh import merge_descendants


class FilterAbstractsTestCase(unittest.TestCase):

    def test_extract_descriptors(self):
        descriptor_str = """D000310 Adrenal Gland Neoplasms N | D000311 Adrenal 
        Glands N | D000328 Adult N | D002404 Catheterization Y | D006801 
        Humans N | D006977 Hypertension, Renal N | D010690 Phlebography Y | 
        D012082 Renal Veins Y | D012083 Renin N"""
        expected = {'D000310': False, 'D000311': False, 'D000328': False,
                    'D002404': True, 'D006801': False, 'D006977': False,
                    'D010690': True, 'D012082': True, 'D012083': False}
        self.assertEqual(expected, extract_descriptors(descriptor_str),
                         'Extracted descriptors do not match expected.')

    def test_extract_keywords(self):
        keyword_str = 'Aging-related tau astrogliopathy (ARTAG) Y | Astrocytes N ' +\
                      '| Atypical Alzheimer disease N | Clinical heterogeneity N | Tau N'
        expected = {'aging-related tau astrogliopathy (artag)': True,
                    'astrocytes': False, 'atypical alzheimer disease': False,
                    'clinical heterogeneity': False, 'tau': False}
        self.assertEqual(expected, extract_keywords(keyword_str),
                         'Extracted keywords do not match expected.')

    def test_is_relevant(self):
        abs_dict = {'D000855': True, 'D000073496': False, 'D010591': False,
                    'D003638': False, 'D037061': True}
        desired0 = {'D000855', 'D010591', 'D020385', 'D060486'}
        desired1 = {'D010591', 'D020385', 'D060486'}
        desired2 = {'D020385', 'D060486'}
        self.assertIs(True, is_relevant(abs_dict, desired0, True),
                      'Should be relevant with one major topic.')
        self.assertIs(True, is_relevant(abs_dict, desired0, False),
                      'Should be relevant with two topics, one major one not.')
        self.assertIs(False, is_relevant(abs_dict, desired1, True),
                      'Should be not relevant, no matching major topic.')
        self.assertIs(True, is_relevant(abs_dict, desired1, False),
                      'Should be relevant with one topic, not major.')
        self.assertIs(False, is_relevant(abs_dict, desired2, True),
                      'Should be not relevant, no overlap of (major) topics.')
        self.assertIs(False, is_relevant(abs_dict, desired2, False),
                      'Should be not relevant, no overlap of (any) topics.')
        search_set = {'neoplasm, breast', 'breast neoplasms', 'breast neoplasm',
                      'unilateral breast neoplasms', 'breast neoplasm, unilateral',
                      'breast neoplasms, unilateral', 'breast carcinoma in situ',
                      'carcinoma, ductal, breast', 'carcinomas, lobular',
                      'lobular carcinomas', 'lobular carcinoma',
                      'carcinoma, lobular', 'breast neoplasms, male',
                      'male breast neoplasm', 'breast neoplasm, male',
                      'neoplasm, male breast', 'inflammatory breast neoplasms',
                      'neoplasms, inflammatory breast',
                      'breast neoplasms, inflammatory',
                      'breast neoplasm, inflammatory', 'inflammatory breast neoplasm',
                      'neoplasm, inflammatory breast',
                      'hereditary breast and ovarian cancer syndrome',
                      'triple negative breast neoplasms'}
        kw0 = {'breast carcinoma in situ': False, 'intraductal papilloma': False,
               'nipple discharge': False}
        kw1 = {'breast neoplasms': True, 'oestrogen receptors': True,
               'signal transduction': True}
        kw2 = {'breast cancer': False, 'proteomic': False,
               'triorganotin isothiocyanates': False, 'vimentin': False,
               'itraq': False}
        kw3 = {'breast cancer': False, 'case report': False,
               'gastrointestinal metastasis': False,
               'intussusception': False, 'invasive lobular carcinoma': False}
        self.assertIs(True, is_relevant(kw0, search_set, False),
                      "Should be relevant: 'breast carcinoma in situ'.")
        self.assertIs(True, is_relevant(kw1, search_set, False),
                      "Should be relevant: 'breast neoplasms'.")
        self.assertIs(False, is_relevant(kw2, search_set, False),
                      "Should not be relevant: 'breast cancer' does not match.")
        self.assertIs(False, is_relevant(kw3, search_set, False),
                      "Should not be relevant: 'invasive lobular carcinoma' does not match.")
        self.assertIs(False, is_relevant(kw0, search_set, True),
                      "Should not be relevant: no major topic keywords.")
        self.assertIs(True, is_relevant(kw1, search_set, True),
                      "Should be relevant: 'breast neoplasms' major topic.")
        self.assertIs(False, is_relevant(kw2, search_set, True),
                      "Should not be relevant: no major topic keywords.")
        self.assertIs(False, is_relevant(kw3, search_set, True),
                      "Should not be relevant: no major topic keywords.")

    def test_find_relevant_abstracts(self):
        test_filename = 'test_abstracts'
        input_dir = 'testdata/pubmed_txt/'
        output_dir = 'testdata/pubmed_rel/'
        makedirs(output_dir, exist_ok=True)
        test_params = [
            'D005796-D009369-D037102',
            'D009369-D037102',
            'D005796',
            'D009369',
            'D037102'
        ]
        relevant_pmids = {
            'D005796-D009369-D037102':
                ['273474', '273475', '273632', '273634', '274699', '274701',
                 '274703', '274705', '274710', '274713', '274714', '274718',
                 '274719', '274720', '274721'],
            'D005796-D009369-D037102-m':
                ['274699', '274703', '274705', '274710', '274714', '274719',
                 '274720', '274721'],
            'D009369-D037102':
                ['273474', '273475', '273632', '273634', '274699', '274705',
                 '274718', '274721'],
            'D009369-D037102-m':
                ['274699', '274705', '274721'],
            'D005796':
                ['274701', '274703', '274710', '274713', '274714', '274719',
                 '274720'],
            'D005796-m':
                ['274703', '274710', '274714', '274719', '274720'],
            'D009369':
                ['273474', '273475', '273632', '273634', '274718'],
            'D009369-m': [],
            'D037102':
                ['274699', '274705', '274721'],
            'D037102-m':
                ['274699', '274705', '274721'],
        }
        for params in test_params:
            descriptors = params.split('-')
            desired = merge_descendants(descriptors)
            for major in (False, True):
                pmid_key = params + '-m' if major else params
                find_relevant_abstracts(input_dir + test_filename + '.txt',
                                        output_dir, major, desired)
                with open(output_dir + test_filename + '_relevant.tsv') as outfile:
                    output_pmids = [line.split()[PMID_INDEX] for line in outfile]
                self.assertEqual(relevant_pmids[pmid_key], output_pmids,
                                 'Incorrect PMIDs for ' + pmid_key)


if __name__ == '__main__':
    unittest.main()
