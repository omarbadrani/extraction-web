import sys
import requests
import re
from bs4 import BeautifulSoup
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QLabel,
                             QLineEdit, QPushButton, QTextEdit, QProgressBar,
                             QHBoxLayout, QMessageBox)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from urllib.parse import urlparse
import time


class ExtractionThread(QThread):
    """Thread séparé pour l'extraction afin de ne pas bloquer l'interface"""
    finished = pyqtSignal(str)
    progress = pyqtSignal(int)
    error = pyqtSignal(str)

    def __init__(self, url):
        super().__init__()
        self.url = url

    def run(self):
        try:
            self.progress.emit(10)
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }

            response = requests.get(self.url, headers=headers, timeout=15)
            response.raise_for_status()
            self.progress.emit(30)

            self.soup = BeautifulSoup(response.text, 'html.parser')
            self.progress.emit(50)

            # Nettoyage du texte
            for script in self.soup(["script", "style"]):
                script.decompose()

            text = self.soup.get_text(separator=' ', strip=True)
            self.progress.emit(60)

            # Regex pour emails, téléphones, adresses
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'
            phone_pattern = r'''
                (?:\+|00)?216\s*[2-9]\d{1}\s*(?:\d{2}[\s\-.]?){3}|
                \b[2-9]\d{1}[\s\-.]?(?:\d{2}[\s\-.]?){3}\b|
                \(\+216\)\s*\d{2}\s*\d{3}\s*\d{3}
            '''
            address_pattern = r'\b\d{1,5}\s+[\w\s,.-]+(?:\s+(?:Avenue|Street|Rue|Route|Immeuble|Bloc|Appartement|Apt|Bâtiment|Residence|Cite|Zone|Lotissement|Place|Immeuble))?(?:\s+\d{5})?\s+(?:Tunisia|Tunisie|Tunis|Sfax|Sousse|Bizerte|Gabès|Ariana|Kairouan|Gafsa|Monastir|Médenine|Nabeul|Béja|Ben\sArous|Siliana|Mahdia|Zaghouan|Kébili|Tozeur|Tataouine|Manouba|Kasserine|Jendouba)\b'

            # === EXTRACTION EMAILS ===
            emails = set(re.findall(email_pattern, text, re.IGNORECASE))

            # Balises pouvant contenir info contact
            coordonnees = self.soup.find_all(['address', 'p', 'div', 'span', 'li'],
                                             string=re.compile(
                                                 r'téléphone|phone|tel|contact|adresse|email|e-mail|address|location|localisation',
                                                 re.IGNORECASE))
            for elem in coordonnees:
                elem_text = elem.get_text()
                found_emails = re.findall(email_pattern, elem_text, re.IGNORECASE)
                emails.update(found_emails)

            # Liens mailto
            for link in self.soup.find_all('a', href=True):
                href = link['href']
                if href.startswith('mailto:'):
                    email = href[7:].split('?')[0]
                    if re.match(email_pattern, email):
                        emails.add(email)

            self.progress.emit(70)

            # === EXTRACTION TELEPHONES ===
            telephones = set()
            phone_matches = re.findall(phone_pattern, text, re.VERBOSE)
            for phone in phone_matches:
                cleaned_phone = re.sub(r'[\s\-\.\(\)]', '', phone.strip())
                if cleaned_phone.startswith('216') and len(cleaned_phone) == 11:
                    telephones.add(self.format_phone(cleaned_phone))
                elif len(cleaned_phone) == 8:
                    telephones.add(self.format_phone('216' + cleaned_phone))

            # Rechercher dans balises ciblées
            for elem in coordonnees:
                elem_text = elem.get_text()
                found_phones = re.findall(phone_pattern, elem_text, re.VERBOSE)
                for phone in found_phones:
                    cleaned_phone = re.sub(r'[\s\-\.\(\)]', '', phone.strip())
                    if cleaned_phone.startswith('216') and len(cleaned_phone) == 11:
                        telephones.add(self.format_phone(cleaned_phone))
                    elif len(cleaned_phone) == 8:
                        telephones.add(self.format_phone('216' + cleaned_phone))

            # Liens tel:
            for link in self.soup.find_all('a', href=True):
                href = link['href']
                if href.startswith('tel:'):
                    phone = href[4:].strip()
                    cleaned_phone = re.sub(r'[\s\-\.\(\)+]', '', phone)
                    if cleaned_phone.startswith('216') and len(cleaned_phone) == 11:
                        telephones.add(self.format_phone(cleaned_phone))
                    elif len(cleaned_phone) == 8:
                        telephones.add(self.format_phone('216' + cleaned_phone))

            self.progress.emit(80)

            # === EXTRACTION ADRESSES ===
            adresses = set()
            address_matches = re.findall(address_pattern, text, re.IGNORECASE | re.VERBOSE)
            for addr in address_matches:
                cleaned_addr = re.sub(r'\s+', ' ', addr.strip())
                adresses.add(cleaned_addr)
            for elem in coordonnees:
                elem_text = elem.get_text()
                found_addresses = re.findall(address_pattern, elem_text, re.IGNORECASE | re.VERBOSE)
                for addr in found_addresses:
                    cleaned_addr = re.sub(r'\s+', ' ', addr.strip())
                    adresses.add(cleaned_addr)

            self.progress.emit(90)

            # === PRÉPARATION DES RÉSULTATS ===
            resultat = f"=== RÉSULTATS DE L'EXTRACTION ===\n\nURL analysée: {self.url}\nDate d'analyse: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n"

            resultat += f"Emails trouvés ({len(emails)}):\n" + ("\n".join(f"- {e}" for e in sorted(emails)) if emails else "Aucun email trouvé") + "\n\n"
            resultat += f"Téléphones trouvés ({len(telephones)}):\n" + ("\n".join(f"- {t}" for t in sorted(telephones)) if telephones else "Aucun numéro de téléphone trouvé") + "\n\n"
            resultat += f"Adresses trouvées ({len(adresses)}):\n" + ("\n".join(f"- {a}" for a in sorted(adresses)) if adresses else "Aucune adresse trouvée") + "\n\n"

            # Description du site
            resultat += self.generer_extrait_texte(text, emails, telephones, adresses)

            self.progress.emit(100)
            self.finished.emit(resultat)

        except requests.exceptions.RequestException as e:
            self.error.emit(f"Erreur de connexion: {str(e)}")
        except Exception as e:
            self.error.emit(f"Erreur inattendue: {str(e)}")

    def format_phone(self, phone):
        cleaned = re.sub(r'[^\d]', '', phone)
        if cleaned.startswith('216'):
            cleaned = cleaned[3:]
        return f"+216 {cleaned[:2]} {cleaned[2:5]} {cleaned[5:]}"

    def generer_extrait_texte(self, texte, emails, telephones, adresses):
        resultat = "=== DESCRIPTION DU SITE WEB ===\n\n"
        try:
            domain = urlparse(self.url).netloc
            title = self.soup.find('title').get_text(strip=True) if self.soup.find('title') else "Sans titre"

            meta_description = ""
            meta_tag = self.soup.find('meta', attrs={'name': re.compile(r'description', re.I)})
            if meta_tag and meta_tag.get('content'):
                meta_description = meta_tag.get('content').strip()[:150]

            keywords = ""
            keywords_tag = self.soup.find('meta', attrs={'name': re.compile(r'keywords', re.I)})
            if keywords_tag and keywords_tag.get('content'):
                keywords = ", ".join(k.strip() for k in keywords_tag.get('content').strip().split(',')[:5])

            description = f"Le site {domain} ({title}) "
            description += f"est un site web dédié à {meta_description.lower()} " if meta_description else "offre du contenu sans description meta spécifique. "
            description += f"avec des thématiques clés telles que {keywords}. " if keywords else "sans thématiques spécifiques identifiées. "

            total_pii = len(emails) + len(telephones) + len(adresses)
            if total_pii > 0:
                description += f"Il contient {total_pii} information(s) personnelle(s) ({len(emails)} email(s), {len(telephones)} numéro(s) de téléphone, {len(adresses)} adresse(s))."
            else:
                description += "Aucune information personnelle n'a été détectée."

            resultat += description + "\n"
        except Exception as e:
            resultat += f"Erreur lors de la génération de la description : {str(e)}\n"
        return resultat


class ExtracteurPII(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.extraction_thread = None

    def initUI(self):
        layout = QVBoxLayout()
        title = QLabel("Extracteur d'Informations Personnelles (PII)")
        title.setStyleSheet("font-weight: bold; font-size: 16px;")
        layout.addWidget(title)

        url_layout = QHBoxLayout()
        self.url_label = QLabel("URL du site web :")
        url_layout.addWidget(self.url_label)

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://example.com")
        self.url_input.returnPressed.connect(self.extraire_informations)
        url_layout.addWidget(self.url_input)
        layout.addLayout(url_layout)

        self.extract_button = QPushButton("Extraire les informations")
        self.extract_button.clicked.connect(self.extraire_informations)
        self.extract_button.setStyleSheet("QPushButton { background-color: #4CAF50; color: white; }")
        layout.addWidget(self.extract_button)

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        self.output = QTextEdit()
        self.output.setReadOnly(True)
        layout.addWidget(self.output)

        self.setLayout(layout)
        self.setWindowTitle("Extracteur d'informations PII - Tunisie")
        self.setGeometry(300, 300, 900, 600)

    def valider_url(self, url):
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False

    def extraire_informations(self):
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "Erreur", "Veuillez entrer une URL valide.")
            return
        if not self.valider_url(url):
            QMessageBox.warning(self, "Erreur", "URL invalide. Format requis: https://example.com")
            return

        self.extract_button.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)

        self.extraction_thread = ExtractionThread(url)
        self.extraction_thread.finished.connect(self.extraction_terminee)
        self.extraction_thread.progress.connect(self.progress_bar.setValue)
        self.extraction_thread.error.connect(self.afficher_erreur)
        self.extraction_thread.start()

    def extraction_terminee(self, resultat):
        self.output.setText(resultat)
        self.extract_button.setEnabled(True)
        self.progress_bar.setVisible(False)

    def afficher_erreur(self, message):
        self.output.setText(message)
        self.extract_button.setEnabled(True)
        self.progress_bar.setVisible(False)
        QMessageBox.critical(self, "Erreur", message)

    def closeEvent(self, event):
        if self.extraction_thread and self.extraction_thread.isRunning():
            self.extraction_thread.terminate()
            self.extraction_thread.wait()
        event.accept()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ExtracteurPII()
    ex.show()
    sys.exit(app.exec_())
