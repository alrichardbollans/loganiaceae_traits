import unittest

import pandas as pd

from getting_logan_malarial_regions import logan_taxa_in_malarial_countries_csv
from logan_wcsp_distributions import logan_distributions_csv


class MyTestCase(unittest.TestCase):
    def test_output_instances(self):
        distros_df = pd.read_csv(logan_distributions_csv, index_col=0)
        distros_df.set_index('kew_id', inplace=True)


        self.assertEqual("['BZL']", distros_df.at['324568-2', 'native_tdwg3_codes'], msg=f'324568-2')
        self.assertEqual("['BZE']", distros_df.at['546920-1', 'native_tdwg3_codes'], msg=f'546920-1')

    def test_malarial_instances(self):
        malarial_taxa = pd.read_csv(logan_taxa_in_malarial_countries_csv)
        malarial_taxa_acc_ids = malarial_taxa['Accepted_ID'].to_list()
        print(malarial_taxa_acc_ids)
        non_malarial_ids = ['77197401-1', '21200-2', '77167599-1', '102673-1']

        for id in non_malarial_ids:
            self.assertNotIn(id,malarial_taxa_acc_ids)

        malarial_ids = ['324568-2','546920-1']

        for id in malarial_ids:
            self.assertIn(id,malarial_ids)
if __name__ == '__main__':
    unittest.main()
