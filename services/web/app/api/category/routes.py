from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity

from app import db
from app.api.category import bp
from app.models import Categories, PDFs, Users
from app.utils.category import determine_categories_of_pdf, delete_empty_categories
from app.utils.api import success_or_404


@bp.route("/<int:pdf_id>", methods=["GET"])
@jwt_required()
@success_or_404
def get_categories_of_pdf(pdf_id):
    current_user = get_jwt_identity()

    pdf_data = (
        PDFs.query.filter(PDFs.id == pdf_id)
        .filter(PDFs.users.any(id=current_user["id"]))
        .first()
    )

    if pdf_data is None:
        return {"message": "Document not found or unauthorized access"}, 404
    
    categories = [{"name": category.name, "color_code": category.color_code} for category in pdf_data.categories]

    return {"categories": categories}

@bp.route("/<int:pdf_id>", methods=["POST"])
@jwt_required()
@success_or_404
def post_categories_of_pdf(pdf_id):
    current_user = get_jwt_identity()

    pdf_data = (
        PDFs.query.filter(PDFs.id == pdf_id)
        .filter(PDFs.users.any(id=current_user["id"]))
        .first()
    )

    if pdf_data is None:
        return {"message": "Document not found or unauthorized access"}, 404

    user_entry = Users.query.filter_by(id=current_user.get("id")).first()
    old_categories = pdf_data.categories

    # find which categories to be created as new category to database
    pdf_categories, pdf_categories_new = determine_categories_of_pdf(
        categories_entries=request.json["categories"],
        categories_of_user=user_entry.categories,
        )

    pdf_data.categories = pdf_categories
    user_entry.categories.extend(pdf_categories_new)

    # delete category from database if not used on any document
    old_categories = [category for category in old_categories if category not in pdf_categories]
    delete_empty_categories(categories=old_categories, user_id=current_user["id"])

    db.session.add(pdf_data)
    db.session.commit()

    return {"message": "Document category updated"}


@bp.route("/pdf-all", methods=["GET"])
@jwt_required()
@success_or_404
def get_pdfs_to_category():

    current_user = get_jwt_identity()

    # /category/pdf-all?categories=Kategorie%201&categories=Kategorie%202
    category_names = request.args.getlist('categories')

    pdfs_data = (
        PDFs.query
        .filter(PDFs.users.any(id=current_user["id"]))
        .filter(*[PDFs.categories.any(Categories.name == name) for name in category_names])
        .all()
        )

    if len(pdfs_data) == 0:
        return {"pdfs": []}

    pdfs = [
        {"id": pdf_data.id, "pdf_filename": pdf_data.pdf_filename}
        for pdf_data in pdfs_data
    ]

    if {"sort", "display"} <= request.args.keys():
        pdfs = sorted(pdfs, key=lambda x: x["id"], reverse=request.args["sort"] == "newest")
        pdfs = pdfs[: int(request.args["display"])]

    return {"pdfs": pdfs}
