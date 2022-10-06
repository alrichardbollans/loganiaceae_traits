import os
import pandas as pd
from automatchnames import COL_NAMES

from pkg_resources import resource_filename
from powo_searches import search_powo
from taxa_lists import get_all_taxa

from metabolite_searches import get_metabolites_for_taxa, output_alkaloids_from_metabolites, get_compound_hits_for_taxa, \
    get_antibac_metabolite_hits_for_taxa, recheck_taxa, output_steroids_from_metabolites, \
    output_cardenolides_from_metabolites, get_antimalarial_metabolite_hits_for_taxa, \
    get_inactive_antimalarial_metabolite_hits_for_taxa
from cleaning import compile_hits, output_summary_of_hit_csv, compiled_sources_col

from logan_manually_collected_data import logan_alk_hits_manual_output_csv, logan_steroid_hits_manual_output_csv, \
    logan_cardenolide_hits_manual_output_csv

_temp_output_path = resource_filename(__name__, 'temp_outputs')
_logan_steroid_hits_knapsack_output_csv = os.path.join(_temp_output_path, 'logan_steroid_knapsack.csv')
_logan_cardenolide_hits_knapsack_output_csv = os.path.join(_temp_output_path, 'logan_card_knapsack.csv')
_logan_alk_hits_knapsack_output_csv = os.path.join(_temp_output_path, 'logan_alk_knapsack.csv')
_powo_search_alks_temp_output_accepted_csv = os.path.join(_temp_output_path, 'powo_alks.csv')

_output_path = resource_filename(__name__, 'outputs')

logan_metabolites_output_csv = os.path.join(_output_path, 'logan_metabolites.csv')
logan_accepted_metabolites_output_csv = os.path.join(_output_path, 'logan_accepted_metabolites.csv')
logan_unaccepted_metabolites_output_csv = os.path.join(_output_path, 'logan_unaccepted_metabolites.csv')
_logan_alks_output_csv = os.path.join(_output_path, 'logan_alkaloids.csv')
_logan_steroid_output_csv = os.path.join(_output_path, 'logan_steroids.csv')
_logan_cardenolide_output_csv = os.path.join(_output_path, 'logan_cardenolides.csv')

logan_alkaloid_hits_output_csv = os.path.join(_output_path, 'logan_alkaloid_hits.csv')
logan_steroid_hits_output_csv = os.path.join(_output_path, 'logan_steroid_hits.csv')
logan_cardenolide_hits_output_csv = os.path.join(_output_path, 'logan_cardenolides_hits.csv')

logan_antibac_metabolite_hits_output_csv = os.path.join(_output_path, 'logan_antibac_metabolites_hits.csv')
logan_antimal_metabolite_hits_output_csv = os.path.join(_output_path, 'logan_antimalarial_metabolites_hits.csv')
logan_inactive_antimal_metabolite_hits_output_csv = os.path.join(_output_path,
                                                                 'logan_inactive_antimalarial_metabolites_hits.csv')
_check_output_csv = os.path.join(_output_path, 'rechecked_taxa.csv')

logan_families_of_int = ['Loganiaceae']


def get_logan_metabolites():
    wcvp_data = get_all_taxa(families_of_interest=logan_families_of_int, ranks=["Species", "Variety", "Subspecies"])
    accepted_data = wcvp_data[wcvp_data['taxonomic_status'] == 'Accepted']
    unaccepted_data = wcvp_data[wcvp_data['taxonomic_status'] != 'Accepted']

    unaccepted_metabolites_df = get_metabolites_for_taxa(unaccepted_data["taxon_name"].values,
                                                         output_csv=logan_unaccepted_metabolites_output_csv)
    accepted_metabolites_df = get_metabolites_for_taxa(accepted_data["taxon_name"].values,
                                                       output_csv=logan_accepted_metabolites_output_csv)

    # accepted_metabolites_df = pd.read_csv(logan_accepted_metabolites_output_csv, index_col=0)
    # unaccepted_metabolites_df = pd.read_csv(logan_unaccepted_metabolites_output_csv, index_col=0)
    # Add new columns
    out_df = accepted_metabolites_df.copy()
    lower_cols = [x.lower() for x in out_df.columns]
    for c in unaccepted_metabolites_df.columns:
        if c.lower() not in lower_cols:
            out_df[c] = 0

    for acc_name in unaccepted_metabolites_df['Accepted_Name'].unique():
        print(acc_name)
        taxa_df = unaccepted_metabolites_df[unaccepted_metabolites_df['Accepted_Name'] == acc_name]
        for c in unaccepted_metabolites_df.columns:

            if c not in ['taxa'] + list(COL_NAMES.values()):
                x = taxa_df[c].max()
                if c not in out_df.columns:
                    # rename c to match out_df
                    # this is an issue caused by capitals in knapsack data.
                    # In future best to resolve this by lower casing all strings on import.
                    c = [x for x in out_df.columns if x.lower() == c.lower()][0]

                if c not in out_df.columns:
                    print(c)
                    raise ValueError

                if x == 1:
                    out_df.loc[out_df['Accepted_Name'] == acc_name, c] = 1

    out_df = out_df.fillna(0)
    out_df.to_csv(logan_metabolites_output_csv)


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


def get_logan_antimal_metabolite_hits():
    all_metas_data = pd.read_csv(logan_metabolites_output_csv)
    get_antimalarial_metabolite_hits_for_taxa(all_metas_data, logan_antimal_metabolite_hits_output_csv,
                                              fams=logan_families_of_int)


def get_logan_inactive_antimal_metabolite_hits():
    all_metas_data = pd.read_csv(logan_metabolites_output_csv)
    get_inactive_antimalarial_metabolite_hits_for_taxa(all_metas_data,
                                                       logan_inactive_antimal_metabolite_hits_output_csv,
                                                       fams=logan_families_of_int)


def get_steroid_card_hits():
    get_logan_knapsack_steroid_hits()
    get_logan_knapsack_cardenolide_hits()

    manual_steroid_hits = pd.read_csv(logan_steroid_hits_manual_output_csv)
    knapsack_steroid_hits = pd.read_csv(_logan_steroid_hits_knapsack_output_csv)

    compile_hits([manual_steroid_hits, knapsack_steroid_hits], logan_steroid_hits_output_csv)

    # Card data is empty, so check and output blank csv
    manual_cardenolide_hits = pd.read_csv(logan_cardenolide_hits_manual_output_csv)
    knapsack_cardenolide_hits = pd.read_csv(_logan_cardenolide_hits_knapsack_output_csv)
    dfs = [manual_cardenolide_hits, knapsack_cardenolide_hits]
    dfs_to_use = []
    for df in dfs:
        if len(df.index) > 0:
            dfs_to_use.append(df)
    if len(dfs_to_use) > 0:
        compile_hits(dfs_to_use, logan_cardenolide_hits_output_csv)

    else:
        out_df = pd.DataFrame(columns=['Accepted_ID', 'Accepted_Name', 'Accepted_Species', 'Accepted_Species_ID',
                                       'Accepted_Rank', compiled_sources_col])
        out_df.to_csv(logan_cardenolide_hits_output_csv)


def output_source_summaries():
    output_summary_of_hit_csv(
        logan_steroid_hits_output_csv,
        os.path.join(_output_path, 'source_summaries', 'steroid_source_summary'),
        families=['Loganiaceae'], ranks=['Species'])

    output_summary_of_hit_csv(
        logan_cardenolide_hits_output_csv,
        os.path.join(_output_path, 'source_summaries', 'cardenolide_source_summary'),
        families=['Loganiaceae'], ranks=['Species'])

    output_summary_of_hit_csv(
        logan_alkaloid_hits_output_csv,
        os.path.join(_output_path, 'source_summaries', 'alkaloid_source_summary'),
        families=['Loganiaceae'],
        source_translations={'POWO': 'POWO pages'}, ranks=['Species'])


def main():
    get_logan_metabolites()
    summarise_metabolites()
    get_logan_antibac_metabolite_hits()
    get_logan_antimal_metabolite_hits()
    get_logan_alkaloid_hits()
    get_steroid_card_hits()
    output_source_summaries()


if __name__ == '__main__':
    main()
