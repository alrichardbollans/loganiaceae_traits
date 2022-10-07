import os

import pandas as pd
import wikipedia_searches
from pkg_resources import resource_filename
### Inputs
from taxa_lists import get_all_taxa

### Outputs
_output_path = resource_filename(__name__, 'outputs')
output_logan_wiki_csv = os.path.join(_output_path, 'list_plants_with_wiki_pages.csv')
output_logan_wiki_views_csv = os.path.join(_output_path, 'taxa_wiki_views.csv')


def main():
    data = get_all_taxa(families_of_interest=['Loganiaceae'], accepted=False,
                        ranks=["Species", "Variety", "Subspecies"])

    taxa = data["taxon_name"].unique()

    wikipedia_searches.make_wiki_hit_df(taxa, output_logan_wiki_csv,
                                        force_new_search=True)


if __name__ == '__main__':
    main()
