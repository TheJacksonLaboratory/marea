import unittest
import nlp_utils as nl

class NlpUtilsTestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        nl.nltk_setup('testdata/nltk_data/')

    def test_remove_stopwords(self):
        # a sentence after concept replacement
        before = ''.join(['The inhibition of binding for  NCBIGene106478911  ',
                          'and DHT by  NCBIGene106478911 ,  MESHD013739  (T),',
                          '  MESHD013196 , dehydroepiandosterone (DHEA),  ',
                          'MESHD019314  ( NCBIGene6822 ),  MESHD000735  (A) ',
                          'and 5-androstene-3beta, 17beta-diol (Adiol) was ',
                          'tested with the use of  MESHD003911 -coated charcoal',
                          ' separation of bound and free  NCBIGene106478911 , ',
                          'respectively, and  MESHD013196 .'])
        # remove_stop_words calls nltk.word_tokenize, which adds space around
        # punctuation.
        after = ''.join(['The inhibition binding NCBIGene106478911 ',
                         'DHT NCBIGene106478911 , MESHD013739 ( T ) ,',
                         ' MESHD013196 , dehydroepiandosterone ( DHEA ) , ',
                         'MESHD019314 ( NCBIGene6822 ) , MESHD000735 ( A ) ',
                         '5-androstene-3beta , 17beta-diol ( Adiol ) ',
                         'tested use MESHD003911 coated charcoal ',
                         'separation bound free NCBIGene106478911 , ',
                         'respectively , MESHD013196 .'])
        self.assertEqual(after, nl.remove_stop_words(before))
        before = ''.join(['Outcomes of unrelated cord blood transplantation in ',
                          'pediatric recipients. We report results of unrelated',
                          'cord blood transplants (UCBT) in 29 pediatric ',
                          'recipients in one center and the risk factors ',
                          'associated with survival. Median age: 9 years ',
                          '(0.5-20); diagnosis: ALL (9), MESHD015470 (4), ',
                          'MESHD015464 (1), MESHD006816 (3), HLH (1), ',
                          'MESHD008228 (3), NCBIGene9253 (2); B-thal (1), ',
                          'FA (1), FEL (1), Krabbe (1), WAS (1), SAA (1).'])
        after = ''.join(['Outcomes unrelated cord blood transplantation ',
                         'pediatric recipients . We report results unrelated',
                         'cord blood transplants ( UCBT ) 29 pediatric ',
                         'recipients one center risk factors ',
                         'associated survival . Median age : 9 years ',
                         '( 0.5-20 ) ; diagnosis : ALL ( 9 ) , MESHD015470 ( 4 ) , ',
                         'MESHD015464 ( 1 ) , MESHD006816 ( 3 ) , HLH ( 1 ) , ',
                         'MESHD008228 ( 3 ) , NCBIGene9253 ( 2 ) ; B-thal ( 1 ) , ',
                         'FA ( 1 ) , FEL ( 1 ) , Krabbe ( 1 ) , WAS ( 1 ) , SAA ( 1 ) .'])
        self.assertEqual(after, nl.remove_stop_words(before))

    def test_remove_edge_hyphen(self):
        self.assertEqual('REP-b', nl.remove_edge_hyphen('-REP-b'))
        self.assertEqual('anti', nl.remove_edge_hyphen('anti-'))
        self.assertEqual('NO', nl.remove_edge_hyphen('-NO-'))
        self.assertEqual('group', nl.remove_edge_hyphen('group'))
        self.assertEqual('-10', nl.remove_edge_hyphen('-10'))


if __name__ == '__main__':
    unittest.main()
