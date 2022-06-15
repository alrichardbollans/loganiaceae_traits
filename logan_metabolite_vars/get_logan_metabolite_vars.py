import os
import pandas as pd
from automatchnames import remove_whitespace_at_beginning_and_end, get_accepted_info_from_names_in_column
from pkg_resources import resource_filename
from powo_searches import search_powo
from taxa_lists import get_all_taxa

from metabolite_searches import get_metabolites_for_taxa, output_alkaloids_from_metabolites, get_compound_hits_for_taxa, \
    get_antibac_metabolite_hits_for_taxa, recheck_taxa, output_steroids_from_metabolites, \
    output_cardenolides_from_metabolites
from cleaning import compile_hits

# from logan_manually_collected_data import logan_steroid_hits_manual_output_csv, \
#     logan_cardenolide_hits_manual_output_csv, logan_alk_hits_manual_output_csv
from logan_manually_collected_data import logan_alk_hits_manual_output_csv

_temp_output_path = resource_filename(__name__, 'temp_outputs')
_logan_steroid_hits_knapsack_output_csv = os.path.join(_temp_output_path, 'logan_steroid_knapsack.csv')
_logan_cardenolide_hits_knapsack_output_csv = os.path.join(_temp_output_path, 'logan_card_knapsack.csv')
_logan_alk_hits_knapsack_output_csv = os.path.join(_temp_output_path, 'logan_alk_knapsack.csv')
_powo_search_alks_temp_output_accepted_csv = os.path.join(_temp_output_path, 'powo_alks.csv')

_output_path = resource_filename(__name__, 'outputs')

logan_metabolites_output_csv = os.path.join(_output_path, 'logan_metabolites.csv')
_logan_alks_output_csv = os.path.join(_output_path, 'logan_alkaloids.csv')
_logan_steroid_output_csv = os.path.join(_output_path, 'logan_steroids.csv')
_logan_cardenolide_output_csv = os.path.join(_output_path, 'logan_cardenolides.csv')

logan_alkaloid_hits_output_csv = os.path.join(_output_path, 'logan_alkaloid_hits.csv')
logan_steroid_hits_output_csv = os.path.join(_output_path, 'logan_steroid_hits.csv')
logan_cardenolide_hits_output_csv = os.path.join(_output_path, 'logan_cardenolides_hits.csv')

logan_antibac_metabolite_hits_output_csv = os.path.join(_output_path, 'logan_antibac_metabolites_hits.csv')
_check_output_csv = os.path.join(_output_path, 'rechecked_taxa.csv')

logan_families_of_int = ['Loganiaceae']


def get_logan_metabolites():
    data = get_all_taxa(families_of_interest=logan_families_of_int, accepted=True)

    ranks_to_use = ["Species", "Variety", "Subspecies"]

    taxa = data.loc[data["rank"].isin(ranks_to_use)]

    taxa_list = taxa["taxon_name"].values

    get_metabolites_for_taxa(taxa_list, output_csv=logan_metabolites_output_csv)


def get_logan_alkaloid_hits():
    # Knapsack
    metabolites_to_check = pd.read_csv(logan_metabolites_output_csv).columns.tolist()

    alks_df = output_alkaloids_from_metabolites(metabolites_to_check, _logan_alks_output_csv)

    logan_metas_data = pd.read_csv(logan_metabolites_output_csv)
    get_compound_hits_for_taxa('alks', logan_metas_data, alks_df, _logan_alk_hits_knapsack_output_csv,
                               fams=logan_families_of_int)

    # POWO
    try:
        search_powo(['alkaloid'],
                    _powo_search_alks_temp_output_accepted_csv, families_of_interest=logan_families_of_int,
                    filters=['species', 'infraspecies'])
    except KeyError as e:
        print(f'KeyError: {e}')
        print('Key error likely raised due to no matches being found')

    # Compile
    knapsack_alk_hits = pd.read_csv(_logan_alk_hits_knapsack_output_csv)
    manual_alk_hits = pd.read_csv(logan_alk_hits_manual_output_csv)

    try:
        powo_hits = pd.read_csv(_powo_search_alks_temp_output_accepted_csv)

        compile_hits([manual_alk_hits, knapsack_alk_hits, powo_hits], logan_alkaloid_hits_output_csv)
    except FileNotFoundError:
        compile_hits([manual_alk_hits, knapsack_alk_hits], logan_alkaloid_hits_output_csv)


def get_logan_knapsack_steroid_hits():
    metabolites_to_check = pd.read_csv(logan_metabolites_output_csv).columns.tolist()

    steroid_df = output_steroids_from_metabolites(metabolites_to_check, _logan_steroid_output_csv)

    logan_metas_data = pd.read_csv(logan_metabolites_output_csv)
    get_compound_hits_for_taxa('steroids', logan_metas_data, steroid_df, _logan_steroid_hits_knapsack_output_csv,
                               fams=logan_families_of_int)


def get_logan_knapsack_cardenolide_hits():
    metabolites_to_check = pd.read_csv(logan_metabolites_output_csv).columns.tolist()

    card_df = output_cardenolides_from_metabolites(metabolites_to_check, _logan_cardenolide_output_csv)

    logan_metas_data = pd.read_csv(logan_metabolites_output_csv)
    get_compound_hits_for_taxa('cardenolides', logan_metas_data, card_df,
                               _logan_cardenolide_hits_knapsack_output_csv,
                               fams=logan_families_of_int)


def summarise_metabolites():
    metas_data = pd.read_csv(logan_metabolites_output_csv)
    summ = metas_data.describe()
    print(summ)
    worthwhile_metabolites = [x for x in summ.columns if summ[x]['mean'] > 0.001]
    print(worthwhile_metabolites)


def get_logan_antibac_metabolite_hits():
    all_metas_data = pd.read_csv(logan_metabolites_output_csv)
    get_antibac_metabolite_hits_for_taxa(all_metas_data, logan_antibac_metabolite_hits_output_csv,
                                         fams=logan_families_of_int)


def get_steroid_card_hits():
    get_logan_knapsack_steroid_hits()
    get_logan_knapsack_cardenolide_hits()

    manual_steroid_hits = pd.read_csv(logan_steroid_hits_manual_output_csv)
    knapsack_steroid_hits = pd.read_csv(_logan_steroid_hits_knapsack_output_csv)

    compile_hits([manual_steroid_hits, knapsack_steroid_hits], logan_steroid_hits_output_csv)

    manual_cardenolide_hits = pd.read_csv(logan_cardenolide_hits_manual_output_csv)
    knapsack_cardenolide_hits = pd.read_csv(_logan_cardenolide_hits_knapsack_output_csv)

    compile_hits([manual_cardenolide_hits, knapsack_cardenolide_hits], logan_cardenolide_hits_output_csv)


def main():
    # # # recheck_taxa(_check_output_csv)
    # summarise_metabolites()
    # get_logan_antibac_metabolite_hits()
    # get_logan_alkaloid_hits()
    get_logan_knapsack_cardenolide_hits()
    get_logan_knapsack_steroid_hits()
    #
    # get_steroid_card_hits()


if __name__ == '__main__':
    main()
