import os

import pandas as pd
# Add progress bar to apply method
from clean_plant_occurrences import read_occurences_and_output_acc_names, clean_occurrences_by_tdwg_regions

from large_file_storage import plant_occurences
from logan_wcsp_distributions import logan_distributions_csv

_logan_standard_cleaned_csv = os.path.join(plant_occurences, 'outputs', 'standard_logan_cleaned_occurrences.csv')

logan_accepted_name_info_of_occurrences_csv = os.path.join(plant_occurences, 'outputs',
                                                     'standard_cleaned_logan_occurences_with_accepted_names.csv')

logan_final_occurrence_output_csv = os.path.join(plant_occurences, 'outputs', 'logan_final_cleaned_occurrences.csv')
_logan_final_native_occurrence_output_csv = os.path.join(plant_occurences, 'outputs', 'logan_final_native_cleaned_occurrences.csv')

families_in_occurrences = ['Loganiaceae']
def read_my_occs():

    standard_occ_df = pd.read_csv(_logan_standard_cleaned_csv)
    read_occurences_and_output_acc_names(standard_occ_df, logan_accepted_name_info_of_occurrences_csv,
                                         families_in_occurrences=families_in_occurrences)


def clean_my_occs():
    acc_occ_df = pd.read_csv(logan_accepted_name_info_of_occurrences_csv)
    print(f'given # of occurrences: {len(acc_occ_df.index)}')
    both = clean_occurrences_by_tdwg_regions(acc_occ_df, logan_distributions_csv, priority='both',
                                             output_csv=logan_final_occurrence_output_csv)
    print(f'# of native/introduced occurrences: {len(both.index)}')

    native = clean_occurrences_by_tdwg_regions(acc_occ_df, logan_distributions_csv, priority='native',
                                               output_csv=_logan_final_native_occurrence_output_csv)
    print(f'# of native occurrences: {len(native.index)}')


if __name__ == '__main__':
    # read_my_occs()
    clean_my_occs()
