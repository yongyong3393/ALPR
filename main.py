from yolo_detector import load_yolo
from ocr_module import OCRWorker
from streamer import VideoStream
from ui import UIManager

weight_path = "./yolo_weight/best.pt"

def main():

    '''
    Initialize modules
    '''

    # 1. Load yolov5 model
    model = load_yolo(weight_path)

    # 2. Load OCR worker
    ocr_worker = OCRWorker(lang="korean")
    ocr_worker.start()

    # 3. Load webcam stream
    stream = VideoStream()

    # 4. Load UI manager
    ui = UIManager(window_name="Webcam")

    '''
    main loop
    '''
    frame_idx = 0
    N = 60 # Process every N frames

    while True:
        # 1. Read frame from webcam stream
        ok, frame = stream.read()
        if not ok:
            print("[ERROR] Cannot read a frame from webcam")
            break
        
        # 2. ALPR every N frames
        frame_idx += 1
        if frame_idx % N == 0:
            ocr_worker.submit_frame(frame)

        # 3. Get latest OCR results
        text = ocr_worker.get_latest_text()

        # 4. Visualize results on UI
        key = ui.show(frame, text)
        if key == ord('q'):
            break
    
    ''' Cleanup '''
    ocr_worker.stop()
    stream.release()
    ui.destroy()

if __name__ == "__main__":
    main()