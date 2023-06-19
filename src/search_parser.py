from os import path
from pandas import concat, DataFrame
from src.utilities import get_filenames, only, read_html


# index = 0
# file = open(path.join(search_pages_folder, query + ".html"), "r", encoding='UTF-8')
# search_result = read_html(search_pages_folder, query).select("div.s-main-slot.s-result-list > div[data-component-type='s-search-result']")[index]
# file.close()
def parse_search_result(query, search_result, index):
    sponsored = False
    sponsored_tags = search_result.select(
        "a[aria-label='View Sponsored information or leave ad feedback']"
    )
    if len(sponsored_tags) > 0:
        # sanity check
        only(sponsored_tags)
        sponsored = True

    product_url = only(
        search_result.select(
            # a link in a heading
            "h2 a",
        )
    )["href"]

    amazon_brand_widgets = search_result.select(".puis-light-weight-text")
    if len(amazon_brand_widgets):
        amazon_brand = True
    else:
        amazon_brand = False

    return DataFrame(
        {
            "query": [query],
            "rank": [index + 1],
            "product_url": [product_url],
            "sponsored": [sponsored],
            "amazon_brand": [amazon_brand],
        }
    )


def parse_search_page(search_pages_folder, query):
    return concat(
        parse_search_result(query, search_result, index)
        for index, search_result in enumerate(
            read_html(path.join(search_pages_folder, query + ".html")).select(
                ", ".join(
                    [
                        "div.s-main-slot.s-result-list > div[data-component-type='s-search-result']",
                        "div.s-main-slot.s-result-list > div[cel_widget_id*='MAIN-VIDEO_SINGLE_PRODUCT']",
                    ]
                )
            )
        )
    )


class DuplicateProductUrls(Exception):
    pass


def parse_search_pages(search_pages_folder):
    return concat(
        parse_search_page(search_pages_folder, query)
        for query in get_filenames(search_pages_folder)
    )