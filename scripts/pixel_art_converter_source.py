import os
import time
import threading
import tkinter as tk
from tkinter import ttk, scrolledtext
import subprocess
import google.generativeai as genai
from PIL import Image, ImageTk

# --- CONFIGURATION ---
API_KEY = "AIzaSyBpocfPTrpckhNWe6vneT9y5bsyIk3VD0o"
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('nano-banana-pro-preview')

PROMPT_MAESTRO = (
    "Extract a vibrant, 256-color indexed palette for this 16-bit arcade sprite. "
    "The style must mimic top-tier assets from the Neo-Geo era. "
    "Clean, hand-placed-looking pixels with professional shading. "
    "No modern gradients; all detail via precise pixel clustering. "
    "Return exactly 256 hex color codes separated by commas."
)

class PixelArtApp:
    def __init__(self, root, input_dir, output_dir):
        self.root = root
        self.root.title("Nano Banana Pixel Art Converter")
        self.root.geometry("900x700")
        self.root.configure(bg="#1e1e2e")

        self.input_dir = input_dir
        self.output_dir = output_dir
        
        self.setup_ui()
        self.is_running = False
        self.conversions_count = 0

    def setup_ui(self):
        # Header
        header = tk.Label(self.root, text="B A N A N A   P I X E L   A R T", 
                         font=("Courier", 24, "bold"), fg="#f9e2af", bg="#1e1e2e")
        header.pack(pady=20)

        # Progress Frame
        prog_frame = tk.Frame(self.root, bg="#1e1e2e")
        prog_frame.pack(fill="x", padx=40)

        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(prog_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill="x", pady=10)

        self.status_label = tk.Label(prog_frame, text="Ready to start...", 
                                   font=("Arial", 12), fg="#cdd6f4", bg="#1e1e2e")
        self.status_label.pack()

        # Images Frame (Side by Side Preview)
        img_frame = tk.Frame(self.root, bg="#1e1e2e")
        img_frame.pack(pady=20)

        self.orig_canvas = tk.Label(img_frame, text="Original", bg="#313244", width=32, height=16)
        self.orig_canvas.grid(row=0, column=0, padx=10)

        arrow = tk.Label(img_frame, text="➔", font=("Arial", 30), fg="#f9e2af", bg="#1e1e2e")
        arrow.grid(row=0, column=1)

        self.pixel_canvas = tk.Label(img_frame, text="Pixel Art", bg="#313244", width=32, height=16)
        self.pixel_canvas.grid(row=0, column=2, padx=10)

        # Log Area
        self.log_area = scrolledtext.ScrolledText(self.root, height=10, 
                                                bg="#181825", fg="#a6adc8", font=("Consolas", 10))
        self.log_area.pack(fill="both", padx=40, pady=20)

        # Controls
        self.start_btn = tk.Button(self.root, text="START CONVERSION", command=self.start_process,
                                 bg="#a6e3a1", fg="#11111b", font=("Arial", 12, "bold"), padx=20)
        self.start_btn.pack(pady=10)

    def log(self, message):
        self.log_area.insert(tk.END, message + "\n")
        self.log_area.see(tk.END)

    def update_previews(self, orig_path, result_path):
        # Load and resize for preview
        orig_img = Image.open(orig_path).resize((256, 256), Image.NEAREST)
        result_img = Image.open(result_path).resize((256, 256), Image.NEAREST)

        self.orig_photo = ImageTk.PhotoImage(orig_img)
        self.result_photo = ImageTk.PhotoImage(result_img)

        self.orig_canvas.config(image=self.orig_photo, text="")
        self.pixel_canvas.config(image=self.result_photo, text="")

    def get_ai_palette(self, image_path):
        try:
            img = Image.open(image_path).convert("RGB")
            response = model.generate_content([PROMPT_MAESTRO, img])
            hex_colors = [c.strip() for c in response.text.replace("\n", "").split(",") if "#" in c]
            if len(hex_colors) < 16: return None
            rgb_palette = []
            for hex_code in hex_colors[:256]:
                h = hex_code.lstrip('#').strip()
                if len(h) == 6:
                    try: rgb_palette.append(tuple(int(h[i:i+2], 16) for i in (0, 2, 4)))
                    except: continue
            return rgb_palette
        except Exception as e:
            self.log(f"AI Quota/Error: {e}")
            return None

    def convert_to_pixel_art(self, input_path, output_path, pixel_size=64):
        with Image.open(input_path) as img:
            img = img.convert("RGBA")
            small_img = img.resize((pixel_size, pixel_size), Image.Resampling.LANCZOS)
            palette = self.get_ai_palette(input_path)
            if palette:
                palette_img = Image.new("P", (1, 1))
                palette_list = [c for rgb in palette for c in rgb]
                palette_list += [0] * (768 - len(palette_list))
                palette_img.putpalette(palette_list)
                quantized = small_img.convert("RGB").quantize(palette=palette_img, dither=Image.Dither.NONE)
            else:
                quantized = small_img.convert("RGB").quantize(colors=256, dither=Image.Dither.NONE)
            
            alpha = small_img.split()[3].point(lambda x: 255 if x > 128 else 0)
            pixel_art_base = quantized.convert("RGBA")
            pixel_art_base.putalpha(alpha)
            pixel_art = pixel_art_base.resize(img.size, Image.NEAREST)
            pixel_art.save(output_path)

    def start_process(self):
        if not self.is_running:
            self.is_running = True
            self.start_btn.config(state="disabled", text="PROCESSING...")
            threading.Thread(target=self.worker_thread, daemon=True).start()

    def sync_to_github(self):
        self.log("📡 Triggering Auto-Sync to GitHub...")
        try:
            # 1. Organize
            script_path = os.path.join(self.output_dir, "scripts", "organize.py")
            if os.path.exists(script_path):
                subprocess.run(["py", script_path], cwd=self.output_dir, check=True)
                self.log("✅ Organization complete.")
            
            # 2. Git Sync
            subprocess.run(["git", "add", "."], cwd=self.output_dir, check=True)
            subprocess.run(["git", "commit", "-m", "Auto-sync: 20 new assets"], cwd=self.output_dir, check=True)
            # Run push in a separate thread to not block the converter if it's slow
            threading.Thread(target=lambda: subprocess.run(["git", "push"], cwd=self.output_dir)).start()
            self.log("🚀 Git Push started in background.")
        except Exception as e:
            self.log(f"⚠️ Sync failed: {e}")

    def worker_thread(self):
        if not os.path.exists(self.output_dir): os.makedirs(self.output_dir)
        files = [f for f in os.listdir(self.input_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        existing_meta = set()
        
        # Load existing from meta.json to avoid duplicates even if moved
        meta_file = os.path.join(self.output_dir, "meta.json")
        if os.path.exists(meta_file):
            with open(meta_file, 'r') as f:
                import json
                data = json.load(f)
                existing_meta = {os.path.basename(i['file_name']) for i in data.get('items', [])}

        files_to_do = [f for f in files if f not in existing_meta][:1500]
        
        total = len(files_to_do)
        self.log(f"Found {total} images to process for today.")

        for i, f in enumerate(files_to_do):
            in_path = os.path.join(self.input_dir, f)
            out_path = os.path.join(self.output_dir, f)
            
            try:
                self.convert_to_pixel_art(in_path, out_path)
                self.root.after(0, self.update_previews, in_path, out_path)
                
                self.conversions_count += 1
                percent = ((i+1) / total) * 100
                self.progress_var.set(percent)
                self.status_label.config(text=f"Processed image {i+1} of {total}: {f}")
                self.log(f"✓ {f} finished.")

                if self.conversions_count >= 20:
                    self.sync_to_github()
                    self.conversions_count = 0
                
            except Exception as e:
                self.log(f"❌ Error in {f}: {e}")
            
            time.sleep(10) # 10s Delay as requested
        
        # Final sync for any remaining
        if self.conversions_count > 0:
            self.sync_to_github()

        self.log("Batch complete for today!")
        self.status_label.config(text="All done for today!")
        self.is_running = False
        self.start_btn.config(state="normal", text="START CONVERSION")

if __name__ == "__main__":
    BASE_DIR = r"C:\Users\usuario\Downloads\size-256-55she7\size-256"
    root = tk.Tk()
    app = PixelArtApp(root, os.path.join(BASE_DIR, "images"), os.path.join(BASE_DIR, "pixel_art_final"))
    root.mainloop()
