# 🌐 Web PII Extractor

![Python](https://img.shields.io/badge/Python-3.7%2B-blue)
![PyQt5](https://img.shields.io/badge/PyQt5-5.15%2B-purple)
![BeautifulSoup4](https://img.shields.io/badge/BeautifulSoup4-4.9%2B-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

An intelligent tool to extract Personal Identifiable Information (PII) from websites, optimized for Tunisian contact formats. Ideal for web scraping professionals, researchers, and data analysts.

## ✨ Features

### 📧 Multi-format Extraction
- **Emails**: Detect email addresses throughout sites
- **Phone Numbers**: Tunisian (+216 XX XXX XXX) & international formats
- **Addresses**: Physical addresses with Tunisian city recognition
- **Contact Info**: Structured contact information

### 🖥️ Professional Interface
- **PyQt5 GUI**: Modern, responsive design
- **Progress Bar**: Real-time extraction tracking
- **Threading**: Asynchronous processing
- **Easy Export**: Direct copy of results

### 🌍 Tunisian Specialization
- **Local formats**: Tunisian phone numbers
- **Tunisian cities**: Recognition of Tunisian city names
- **Address formats**: Understanding of local address patterns
- **Arabic support**: Arabic character handling

## 🚀 Quick Installation

```bash
# Clone repository
git clone https://github.com/omarbadrani/web-pii-extractor.git
cd web-pii-extractor

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate
# Activate (Linux/Mac)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## 🎮 Basic Usage

1. **Launch the application:**
```bash
python pii_extractor.py
```

2. **Enter website URL** (e.g., `https://example.tn`)

3. **Click "Extract Information"**

4. **View results** in the output area

## ⚙️ Key Configuration

Edit in `pii_extractor.py`:
```python
# Email pattern
email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'

# Tunisian phone pattern
phone_pattern = r'(?:\+|00)?216\s*[2-9]\d{1}\s*(?:\d{2}[\s\-.]?){3}'

# Timeout settings
TIMEOUT = 15  # seconds
RETRIES = 3
```

## 📊 Performance

| Site Type | Avg. Time | Data Extracted |
|-----------|-----------|----------------|
| Small (<1MB) | 2-5s | Emails: 1-3, Phones: 0-2 |
| Medium (1-5MB) | 5-10s | Emails: 3-10, Phones: 2-5 |
| Large (>5MB) | 10-20s | Emails: 10-50+, Phones: 5-20+ |

## 🛡️ Ethical Usage

- **Respect robots.txt** and website terms
- **Limit request rates** to avoid server overload
- **Use legally** - only extract publicly available data
- **Comply with GDPR/local laws**

## 📁 Project Structure
```
web-pii-extractor/
├── pii_extractor.py      # Main application
├── requirements.txt      # Dependencies
├── README.md            # Documentation
└── LICENSE              # MIT License
```

## 🔧 Troubleshooting

### Common Issues:
- **Connection errors**: Check internet/proxy settings
- **No data found**: Verify site contains contact information
- **Timeout**: Increase TIMEOUT value or check connection speed

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## 👤 Author

**omar badrani**  
- GitHub: https://github.com/omarbadrani  
- Email: omarbadrani770@gmail.com

---

**Note**: This tool is for educational/research purposes. Users must comply with applicable laws regarding data protection and intellectual property.

⭐ **If this tool is helpful, please star the repository!** ⭐
