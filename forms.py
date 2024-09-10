from flask_wtf import FlaskForm
from wtforms import FileField
from wtforms.validators import DataRequired

class PDFUploadForm(FlaskForm):
    file = FileField('PDF File', validators=[DataRequired()])
