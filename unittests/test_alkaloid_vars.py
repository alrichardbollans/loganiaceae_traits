import unittest

import pandas as pd
from unit_test_methods import confirming_hits

from logan_metabolite_vars import logan_alkaloid_hits_output_csv



class MyTestCase(unittest.TestCase):
    def test_alk_hits(self):
        p = confirming_hits()
        hits = pd.read_csv(logan_alkaloid_hits_output_csv, index_col=0)
        p.confirm_hit('Strychnos spinosa', hits)
        p.confirm_no_hit('Srychnos spinosa', hits)
        p.confirm_knapsack_hit('Strychnos spinosa', hits,
                               ['Strychnine', 'Brucine N-oxide', 'Diaboline', 'Pseudobrucine'])

        p.confirm_knapsack_hit('Strychnos icaja', hits)

        p.confirm_hit('Strychnos vanprukii', hits)


if __name__ == '__main__':
    unittest.main()
