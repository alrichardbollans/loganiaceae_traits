import os

import pandas as pd

from logan_manually_collected_data import logan_trait_parsing_output_path, logan_encoded_traits_csv

logan_alk_hits_manual_output_csv = os.path.join(logan_trait_parsing_output_path, 'logan_alks_manual.csv')

def get_manual_alk_hits():
    manual_df = pd.read_csv(logan_encoded_traits_csv,index_col=0
                            )
    # Get steroids
    alk_hits = manual_df[manual_df['Alkaloids'] == 1]

    alk_hits['Source'] = 'Manual'

    alk_hits.to_csv(logan_alk_hits_manual_output_csv)

def main():
    get_manual_alk_hits()


if __name__ == '__main__':
    main()