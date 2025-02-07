import pytesseract
import tkinter as tk
import pyautogui
import numpy as np
import cv2

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

capture_area = None


def select_image():
    """Chat area selector"""
    overlay = tk.Tk()
    overlay.attributes("-fullscreen", True)
    overlay.attributes("-alpha", 0.3)
    overlay.configure(bg="black")
    canvas = tk.Canvas(overlay, bg="black", highlightthickness=0)
    canvas.pack(fill=tk.BOTH, expand=True)

    rect_id = None

    def on_mouse_press(event):
        nonlocal rect_id
        select_image.start_x, select_image.start_y = event.x, event.y
        rect_id = canvas.create_rectangle(event.x, event.y, event.x, event.y, outline="red", width=2)

    def on_mouse_drag(event):
        """Update rectangle as mouse moves"""
        canvas.coords(rect_id, select_image.start_x, select_image.start_y, event.x, event.y)

    def on_mouse_release(event):
        global capture_area
        end_x, end_y = event.x, event.y

        x1, y1 = min(select_image.start_x, end_x), min(select_image.start_y, end_y)
        x2, y2 = max(select_image.start_x, end_x), max(select_image.start_y, end_y)
        
        capture_area = (x1, y1, x2 - x1, y2 - y1)
        
        overlay.destroy()
        print(f"Captured area: {capture_area}")
        bot_logic()  # Automatically extract text after area selection

    canvas.bind("<ButtonPress-1>", on_mouse_press)
    canvas.bind("<B1-Motion>", on_mouse_drag)
    canvas.bind("<ButtonRelease-1>", on_mouse_release)

    overlay.mainloop()


def bot_logic():
    """Captures the image from selected area and extracts text with better accuracy."""
    global capture_area
    if capture_area is None:
        print("No image area defined. Select an area.")
        return

    screenshot = pyautogui.screenshot(region=capture_area)
    screenshot_array = np.array(screenshot)
    
    gray = cv2.cvtColor(screenshot_array, cv2.COLOR_BGR2GRAY)

    gray = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 2)

    scale_factor = 2  # Increase resolution
    gray = cv2.resize(gray, (gray.shape[1] * scale_factor, gray.shape[0] * scale_factor), interpolation=cv2.INTER_LINEAR)

    # OCR Configuration - Use the best OCR mode for accuracy
    custom_config = r'--oem 3 --psm 6'

    text = pytesseract.image_to_string(gray, lang='eng', config=custom_config)
    
    print("\nExtracted Text:\n", text)

    text_area.config(state=tk.NORMAL)
    text_area.delete("1.0", tk.END)
    text_area.insert(tk.END, text)
    text_area.config(state=tk.DISABLED)


def copy_text():
    """Copy text from the text area to clipboard"""
    root.clipboard_clear()
    root.clipboard_append(text_area.get("1.0", tk.END).strip())
    root.update()


def start_gui():
    """Main GUI window"""
    global text_area, root

    root = tk.Tk()
    root.title("Image To Text")
    root.geometry("300x300")

    root.columnconfigure(0, weight=1)
    root.rowconfigure(1, weight=1)

    set_image_frame = tk.LabelFrame(root, text="Image to Text", padx=10, pady=10, font=("Arial", 10, "bold"))
    set_image_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

    set_image_button = tk.Button(set_image_frame, text="Select Image to Convert to Text", command=select_image, font=("Arial", 10))
    set_image_button.pack(pady=5)

    text_frame = tk.Frame(root)
    text_frame.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

    text_frame.columnconfigure(0, weight=1)
    text_frame.rowconfigure(0, weight=1)

    text_area = tk.Text(text_frame, wrap=tk.WORD, font=("Arial", 10))
    text_area.config(state=tk.DISABLED)
    text_area.grid(row=0, column=0, sticky="nsew")

    scrollbar = tk.Scrollbar(text_frame, command=text_area.yview)
    scrollbar.grid(row=0, column=1, sticky="ns")
    text_area.config(yscrollcommand=scrollbar.set)

    copy_button = tk.Button(root, text="Copy Text", command=copy_text, font=("Arial", 10, "bold"))
    copy_button.grid(row=2, column=0, pady=10)

    root.mainloop()


if __name__ == "__main__":
    start_gui()
