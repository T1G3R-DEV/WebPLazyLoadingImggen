import os
from PIL import Image
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext

def generate_images(inputs):
    folder = os.path.dirname(inputs[0]) if len(inputs) == 1 else os.path.commonpath(inputs)
    preview_folder = os.path.join(folder, "previews")
    os.makedirs(preview_folder, exist_ok=True)

    html_blocks = []

    for input_path in inputs:
        filename = os.path.basename(input_path)
        base_name, _ = os.path.splitext(filename)

        try:
            with Image.open(input_path) as img:
                # Use original size; just compress
                tiny_path = os.path.join(preview_folder, f"{base_name}-tiny.webp")
                small_path = os.path.join(preview_folder, f"{base_name}-small.webp")
                full_path = os.path.join(preview_folder, f"{base_name}-full.webp")

                img.save(tiny_path, "WEBP", quality=10)
                img.save(small_path, "WEBP", quality=40)
                img.save(full_path, "WEBP", quality=85)

            html_blocks.append(f'''
<a href="{input_path}">
  <img
    src="previews/{base_name}-tiny.webp"
    data-src1="previews/{base_name}-small.webp"
    data-src2="previews/{base_name}-full.webp"
    alt="{filename}"
    loading="lazy"
    style="max-width: 100%; height: auto;"
    class="progressive-image"
  />
</a>
''')
        except Exception as e:
            print(f"Failed to process {input_path}: {e}")

    # Full HTML (optional use)
    html_output = f"""<script>
function loadHighResImages() {{
  const images = document.querySelectorAll("img.progressive-image");
  images.forEach(img => {{
    const small = img.dataset.src1;
    const full = img.dataset.src2;

    const smallImg = new Image();
    smallImg.src = small;
    smallImg.onload = () => {{
      img.src = small;
      img.classList.add("loaded");

      const fullImg = new Image();
      fullImg.src = full;
      fullImg.onload = () => {{
        img.src = full;
      }};
    }};
  }});
}}
document.addEventListener("DOMContentLoaded", loadHighResImages);
</script>

""" + "\n".join(html_blocks)

    return html_output

# === GUI Setup ===
def select_files_or_folder():
    options = [('Image files', '*.jpg *.jpeg *.png *.webp')]
    files = filedialog.askopenfilenames(title="Select images", filetypes=options)
    if not files:
        folder = filedialog.askdirectory(title="Or select a folder")
        if not folder:
            return
        # All matching images in the folder
        files = [os.path.join(folder, f) for f in os.listdir(folder)
                 if f.lower().endswith((".jpg", ".jpeg", ".png", ".webp"))]

    selected_path.set(f"{len(files)} file(s) selected")
    try:
        html = generate_images(files)
        html_textbox.delete("1.0", tk.END)
        html_textbox.insert(tk.END, html)
        messagebox.showinfo("Done", "Images processed and HTML generated.")
    except Exception as e:
        messagebox.showerror("Error", f"Something went wrong:\n{e}")

# === GUI ===
app = tk.Tk()
app.title("WebP Lazy Gallery Generator")
app.geometry("700x600")
app.resizable(True, True)

tk.Label(app, text="Select image files or folder:", font=("Arial", 12)).pack(pady=10)
tk.Button(app, text="Select Files or Folder", command=select_files_or_folder, bg="#4CAF50", fg="white").pack()

selected_path = tk.StringVar()
tk.Label(app, textvariable=selected_path, fg="blue").pack(pady=5)

tk.Label(app, text="Generated HTML (copy into your site):").pack()
html_textbox = scrolledtext.ScrolledText(app, wrap=tk.WORD, width=80, height=25)
html_textbox.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

app.mainloop()
