import os
import shutil
import uuid
from pathlib import Path

import cv2
import numpy as np
from flask import make_response, request, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from pdf2image import convert_from_path

from app import app, db
from app.models import Images, Users, PDFs
from app.api.pdf import bp

from app.utils.api import success_or_404
from app.utils.category import delete_empty_categories
from app.utils.pdf import allowed_filename, extract_metadata_from_pdf, search_pdf_from_list

ALLOWED_EXTENSIONS = {"pdf"}
THUMBNAIL_WIDTH = 300
SEARCH_RESULT_LIMIT = 5

@bp.route("/<int:pdf_id>", methods=["GET"])
@jwt_required()
@success_or_404
def download_pdf(pdf_id):
    current_user = get_jwt_identity()

    pdf_data = (
        PDFs.query.filter(PDFs.id == pdf_id)
        .filter(PDFs.users.any(id=current_user["id"]))
        .first()
    )

    if pdf_data is None:
        return {"message": "Document not found or unauthorized access"}, 404

    return send_file(pdf_data.pdf_path, download_name=pdf_data.pdf_filename)


@bp.route("", methods=["GET"])
@jwt_required()
@success_or_404
def get_user_pdfs():
    current_user = get_jwt_identity()

    pdfs_data = PDFs.query.filter(PDFs.users.any(id=current_user["id"])).all()

    if len(pdfs_data) == 0:
        return {"pdfs": []}

    pdfs = [
        {
            "id": pdf_data.id,
            "pdf_filename": pdf_data.pdf_filename,
            "categories": [{"name": category.name, "color_code": category.color_code} for category in pdf_data.categories],
        }
        for pdf_data in pdfs_data
    ]

    if {"sort", "display"} <= request.args.keys():
        pdfs = sorted(pdfs, key=lambda x: x["id"], reverse=request.args["sort"] == "newest")
        pdfs = pdfs[: int(request.args["display"])]

    return {"pdfs": pdfs}


@bp.route("", methods=["POST"])
@jwt_required()
@success_or_404
def upload_pdf():
    current_user = get_jwt_identity()
    # Check if the request contains a file named "pdf"
    if "pdf" not in request.files:
        return {"message": "No file provided"}, 400

    file = request.files["pdf"]
    if file.filename == "":
        return {"message": "No file selected"}, 400
    
    if not file or not allowed_filename(file.filename, ALLOWED_EXTENSIONS):
        return {"message": "Invalid file type"}, 400

    pdf_filename = file.filename
    pdf_dir_uuid = str(uuid.uuid4())

    # save to local folder
    pdf_path = os.path.join(app.config["UPLOAD_FOLDER"], pdf_dir_uuid, pdf_filename)
    Path(pdf_path).parent.mkdir(exist_ok=True, parents=True)
    file.save(pdf_path)
    user_entry = Users.query.filter_by(id=current_user["id"]).first()
    ocr_data = extract_metadata_from_pdf(pdf_path=pdf_path)

    # Save pdf information in pdf_table
    new_pdf = PDFs(pdf_path=pdf_path, pdf_filename=pdf_filename, ocr_data=ocr_data)
    new_pdf.users.append(user_entry)

    # append dummy category
    new_pdf.categories.append(user_entry.categories[0])

    db.session.add(new_pdf)
    db.session.commit()

    return {"message": "Document uploaded successfully"}


@bp.route("/<int:pdf_id>", methods=["DELETE"])
@jwt_required()
@success_or_404
def delete_pdf(pdf_id):
    current_user = get_jwt_identity()

    pdf_data = (
        PDFs.query.filter(PDFs.id == pdf_id)
        .filter(PDFs.users.any(id=current_user["id"]))
        .first()
    )

    if not pdf_data:
        return {"message": "Document not found or unauthorized access"}, 404

    # Delete the PDF and its associated images from the server and the database
    pdf_path = pdf_data.pdf_path
    delete_empty_categories(categories=pdf_data.categories, user_id=current_user["id"])
    pdf_data.categories = []
    db.session.query(PDFs).filter_by(id=pdf_id).delete()
    db.session.commit()
    shutil.rmtree(os.path.dirname(pdf_path))

    return {"message": "Document deleted"}


@bp.route("/<int:pdf_id>", methods=["PUT"])
@jwt_required()
@success_or_404
def update_pdf(pdf_id):
    current_user = get_jwt_identity()

    pdf_data = (
        PDFs.query.filter(PDFs.id == pdf_id)
        .filter(PDFs.users.any(id=current_user["id"]))
        .first()
    )

    if not pdf_data:
        return {"message": "Document not found or unauthorized access"}, 404

    # Update the filename of the PDF in the server and the database
    new_pdf_filename = request.json.get("pdf_filename")
    if not new_pdf_filename:
        return {"message": "Document filename not provided"}, 400

    db.session.query(PDFs).filter_by(id=pdf_id).update(
        {"pdf_filename": new_pdf_filename}
    )
    db.session.commit()
    return {"message": "Document filename updated"}

@app.route("/pdf/thumbnail/<int:pdf_id>", methods=["GET"])
@jwt_required()
@success_or_404
def get_thumbnail(pdf_id):
    current_user = get_jwt_identity()

    pdf_data = (
        PDFs.query.filter(PDFs.id == pdf_id)
        .filter(PDFs.users.any(id=current_user["id"]))
        .first()
    )

    if len(pdf_data.images) > 0:
        thumbnail_img = cv2.imread(pdf_data.images[0].image_path)
    else:
        thumbnail_img_all = convert_from_path(pdf_data.pdf_path, first_page=1, last_page=1)
        thumbnail_img = np.array(thumbnail_img_all[0])
        thumbnail_img = cv2.cvtColor(thumbnail_img, cv2.COLOR_BGR2RGB)

        image_name = f"{str(uuid.uuid4())}.png"
        image_path = os.path.join(os.path.dirname(pdf_data.pdf_path), image_name)
        image = Images(pdf_id=pdf_data.id, image_path=image_path, image_name=image_name)
        cv2.imwrite(image_path, thumbnail_img)
        db.session.add(image)
        db.session.commit()

    width_ratio = thumbnail_img.shape[1] / THUMBNAIL_WIDTH
    img_shape = (THUMBNAIL_WIDTH, int(thumbnail_img.shape[0] / width_ratio))
    thumbnail_img = cv2.resize(src=thumbnail_img, dsize=img_shape)

    _, buffer = cv2.imencode(".png", thumbnail_img)
    response = make_response(buffer.tobytes())
    response.headers["Content-Type"] = "image/png"
    return response
    
@bp.route("/search/<string:search_term>", methods=["GET"])
@jwt_required()
@success_or_404
def search_from_user_pdfs(search_term: str):
    current_user = get_jwt_identity()

    empty_list = {"pdfs": []}

    if search_term == "":
        return empty_list

    pdfs_data = PDFs.query.filter(PDFs.users.any(id=current_user["id"])).all()

    if len(pdfs_data) == 0:
        return empty_list

    pdfs = [
        {
            "id": pdf_data.id,
            "pdf_filename": pdf_data.pdf_filename,
            "filename": pdf_data.pdf_filename.replace(".pdf", ""),
            "docutext": pdf_data.ocr_data["document_data"]["document_text"]
            if "document_data" in pdf_data.ocr_data
            else "",
        }
        for pdf_data in pdfs_data
    ]
    keyword_list = search_term.split()
    if len(keyword_list) > 1:
        keyword_list += [search_term]

    return search_pdf_from_list(pdfs=pdfs, keyword_list=keyword_list, search_limit=SEARCH_RESULT_LIMIT)


@bp.route("/dummy-upload", methods=["POST"])
@jwt_required()
@success_or_404
def dummy_pdf_post():
    current_user = get_jwt_identity()
    if not current_user:
        return {"message": "Invalid User"}, 400
    # Check if the request contains a file named "pdf"
    if "pdf" not in request.files:
        return {"message": "Error occurred, 'pdf' should be the name of the key for the file"}, 400
    file = request.files["pdf"]
    file_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
    file.save(file_path)
    response = send_file(file_path)
    response.headers["metadata"] = {
        "name": "John Doe",
        "age": 30,
        "email": "john.doe@example.com",
    }
    return response
