import easyocr
import re
import cv2
import numpy as np
from PIL import Image
import io


# ---------------------------------------------------------
# 1. Character Sets & Config
# ---------------------------------------------------------

DEVANAGARI_CHARS = set([
    '०', '१', '२', '३', '४', '५', '६', '७', '८', '९',
    'ा', 'ी', 'स', 'ँ', 'अ',
    'क','ख','ग','घ','ङ','च','छ','ज','झ','ञ',
    'ट','ठ','ड','ढ','ण','त','थ','द','ध','न',
    'प','फ','ब','भ','म','य','र','ल','व','श',
    'ष','स','ह'
])

LATIN_CHARS = set('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')

PROVINCES = [
    "BAGMATI","KOSHI","GANDAKI",
    "KARNALI", "LUMBINI", "SUDURPASHCHIM", "MADHESH"
]

CONFUSION_MAP = {
    '0': ['O', 'Q', 'D'],
    '1': ['I', 'L', '|'],
    '2': ['Z'],
    '5': ['S'],
    '6': ['G', 'C'],
    '8': ['B'],
    '9': ['g'],

    'O': ['0'],
    'I': ['1', 'l'],
    'S': ['5'],
    'B': ['8'],
    'G': ['6'],
    'Z': ['2'],
    'D': ['0'],
    'Q': ['0']
}


# ---------------------------------------------------------
# 2. Initialize OCR Reader (global for speed)
# ---------------------------------------------------------

READER = easyocr.Reader(['en', 'ne'], gpu=False)


# ---------------------------------------------------------
# 3. Utility Cleaning + Correction
# ---------------------------------------------------------

def clean_input(text):
    text = text.upper()
    text = re.sub(r'[^A-Z0-9]', '', text)

    for p in PROVINCES:
        text = text.replace(p, "")

    text = text.replace("NEP", "")
    return text


def correct_plate(text: str):
    """
    Corrects AAA#### pattern using confusion map.
    Returns: (plate_str_or_None, success_bool)
    """


    text = text[:7]
    corrected = list(text)

    # First 3 = letters
    for i in range(3):
        c = corrected[i]
        if c.isdigit():
            for letter, confused_with in CONFUSION_MAP.items():
                if letter.isalpha() and c in confused_with:
                    corrected[i] = letter
                    break

    # Last 4 = digits
    for i in range(3, 7):
        c = corrected[i]
        if c.isalpha():
            for number, confused_with in CONFUSION_MAP.items():
                if number.isdigit() and c in confused_with:
                    corrected[i] = number
                    break

    final = "".join(corrected)



    return final, True


# ---------------------------------------------------------
# 4. Classifier (Devanagari vs Embossed)
# ---------------------------------------------------------

def classify_text(raw_text: str) -> str:
    devanagari = sum(c in DEVANAGARI_CHARS for c in raw_text)
    latin = sum(c in LATIN_CHARS for c in raw_text)

    if devanagari == 0 and latin == 0:
        return "UNKNOWN"
    devanagari_ratio = devanagari / (devanagari + latin)

    if devanagari_ratio > 0.3:
        return "DEVANAGARI"

    return "EMBOSSED"


# ---------------------------------------------------------
# 5. Main Django-Friendly API
# ---------------------------------------------------------

def extract_nepali_plate(image_file) -> str | None:
    """
    Django-friendly function.
    image_file → Django InMemoryUpload OR raw bytes.

    Returns:
        - 7-char embossed Nepali plate (e.g., CAB1321)
        - None if not embossed or invalid
    """

    # ---- Load image ----
    if hasattr(image_file, "read"):
        img_bytes = image_file.read()
    else:
        img_bytes = image_file

    image = Image.open(io.BytesIO(img_bytes)).convert("RGB")
    img_np = np.array(image)
    img_bgr = cv2.cvtColor(img_np, cv2.COLOR_RGB2BGR)

    # ---- OCR ----
    results = READER.readtext(img_bgr, detail=0, paragraph=False)
    full_text = "".join(results).upper().replace(" ", "")

    if not full_text:
        return None

    # ---- Determine plate type ----
    plate_type = classify_text(full_text)

    if plate_type != "EMBOSSED":
        return None  # only return embossed plates

    # ---- Clean + correct embossed ----
    cleaned = clean_input(full_text)
    plate, ok = correct_plate(cleaned)

    return plate if ok else None
