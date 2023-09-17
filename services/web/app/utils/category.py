from app.models import Categories, PDFs
from app import db

def determine_categories_of_pdf(categories_entries: list[dict[str]], categories_of_user: list[Categories]) -> list[Categories]:
    pdf_categories = []
    pdf_categories_new = []
    names_category_of_user = {category.name: category for category in categories_of_user}
    for category_entry in categories_entries:
        if category_entry["name"] not in names_category_of_user:
            category = Categories(name=category_entry["name"], color_code=category_entry["color_code"])
            pdf_categories_new.append(category)
        else:
            category = names_category_of_user[category_entry["name"]]
        pdf_categories.append(category)

    return pdf_categories, pdf_categories_new

def delete_empty_categories(categories: list[Categories], user_id: int) -> None:
    for category in categories:
        pdf_with_category = (
            PDFs.query
            .filter(PDFs.users.any(id=user_id))
            .filter(PDFs.categories.any(name=category.name)).all()
        )
        if len(pdf_with_category) == 0:
            db.session.delete(category)
