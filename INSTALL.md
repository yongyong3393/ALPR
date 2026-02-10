# Install (CPU OCR)

Use Python 3.12.

```
python -m pip install --upgrade pip
python -m pip install PySide6
python -m pip install torch torchvision --index-url https://download.pytorch.org/whl/cu126
python -m pip install ultralytics
python -m pip install paddlepaddle==3.3.0
python -m pip install paddleocr==3.3.0 paddlex==3.3.0
```

Run:
```
python -m main.app
```
