from flask import Flask, request, render_template, send_file, redirect, url_for
from werkzeug.utils import secure_filename
from PyPDF2 import PdfReader
from flask_wtf.csrf import CSRFProtect
from forms import PDFUploadForm  # Importez votre formulaire
import os
from dotenv import load_dotenv
from fpdf import FPDF  # Importez FPDF pour la création de PDF

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

app = Flask(__name__)

# Clé secrète pour protéger contre les attaques CSRF
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
csrf = CSRFProtect(app)

# Chemin d'upload et autres configurations
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Assurez-vous que le dossier 'uploads' existe
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Autoriser seulement les fichiers PDF
ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    form = PDFUploadForm()
    if form.validate_on_submit():
        file = form.file.data

        if file and allowed_file(file.filename):
            # Sécuriser le nom du fichier
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

            # Sauvegarder le fichier
            file.save(filepath)

            # Lire le fichier PDF et extraire le texte
            reader = PdfReader(filepath)
            extracted_text = "".join(page.extract_text() for page in reader.pages)

            # Rediriger vers une page où le texte extrait est affiché et peut être modifié
            return render_template('edit_text.html', text=extracted_text, filename=filename)

    return render_template('upload.html', form=form)


@app.route('/edit', methods=['POST'])
def edit_text():
    edited_text = request.form['edited_text']
    filename = request.form['filename']

    # Créer un nouveau fichier PDF à partir du texte modifié
    pdf_filename = filename.rsplit('.', 1)[0] + '_edited.pdf'
    pdf_filepath = os.path.join(app.config['UPLOAD_FOLDER'], pdf_filename)

    # Utiliser FPDF pour créer un nouveau PDF
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Utiliser une police compatible Unicode (DejaVuSans)
    pdf.add_font('mvboli', '', 'static/fonts/mvboli.ttf', uni=True)
    pdf.set_font('mvboli', '', 12)

     # Ajuster la hauteur des lignes pour réduire l'espace entre elles
    line_height = 5  # Réduit l'espace entre les lignes (par défaut 10)
    
    # Ajouter le texte édité dans le PDF
    pdf.multi_cell(0, line_height, edited_text)
    pdf.output(pdf_filepath)


    # Envoyer le fichier PDF édité à l'utilisateur
    return send_file(pdf_filepath, as_attachment=True)



if __name__ == '__main__':
    app.run(debug=False)
