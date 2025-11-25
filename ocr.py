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
        if rec_texts:
            # TODO: 문자열 처리 로직 수정. 현재는 여러 줄이면 이어 붙이는 로직만 추가
            return "".join(rec_texts)
        else:
            return None