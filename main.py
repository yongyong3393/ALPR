from alpr_worker import ALPRWorker
from video_stream import VideoStream
from ui_manager import UIManager

def main():

    '''
    Initialize modules
    '''

    # 1. Load ALPR worker (YOLO + OCR)
    alpr_worker = ALPRWorker()
    alpr_worker.start()

    # 2. Load webcam stream
    stream = VideoStream()

    # 3. Load UI manager
    ui_manager = UIManager(window_name="Webcam")

    '''
    main loop
    '''
    frame_idx = 0
    N = 60 # Process every N frames
    frame = None
    last_box = None
    last_text = None

    while True:
        # 1. Read frame from webcam stream
        ok, frame = stream.read()
        if not ok:
            print("[ERROR] Cannot read a frame from webcam")
            break
        
        # 2. ALPR every N frames
        frame_idx += 1
        if frame_idx % N == 0:
            alpr_worker.submit_frame(frame)

        # 3. Get latest OCR results
        last_box, last_text = alpr_worker.get_latest_result()

        # 4. Visualize results on UI
        key = ui_manager.show(frame, last_box, last_text)
        if key == ord('q'):
            break
    
    ''' Cleanup '''
    alpr_worker.stop()
    stream.release()
    ui_manager.destroy()

if __name__ == "__main__":
    main()