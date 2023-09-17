import io
import os
import uuid
from pathlib import Path

from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity
from pypdf import PdfWriter, PdfReader
from pytesseract import pytesseract

from app import app, db
from app.api.image import bp
from app.models import Images, Users, PDFs
from utils.api import success_or_404
from utils.image import extract_metadata_from_images


@bp.route("", methods=["POST"])
@jwt_required()
@success_or_404
def upload_images():
    current_user = get_jwt_identity()
    # get the user's email from the database
    user_entry = Users.query.filter_by(id=current_user.get("id")).first()
    if user_entry is None:
        return {"message": "User not found"}, 404

    # validator form
    if (request.form.get("filename") == None or request.files.getlist("images") is None):
        return {"message": "Filename and image files is required"}, 400

    # create unique dir for the PDF
    pdf_dir_uuid = str(uuid.uuid4())
    pdf_filename = request.form.get("filename") + ".pdf"
    pdf_path = os.path.join(app.config["UPLOAD_FOLDER"], pdf_dir_uuid, pdf_filename)
    Path(pdf_path).parent.mkdir(exist_ok=True, parents=True)
    
    # save images to disk and keep track of their paths
    image_paths = []
    pdf_output = PdfWriter()
    for image in request.files.getlist("images"):
        filename = str(uuid.uuid4()) + ".png"
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], pdf_dir_uuid, filename)
        image.save(filepath)
        image_paths.append(filepath)
        pdf_page = pytesseract.image_to_pdf_or_hocr(filepath, extension="pdf")
        pdf_output.add_page(PdfReader(io.BytesIO(pdf_page)).pages[0])
    with open(pdf_path, "wb") as fp:
        pdf_output.write(fp)

    # save PDF path and filename to database
    new_pdf = PDFs(
        pdf_path=pdf_path,
        pdf_filename=pdf_filename,
        ocr_data=extract_metadata_from_images(image_paths),
    )
    new_pdf.users.append(user_entry)

    # append dummy category
    new_pdf.categories.append(user_entry.categories[0])

    db.session.add(new_pdf)
    db.session.commit()

    # save image paths and filenames to database
    images = []
    for image_path in image_paths:
        image_name = os.path.basename(image_path)
        image = Images(pdf_id=new_pdf.id, image_path=image_path, image_name=image_name)
        images.append(image)
    db.session.bulk_save_objects(images)
    db.session.commit()
    
    return {"message": "Document created"}

