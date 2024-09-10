from flask import Flask, request, render_template, send_file
from werkzeug.utils import secure_filename
from PyPDF2 import PdfReader
from flask_wtf.csrf import CSRFProtect
from forms import PDFUploadForm  # Importez votre formulaire
import os
from dotenv import load_dotenv

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
            extracted_text = ""
            for page in reader.pages:
                extracted_text += page.extract_text()
            
            # Créer un fichier texte à partir de l'extraction
            txt_filename = filename.rsplit('.', 1)[0] + '.txt'
            txt_filepath = os.path.join(app.config['UPLOAD_FOLDER'], txt_filename)
            
            with open(txt_filepath, 'w', encoding='utf-8') as txt_file:
                txt_file.write(extracted_text)
            
            try:
                # Envoyer le fichier .txt à l'utilisateur
                return send_file(txt_filepath, as_attachment=True)
            finally:
                # Supprimer le fichier PDF et le fichier texte après l'envoi
                if os.path.exists(filepath):
                    os.remove(filepath)
                if os.path.exists(txt_filepath):
                    os.remove(txt_filepath)
    
    return render_template('upload.html', form=form)

if __name__ == '__main__':
    app.run(debug=True)
