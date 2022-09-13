import hashlib
import os.path
import urllib.request
from typing import List
from urllib.error import HTTPError

import pandas as pd
from automatchnames import get_accepted_info_from_names_in_column, clean_urn_ids, get_accepted_info_from_ids_in_column
from cleaning import compile_hits, generic_prepare_data, get_tempout_csv, output_summary_of_hit_csv, single_source_col
from common_name_vars import wiersema_temp_output_accepted
from pkg_resources import resource_filename
from poison_vars import cornell_poison_file, CPCS_poison_file, UCANR_toxic_file, UCANR_nontoxic_file, tppt_toxic_file
### Inputs
from taxa_lists.get_taxa_from_wcvp import get_all_taxa
from tqdm import tqdm

_inputs_path = resource_filename(__name__, 'inputs')
_initial_USDA_csv = os.path.join(_inputs_path, 'USDA Plants Database.csv')
# Non-sci names sheet saved as utf8
_initial_MPNS_csv = os.path.join(_inputs_path, 'MPNSv11 Loganiaceae + Gentianaceae + Gelsemiaceae.csv')
_ppa_africa_csv = os.path.join(_inputs_path, 'PPAfrica-botswana-commonnames', 'vernacularname.txt')
_species_profile_csv = os.path.join(_inputs_path, 'SpeciesProfileVernacular', 'vernacular.tab')
_duke_common_name_data = os.path.join(_inputs_path, 'COMMON_NAMES.csv')
_duke_taxa_codes = os.path.join(_inputs_path, 'FNFTAX.csv')

### Temp outputs
_temp_outputs_path = resource_filename(__name__, 'temp_outputs')

_wiki_common_names_temp_output_csv = os.path.join(_temp_outputs_path, 'wiki_common_name_hits.csv')
_powo_common_names_temp_output_csv = os.path.join(_temp_outputs_path, 'powo_common_name_hits.csv')

# Standardised versions
_spp_common_names_temp_output_accepted_csv = os.path.join(_temp_outputs_path, 'spp_common_names_accepted.csv')
_ppa_common_names_temp_output_accepted_csv = os.path.join(_temp_outputs_path, 'ppa_common_names_accepted.csv')
_wiki_common_names_temp_output_accepted_csv = os.path.join(_temp_outputs_path, 'wiki_common_name_hits_accepted.csv')
_powo_common_names_temp_output_accepted_csv = os.path.join(_temp_outputs_path, 'powo_common_name_hits_accepted.csv')
_cleaned_USDA_accepted_csv = os.path.join(_temp_outputs_path, 'USDA Plants Database_cleaned_accepted.csv')
_cleaned_MPNS_accepted_csv = os.path.join(_temp_outputs_path, 'MPNS Data_cleaned_accepted.csv')

### Outputs
_output_path = resource_filename(__name__, 'outputs')
output_logan_common_names_csv = os.path.join(_output_path, 'list_of_plants_with_common_names.csv')


def prepare_usda_common_names(families_of_interest=None):
    # # Copied from https://plants.usda.gov/csvdownload?plantLst=plantCompleteList
    usda_df = pd.read_csv(_initial_USDA_csv)
    usda_df.drop(columns=['Symbol', 'Synonym Symbol'], inplace=True)
    usda_df = usda_df.rename(columns={'Common Name': 'USDA_Snippet'})
    usda_df = usda_df.dropna(subset=['USDA_Snippet'])
    if families_of_interest is not None:
        usda_df = usda_df[usda_df['Family'].str.contains('|'.join(families_of_interest))]

    accepted_usda_df = get_accepted_info_from_names_in_column(usda_df, 'Scientific Name with Author')

    accepted_usda_df['Source'] = 'USDA Plants Database'

    accepted_usda_df.to_csv(_cleaned_USDA_accepted_csv)

    return accepted_usda_df


def prepare_common_names_spp_ppa():
    species_profile = pd.read_csv(_species_profile_csv, sep='\t', header=None)

    species_profile[single_source_col] = 'SpeciesProfileVernacular'
    species_profile['SPP_Snippet'] = species_profile[1] + ":" + species_profile[2]
    species_profile['ID'] = species_profile[0].apply(clean_urn_ids)
    species_profile.drop(columns=[0, 1, 2, 3], inplace=True)
    spp = get_accepted_info_from_ids_in_column(species_profile, 'ID')
    spp.to_csv(_spp_common_names_temp_output_accepted_csv)

    ppa_africa = pd.read_csv(_ppa_africa_csv, sep='\t', header=None)
    ppa_africa[single_source_col] = 'PPAfrica-botswana-commonnames'
    ppa_africa['PPA_Snippet'] = ppa_africa[3] + ":" + ppa_africa[2]
    ppa_africa['ID'] = ppa_africa[0].apply(clean_urn_ids)
    ppa_africa.drop(columns=[0, 1, 2, 3, 4], inplace=True)

    ppa = get_accepted_info_from_ids_in_column(ppa_africa, 'ID')

    ppa.to_csv(_ppa_common_names_temp_output_accepted_csv)

    return spp, ppa


def prepare_MPNS_common_names(families_of_interest: List[str] = None) -> pd.DataFrame:
    # Requested from from MPNS
    mpns_df = pd.read_csv(_initial_MPNS_csv)
    mpns_df.drop(columns=['authority', 'plant_id', 'ID'], inplace=True)

    mpns_df = mpns_df.dropna(subset=['non_sci_name'])
    mpns_df = mpns_df[mpns_df['non_sci_name_type'] == 'common']
    if families_of_interest is not None:
        mpns_df = mpns_df[mpns_df['family'].str.contains('|'.join(families_of_interest))]

    mpns_df['non_sci_name'] = mpns_df.groupby(['taxon_name'])['non_sci_name'].transform(lambda x: ':'.join(x))
    mpns_df = mpns_df.drop_duplicates()
    mpns_df.rename(columns={'non_sci_name': 'MPNS_Snippet'}, inplace=True)

    accepted_mpns_df = get_accepted_info_from_names_in_column(mpns_df, 'taxon_name',
                                                              families_of_interest=families_of_interest)

    accepted_mpns_df = accepted_mpns_df.dropna(subset=['Accepted_Name'])
    accepted_mpns_df['Source'] = 'MPNS'
    print(accepted_mpns_df)
    accepted_mpns_df.drop(accepted_mpns_df.columns[0], axis=1, inplace=True)

    accepted_mpns_df.to_csv(_cleaned_MPNS_accepted_csv)

    return accepted_mpns_df


def get_powo_common_names(species_names: List[str], species_ids: List[str],
                          families_of_interest: List[str] = None, force_new_search=False) -> pd.DataFrame:
    '''
    Searches POWO for species names which have a common names section.
    :param species_names:
    :param species_ids:
    :return:
    '''
    out_dict = {'Name': [], 'POWO_Snippet': [], 'Source': []}
    # Save previous searches using a hash of names to avoid repeating searches
    names = list(species_names)
    ids = list(species_ids)
    full_list = names + ids
    str_to_hash = str(full_list).encode()
    temp_csv = "powo_common_name_search_" + str(hashlib.md5(str_to_hash).hexdigest()) + ".csv"

    temp_output_powo_csv = os.path.join(_temp_outputs_path, temp_csv)
    if os.path.isfile(temp_output_powo_csv) and not force_new_search:

        df = pd.read_csv(temp_output_powo_csv)
    else:
        for i in tqdm(range(len(species_names)), desc="Searching POWO for common names…", ascii=False, ncols=72):
            try:
                name = species_names[i]
                id = species_ids[i]

                fp = urllib.request.urlopen("https://powo.science.kew.org/taxon/urn:lsid:ipni.org:names:" + str(id))
                mybytes = fp.read()

                mystr = mybytes.decode("utf8")
                fp.close()
                # print(mystr)
                common_name_section = '<section id="vernacular-names" class="c-article-section">'
                if common_name_section in mystr:
                    i = mystr.index(common_name_section)
                    snippet = mystr[i - 1:i + len(common_name_section) + 1]
                    out_dict['Name'].append(name)
                    out_dict['POWO_Snippet'].append(snippet)
                    out_dict['Source'].append('POWO pages(' + str(id) + ')')
            except HTTPError:
                print(f'Couldnt find id on POWO: {species_ids[i]}')
        df = pd.DataFrame(out_dict)
    df.to_csv(temp_output_powo_csv)
    acc_df = get_accepted_info_from_names_in_column(df, 'Name',
                                                    families_of_interest=families_of_interest)

    acc_df.to_csv(_powo_common_names_temp_output_accepted_csv)
    return acc_df


def get_wiki_common_names(taxa_list: List[str], families_of_interest: List[str] = None):
    import wikipedia_searches

    wiki_df = wikipedia_searches.search_for_common_names(taxa_list, _wiki_common_names_temp_output_csv)
    # wiki_df=pd.read_csv(_wiki_common_names_temp_output_csv)
    acc_wiki_df = get_accepted_info_from_names_in_column(wiki_df, 'Name',
                                                         families_of_interest=families_of_interest)
    acc_wiki_df.to_csv(_wiki_common_names_temp_output_accepted_csv)

    return acc_wiki_df


def prepare_cornell_data():
    tables = pd.read_html(cornell_poison_file)
    toxic_df = tables[0]
    generic_prepare_data('Cornell CALS', _temp_outputs_path, toxic_df, 'Scientific Name', dropifna=['Common Name(s)'])


def prepare_CPCS_data():
    tables = pd.read_html(CPCS_poison_file)

    non_toxic_db = tables[1]
    # Remove letter headers
    non_toxic_db = non_toxic_db[~non_toxic_db['Latin or scientific name'].str.contains('^[A-Z]$', regex=True)]
    generic_prepare_data('CPCS nontoxic', _temp_outputs_path, non_toxic_db, 'Latin or scientific name',
                         dropifna=['Common name'])

    toxic_db = tables[4]
    toxic_db = toxic_db[~toxic_db['Latin or scientific name'].str.contains('^[A-Z]$', regex=True)]
    generic_prepare_data('CPCS toxic', _temp_outputs_path, toxic_db, 'Latin or scientific name',
                         dropifna=['Common name'])


def prepare_toxic_UCANR_data():
    toxic_tables = pd.read_html(UCANR_toxic_file, header=0)
    toxic_db = toxic_tables[0]
    generic_prepare_data('UCANR Toxic', _temp_outputs_path, toxic_db, 'Toxic plants: Scientific name',
                         dropifna=['Common name'])


def prepare_nontoxic_UCANR_data():
    nontoxic_tables = pd.read_html(UCANR_nontoxic_file, header=0)
    nontoxic_db = nontoxic_tables[0]
    generic_prepare_data('UCANR NonToxic', _temp_outputs_path, nontoxic_db, 'Safe plants: Scientific name',
                         dropifna=['Common name'])


def prepare_duke_usda_data(families_of_interest: List[str] = None):
    cmmn_names = pd.read_csv(_duke_common_name_data)
    taxa_codes = pd.read_csv(_duke_taxa_codes)
    merged = pd.merge(cmmn_names, taxa_codes, on='FNFNUM')
    merged.dropna(subset=['CNNAM'], inplace=True)

    if families_of_interest is not None:
        # The step with the mask is necessary to include taxa with unknown families
        mask = merged['FAMILY'].str.contains('|'.join(families_of_interest))
        mask.fillna(True, inplace=True)
        merged = merged[mask]

    merged['Common names'] = merged.groupby(['TAXON'])['CNNAM'].transform(lambda x: ':'.join(x))
    merged = merged.drop_duplicates(subset=['TAXON'])

    generic_prepare_data('USDA(Duke)', _temp_outputs_path, merged, 'TAXON')


def prepare_TPPT_data(families_of_interest: List[str] = None):
    toxic_db = pd.read_csv(tppt_toxic_file)
    toxic_db.dropna(subset=['German_plant_name', 'English_plant_name'], how='all', inplace=True)
    if families_of_interest is not None:
        toxic_db = toxic_db[toxic_db['Plant_family'].str.contains('|'.join(families_of_interest))]

    generic_prepare_data('TPPT', _temp_outputs_path, toxic_db, 'Latin_plant_name',
                         families_of_interest=toxic_db['Plant_family'].unique().tolist())


def prepare_data():
    families_of_interest = ['Loganiaceae']
    accepted_data = get_all_taxa(families_of_interest=families_of_interest, accepted=True)

    ranks_to_use = ["Species", "Variety", "Subspecies"]

    accepted_taxa_df = accepted_data.loc[accepted_data["rank"].isin(ranks_to_use)]

    accepted_taxa = accepted_taxa_df["taxon_name"].values
    accepted_taxa_ids = accepted_taxa_df["kew_id"].values

    # Get lists
    get_wiki_common_names(accepted_taxa, families_of_interest=families_of_interest)
    get_powo_common_names(accepted_taxa, accepted_taxa_ids, families_of_interest=families_of_interest)

    prepare_usda_common_names(families_of_interest=families_of_interest)
    prepare_common_names_spp_ppa()
    prepare_MPNS_common_names(families_of_interest=families_of_interest)

    prepare_cornell_data()
    prepare_CPCS_data()
    prepare_toxic_UCANR_data()
    prepare_nontoxic_UCANR_data()
    prepare_duke_usda_data(families_of_interest=families_of_interest)
    prepare_TPPT_data(families_of_interest=families_of_interest)


def main():
    if not os.path.isdir(_temp_outputs_path):
        os.mkdir(_temp_outputs_path)
    if not os.path.isdir(_output_path):
        os.mkdir(_output_path)

    prepare_data()

    cornell_hits = pd.read_csv(get_tempout_csv('Cornell CALS', _temp_outputs_path), index_col=0)
    cpcs_hits = pd.read_csv(get_tempout_csv('CPCS nontoxic', _temp_outputs_path), index_col=0)
    cpcs_toxic_hits = pd.read_csv(get_tempout_csv('CPCS toxic', _temp_outputs_path), index_col=0)
    ucantoxic_hits = pd.read_csv(get_tempout_csv('UCANR Toxic', _temp_outputs_path), index_col=0)
    ucannontoxic_hits = pd.read_csv(get_tempout_csv('UCANR NonToxic', _temp_outputs_path), index_col=0)
    duke_hits = pd.read_csv(get_tempout_csv('USDA(Duke)', _temp_outputs_path), index_col=0)
    tppt_hits = pd.read_csv(get_tempout_csv('TPPT', _temp_outputs_path), index_col=0)
    wiersema_hits = pd.read_csv(wiersema_temp_output_accepted, index_col=0)

    usda_hits = pd.read_csv(_cleaned_USDA_accepted_csv)
    spp_df = pd.read_csv(_spp_common_names_temp_output_accepted_csv)
    ppa_df = pd.read_csv(_ppa_common_names_temp_output_accepted_csv)
    powo_hits = pd.read_csv(_powo_common_names_temp_output_accepted_csv)
    wiki_hits = pd.read_csv(_wiki_common_names_temp_output_accepted_csv)
    mpns_hits = pd.read_csv(_cleaned_MPNS_accepted_csv)

    all_dfs = [mpns_hits, usda_hits, powo_hits, wiki_hits, spp_df, ppa_df, cornell_hits, cpcs_hits, cpcs_toxic_hits,
               ucantoxic_hits, ucannontoxic_hits, duke_hits, tppt_hits, wiersema_hits]
    # Some dfs are empty and don't have accepted info as a result
    dfs_to_use = [df for df in all_dfs if (len(df.index) > 0)]
    compile_hits(dfs_to_use, output_logan_common_names_csv)

    output_summary_of_hit_csv(
        output_logan_common_names_csv,
        os.path.join(_output_path, 'source_summaries', 'commonname_source_summary'))


if __name__ == '__main__':
    main()
