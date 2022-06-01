import os

import wikipedia_searches
from pkg_resources import resource_filename
### Inputs
from taxa_lists import get_all_taxa

### Outputs
_output_path = resource_filename(__name__, 'outputs')
output_logan_wiki_csv = os.path.join(_output_path, 'list_plants_with_wiki_pages.csv')
output_logan_wiki_views_csv = os.path.join(_output_path, 'taxa_wiki_views.csv')


def main():
    data = get_all_taxa(families_of_interest=['Loganiaceae'], accepted=True)

    ranks_to_use = ["Species", "Variety", "Subspecies"]

    taxa = data.loc[data["rank"].isin(ranks_to_use)]

    taxa_list = taxa["taxon_name"].values

    wikipedia_searches.make_wiki_hit_df(taxa_list, output_logan_wiki_csv, force_new_search=True)
    # taxa_to_recheck = pd.read_csv(os.path.join(_output_path,'taxa_to_recheck.csv'))
    # wikipedia_searches.make_pageview_df(taxa_list, output_logan_wiki_views_csv)


if __name__ == '__main__':
    main()
