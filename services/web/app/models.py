from sqlalchemy.dialects.postgresql import JSONB

from app import db

docu_user = db.Table(
    "docu_user",
    db.Column("docu_id", db.BigInteger, db.ForeignKey("pdfs.id")),
    db.Column("user_id", db.BigInteger, db.ForeignKey("users.id")),
)

docu_category = db.Table(
    "docu_category",
    db.Column("docu_id", db.BigInteger, db.ForeignKey("pdfs.id")),
    db.Column("category_id", db.BigInteger, db.ForeignKey("categories.id")),
)


# https://www.digitalocean.com/community/tutorials/how-to-use-many-to-many-database-relationships-with-flask-sqlalchemy#step-2-setting-up-database-models-for-a-many-to-many-relationship
class Users(db.Model):
    __tablename__ = "users"
    id = db.Column(db.BigInteger, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    categories = db.relationship("Categories", backref="users", lazy=True)
    accepted_tos = db.Column(db.Boolean, unique=False, default=False)  # TODO or should be none?
    # TODO default to UTC timezone, just test and create API later when we have pgAdmin
    date_accepted_tos = db.Column(db.DateTime(timezone=True))


class PDFs(db.Model):
    __tablename__ = "pdfs"
    id = db.Column(db.BigInteger, primary_key=True)
    pdf_path = db.Column(db.Text, nullable=False)
    # allow to quickly read filenames without iterating in folders
    pdf_filename = db.Column(db.String(255), nullable=False)
    images = db.relationship("Images", backref="pdfs", lazy=True)
    users = db.relationship("Users", secondary=docu_user, backref="pdfs")
    categories = db.relationship("Categories", secondary=docu_category, backref="pdfs")
    ocr_data = db.Column(JSONB, nullable=True)


class Images(db.Model):
    __tablename__ = "images"
    id = db.Column(db.BigInteger, primary_key=True)
    pdf_id = db.Column(db.BigInteger, db.ForeignKey("pdfs.id", ondelete="CASCADE"), nullable=False)
    image_path = db.Column(db.Text, nullable=False)
    image_name = db.Column(db.String(255), nullable=False)


class Categories(db.Model):
    __tablename__ = "categories"
    id = db.Column(db.BigInteger, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    icon_path = db.Column(db.Text, nullable=True)
    color_code = db.Column(db.String(255), nullable=True)  # HEX Code, lower case ("0080ff")
    user_id = db.Column(db.BigInteger, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
