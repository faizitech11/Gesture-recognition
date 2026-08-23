import threading
import time
import cv2
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from pycaw.pycaw import AudioUtilities
import customtkinter as ctk
from PIL import Image
import keyboard

# Appearance Settings
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class AdvancedGestureApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Smart Media Gesture Controller")
        self.geometry("950x650")
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.is_running = True
        self.overlay_window = None
        self.last_action_time = 0  # Cooldown timer to prevent rapid triggers

        # --- PyCaw Audio Setup ---
        devices = AudioUtilities.GetSpeakers()
        volume_device = devices.EndpointVolume
        vol_range = volume_device.GetVolumeRange()
        self.min_vol, self.max_vol = vol_range[0], vol_range[1]
        self.volume_device = volume_device

        # --- MediaPipe Setup (Detects up to 2 Hands) ---
        base_options = python.BaseOptions(model_asset_path='hand_landmarker.task')
        options = vision.HandLandmarkerOptions(base_options=base_options, num_hands=2)
        self.detector = vision.HandLandmarker.create_from_options(options)

        self._build_ui()

        # Start Camera Processing Thread
        self.thread = threading.Thread(target=self._process_camera, daemon=True)
        self.thread.start()

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Video Display Area
        self.video_frame = ctk.CTkFrame(self, corner_radius=15)
        self.video_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")
        
        self.video_label = ctk.CTkLabel(self.video_frame, text="Loading Camera Feed...")
        self.video_label.pack(expand=True, fill="both", padx=10, pady=10)

        # Side Control Panel
        self.panel = ctk.CTkFrame(self, corner_radius=15)
        self.panel.grid(row=0, column=1, padx=(0, 20), pady=20, sticky="nsew")

        self.title_label = ctk.CTkLabel(self.panel, text="Control Center", font=ctk.CTkFont(size=20, weight="bold"))
        self.title_label.pack(pady=(20, 10))

        self.vol_label = ctk.CTkLabel(self.panel, text="Volume: 0%", font=ctk.CTkFont(size=16))
        self.vol_label.pack(pady=10)

        self.progress_bar = ctk.CTkProgressBar(self.panel, orientation="vertical", height=200, width=25)
        self.progress_bar.set(0)
        self.progress_bar.pack(pady=10)

        self.gesture_status = ctk.CTkLabel(self.panel, text="Gesture: None", font=ctk.CTkFont(size=14, weight="bold"), text_color="#00FF99")
        self.gesture_status.pack(pady=10)

        self.status_label = ctk.CTkLabel(
            self.panel, 
            text="• Right Hand: Next Song\n• Left Hand: Prev Song\n• Index Tilt: Fast Seek\n• High-Five: Lock Screen", 
            font=ctk.CTkFont(size=11), 
            text_color="gray", 
            justify="left"
        )
        self.status_label.pack(side="bottom", pady=20)

    def _is_high_five(self, hand_landmarks):
        """Detect open palm (High-Five)."""
        tips = [4, 8, 12, 16, 20]
        pips = [2, 6, 10, 14, 18]
        return sum(1 for tip, pip in zip(tips, pips) if hand_landmarks[tip].y < hand_landmarks[pip].y) == 5

    def _is_only_index(self, hand_landmarks):
        """Check if ONLY Index finger is raised."""
        index_up = hand_landmarks[8].y < hand_landmarks[6].y
        others_down = (hand_landmarks[12].y > hand_landmarks[10].y and 
                       hand_landmarks[16].y > hand_landmarks[14].y and 
                       hand_landmarks[20].y > hand_landmarks[18].y)
        return index_up and others_down

    def _trigger_black_screen(self):
        """Opens fullscreen black overlay."""
        if self.overlay_window is not None and self.overlay_window.winfo_exists():
            return
        self.overlay_window = ctk.CTkToplevel(self)
        self.overlay_window.attributes("-fullscreen", True)
        self.overlay_window.configure(fg_color="black")
        self.overlay_window.attributes("-topmost", True)
        self.overlay_window.bind("<Escape>", lambda e: self.overlay_window.destroy())
        self.overlay_window.bind("<Button-1>", lambda e: self.overlay_window.destroy())

    def _process_camera(self):
        cap = cv2.VideoCapture(0)

        while self.is_running and cap.isOpened():
            success, img = cap.read()
            if not success:
                continue

            img = cv2.flip(img, 1)
            h, w, _ = img.shape
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=img_rgb)

            detection_result = self.detector.detect(mp_image)
            current_time = time.time()
            current_gesture_text = "None"

            if detection_result.hand_landmarks and detection_result.handedness:
                for idx, hand_landmarks in enumerate(detection_result.hand_landmarks):
                    hand_label = detection_result.handedness[idx][0].category_name

                    # 1. High-Five Screen Lock
                    if self._is_high_five(hand_landmarks):
                        self.after(0, self._trigger_black_screen)
                        current_gesture_text = "High-Five (Lock)"

                    # 2. Index Finger Seek Control (Forward / Rewind)
                    elif self._is_only_index(hand_landmarks):
                        index_tip = hand_landmarks[8]
                        index_base = hand_landmarks[5]
                        dx = index_tip.x - index_base.x

                        if dx > 0.08:  # Tilt Right -> Seek Forward
                            current_gesture_text = "Seeking Forward >>"
                            if current_time - self.last_action_time > 0.3:
                                keyboard.send("right")
                                self.last_action_time = current_time

                        elif dx < -0.08:  # Tilt Left -> Rewind
                            current_gesture_text = "Rewinding <<"
                            if current_time - self.last_action_time > 0.3:
                                keyboard.send("left")
                                self.last_action_time = current_time

                    # 3. Next / Previous Song (Right or Left Hand Pointing)
                    elif current_time - self.last_action_time > 1.2:
                        if hand_label == "Right" and hand_landmarks[8].y < hand_landmarks[6].y:
                            keyboard.send("next track")
                            current_gesture_text = "Next Track (Right Hand)"
                            self.last_action_time = current_time

                        elif hand_label == "Left" and hand_landmarks[8].y < hand_landmarks[6].y:
                            keyboard.send("previous track")
                            current_gesture_text = "Previous Track (Left Hand)"
                            self.last_action_time = current_time

                    # 4. Pinch Volume Logic (Default Gesture)
                    thumb = hand_landmarks[4]
                    index = hand_landmarks[8]
                    x1, y1 = int(thumb.x * w), int(thumb.y * h)
                    x2, y2 = int(index.x * w), int(index.y * h)

                    cv2.circle(img_rgb, (x1, y1), 6, (0, 255, 150), cv2.FILLED)
                    cv2.circle(img_rgb, (x2, y2), 6, (0, 255, 150), cv2.FILLED)
                    cv2.line(img_rgb, (x1, y1), (x2, y2), (0, 150, 255), 2)

                    length = np.hypot(x2 - x1, y2 - y1)
                    vol = np.interp(length, [20, 180], [self.min_vol, self.max_vol])
                    vol_per = np.interp(length, [20, 180], [0, 100])

                    self.volume_device.SetMasterVolumeLevel(vol, None)
                    self.after(0, lambda p=vol_per: self.vol_label.configure(text=f"Volume: {int(p)}%"))
                    self.after(0, lambda p=vol_per: self.progress_bar.set(p / 100))

            # Update status GUI
            self.after(0, lambda t=current_gesture_text: self.gesture_status.configure(text=f"Gesture: {t}"))

            # Render frame using CTkImage (High DPI display support)
            img_pil = Image.fromarray(img_rgb)
            ctk_img = ctk.CTkImage(light_image=img_pil, dark_image=img_pil, size=(640, 480))
            self.after(0, lambda i=ctk_img: self._update_video_feed(i))
            time.sleep(0.01)

        cap.release()

    def _update_video_feed(self, ctk_img):
        self.video_label.configure(image=ctk_img, text="")

    def on_closing(self):
        self.is_running = False
        self.destroy()

if __name__ == "__main__":
    app = AdvancedGestureApp()
    app.mainloop()