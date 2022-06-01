import ast
import os
import unittest

import pandas as pd
from automatchnames import get_accepted_info_from_names_in_column
from clean_plant_occurrences import read_occurences_and_output_acc_names, \
    find_whether_occurrences_in_native_or_introduced_regions, get_tdwg_regions_for_occurrences
from pkg_resources import resource_filename
from tqdm import tqdm

from cleaning_logan_plant_occurrences import logan_final_occurrence_output_csv, clean_occurrences_by_tdwg_regions
from large_file_storage import plant_occurences
from logan_wcsp_distributions import logan_distributions_csv

input_test_dir = resource_filename(__name__, 'test_inputs')
test_output_dir = resource_filename(__name__, 'test_outputs')

_final_cleaned_output_df = pd.read_csv(logan_final_occurrence_output_csv, index_col=0)
_native_cleaned_output_df = pd.read_csv(
    os.path.join(plant_occurences, 'outputs', 'logan_final_native_cleaned_occurrences.csv'), index_col=0)


class MyTestCase(unittest.TestCase):

    def test_clean_output_for_standard_criteria(self):
        def test_examples(occ_df: pd.DataFrame, tag: str):
            dups = occ_df[occ_df.duplicated(subset=['gbifID'])]
            self.assertEqual(len(dups.index), 0)

            # Coord uncertainty 20000
            print('coord uncertainty clean')
            uncertain = occ_df[occ_df['coordinateUncertaintyInMeters'] > 20000]
            uncertain.to_csv(os.path.join(test_output_dir, tag + 'bad_coord_examples.csv'))
            # clim_occ_df = clim_occ_df[clim_occ_df['coordinateUncertaintyInMeters'] <= 20000]

            self.assertEqual(len(uncertain.index), 0)

            ## Years
            uncertain = occ_df[occ_df['year'] < 1945]
            uncertain.to_csv(os.path.join(test_output_dir, tag + 'bad_year_examples.csv'))
            self.assertEqual(len(uncertain.index), 0)
            ## 0 long and lat
            uncertain = occ_df[(occ_df['decimalLongitude'] == 0) & (occ_df['decimalLatitude'] == 0)]
            uncertain.to_csv(os.path.join(test_output_dir, tag + 'bad_zerolatlong_examples.csv'))
            self.assertEqual(len(uncertain.index), 0)
            uncertain = occ_df[(occ_df['decimalLongitude'] == occ_df['decimalLatitude'])]
            uncertain.to_csv(os.path.join(test_output_dir, 'bad_eqlatlong_examples.csv'))
            self.assertEqual(len(uncertain.index), 0)
            # na lat long
            uncertain = occ_df[(occ_df['decimalLongitude'].isna()) | (occ_df['decimalLatitude'].isna())]
            uncertain.to_csv(os.path.join(test_output_dir, tag + 'bad_nalatlong_examples.csv'))
            self.assertEqual(len(uncertain.index), 0)

            # na codes
            # uncertain = occ_df[(occ_df['countryCode'].isna())]
            # uncertain.to_csv(os.path.join(test_dir, tag+'bad_naccode_examples.csv'))

        test_examples(_final_cleaned_output_df, '')
        test_examples(_native_cleaned_output_df, 'native')

    def test_tdwg_regions_in_given_codes(self):
        # Test natives
        print('testing native tdwg3 codes')
        for idx, row in tqdm(_native_cleaned_output_df.iterrows(), total=_native_cleaned_output_df.shape[0],
                             desc="Searching 1", ascii=False, ncols=72):
            self.assertIn(row['tdwg3_region'], ast.literal_eval(row['native_tdwg3_codes']))

        print('testing native/introduced tdwg3 codes')
        for idx, row in tqdm(_final_cleaned_output_df.iterrows(), total=_final_cleaned_output_df.shape[0],
                             desc="Searching 2", ascii=False, ncols=72):
            native_intro_codes = ast.literal_eval(row['native_tdwg3_codes']) + ast.literal_eval(
                row['intro_tdwg3_codes'])
            self.assertIn(row['tdwg3_region'], native_intro_codes)

    def test_gbif_records_preserved(self):
        _standard_cleaned_csv = os.path.join(plant_occurences, 'outputs', 'standard_logan_cleaned_occurrences.csv')
        standard_cleaned_records = pd.read_csv(_standard_cleaned_csv)

        columns_to_check = ['gbifID', 'decimalLongitude', 'decimalLatitude', 'fullname']

        def tidy_df_to_match(df):
            new_df = df[columns_to_check]
            new_df.drop_duplicates(subset=['gbifID'], keep='first', inplace=True)
            new_df.set_index('gbifID', inplace=True)
            new_df.sort_index(ascending=True, inplace=True)
            return new_df

        standard_cleaned_records_in_native = tidy_df_to_match(standard_cleaned_records[
                                                                  standard_cleaned_records['gbifID'].isin(
                                                                      _native_cleaned_output_df['gbifID'].values)][
                                                                  columns_to_check])
        natives_with_basic_columns = tidy_df_to_match(_native_cleaned_output_df)

        print('testing:')
        print(standard_cleaned_records_in_native)
        print(natives_with_basic_columns)

        pd.testing.assert_frame_equal(standard_cleaned_records_in_native, natives_with_basic_columns)

        standard_cleaned_records_in_final = tidy_df_to_match(standard_cleaned_records[
                                                                 standard_cleaned_records['gbifID'].isin(
                                                                     _final_cleaned_output_df['gbifID'].values)][
                                                                 columns_to_check])
        final_with_basic_columns = tidy_df_to_match(_final_cleaned_output_df)

        print('testing:')
        print(standard_cleaned_records_in_final)
        print(final_with_basic_columns)
        pd.testing.assert_frame_equal(standard_cleaned_records_in_final, final_with_basic_columns)

    def test_more_with_introduced(self):
        self.assertGreaterEqual(_final_cleaned_output_df.shape[0], _native_cleaned_output_df.shape[0])


if __name__ == '__main__':
    unittest.main()
