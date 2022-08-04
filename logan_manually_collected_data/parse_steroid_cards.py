import os

import pandas as pd

from logan_manually_collected_data import logan_trait_parsing_output_path, logan_encoded_traits_csv

logan_steroid_hits_manual_output_csv = os.path.join(logan_trait_parsing_output_path, 'logan_steroids_manual.csv')
logan_cardenolide_hits_manual_output_csv = os.path.join(logan_trait_parsing_output_path,
                                                        'logan_cardenolides_manual.csv')


def get_manual_steroid_hits():
    manual_df = pd.read_csv(logan_encoded_traits_csv, index_col=0
                            )
    # Get steroids
    steroid_hits = manual_df[manual_df['Steroids'] == 1]

    steroid_hits['Source'] = 'Manual'

    steroid_hits.to_csv(logan_steroid_hits_manual_output_csv)


def get_manual_cardenolide_hits():
    manual_df = pd.read_csv(logan_encoded_traits_csv, index_col=0
                            )
    # Get cardenolides
    cardenolide_hits = manual_df[manual_df['Cardenolides'] == 1]

    cardenolide_hits['Source'] = 'Manual'

    cardenolide_hits.to_csv(logan_cardenolide_hits_manual_output_csv)


def main():
    get_manual_steroid_hits()
    get_manual_cardenolide_hits()


if __name__ == '__main__':
    main()
