import re
from paddleocr import PaddleOCR

class OCR:
    """
    OCR Module using PaddleOCR.
    """

    def __init__(self):
        self.model = PaddleOCR(lang="korean", device="cpu")

    def detect(self, plate_crop) -> str:
        result = self.model.predict(input=plate_crop)
        if not result:
            return None
        rec_texts = result[0].get("rec_texts", [])
        if not rec_texts:
            return None
        return self._extract_plate_text(rec_texts)

    @staticmethod
    def _extract_plate_text(rec_texts):
        raw = "".join(rec_texts)
        cleaned = re.sub(r"[\s-]+", "", raw)
        match = re.search(r"\d{2,3}[가-힣]\d{4}", cleaned)
        if match:
            return match.group(0)
        return None
