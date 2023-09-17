# test append category to user
# test for extend categories on pdf
# test for remove categories on pdf

import pytest

from app.models import Categories
from app.utils.category import append_category_to_pdf, remove_category_from_pdf


@pytest.mark.parametrize("categories_entries, categories_of_pdf, pdf_categories_new", [
    ({"categories": [
        {"color_code": "222222", "name": "Cat2"},
        {"color_code": "333333", "name": "Cat3"},
    ]},
     [
         Categories(name="Cat1", color_code="111111")
     ],
     [
         Categories(name="Cat2", color_code="222222"),
         Categories(name="Cat3", color_code="333333"),
     ]),
    ({"categories": [
        {"color_code": "111111", "name": "Cat1"},
        {"color_code": "333333", "name": "Cat3"},
    ]},
     [
         Categories(name="Cat1", color_code="111111")
     ],
     [
         Categories(name="Cat3", color_code="333333"),
     ]),
    ({"categories": [
        {"color_code": "111111", "name": "Cat1"},
    ]},
     [
         Categories(name="Cat1", color_code="111111")
     ],
     [])
]
                         )
def test_append_category_to_user(categories_entries, categories_of_pdf, pdf_categories_new):
    assert append_category_to_pdf(
        categories_entries=categories_entries,
        categories_of_user=categories_of_pdf,
    ) == pdf_categories_new


@pytest.mark.parametrize("categories_entries, pdf_categories, categories_to_be_removed", [
    ({"categories": [
        {"color_code": "222222", "name": "Cat2"},
        {"color_code": "333333", "name": "Cat3"},
    ]},
     [
         Categories(name="Cat1", color_code="111111")
     ],
     [
         Categories(name="Cat1", color_code="111111")
     ]),
    ({"categories": [
        {"color_code": "111111", "name": "Cat1"},
        {"color_code": "333333", "name": "Cat3"},
    ]},
     [
         Categories(name="Cat1", color_code="111111")
     ],
     [

     ]),
    ({"categories": [
        {"color_code": "222222", "name": "Cat2"},
        {"color_code": "333333", "name": "Cat3"},
    ]},
     [
         Categories(name="Cat2", color_code="222222"),
         Categories(name="Cat1", color_code="111111")
     ],
     [
         Categories(name="Cat1", color_code="333333")
     ]),
    ({"categories": [
        {"color_code": "999999", "name": "Cat1"},
        {"color_code": "333333", "name": "Cat3"},
    ]},
     [
         Categories(name="Cat1", color_code="111111")
     ],
     []),
]
                         )
def test_remove_category_from_user(categories_entries, pdf_categories, categories_to_be_removed):
    assert remove_category_from_pdf(
        categories_entries=categories_entries,
        pdf_categories=pdf_categories,
    ) == categories_to_be_removed
