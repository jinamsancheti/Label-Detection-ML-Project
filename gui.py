import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext
from PIL import Image, ImageTk
import os
import MLfunctions
import units_dict

class CustomStyle:
    BACKGROUND = "#89A8B2"      # Deep blue-gray
    FRAME_BG = "#B3C8CF"        # Darker blue-gray
    BUTTON_BG = "#3498DB"       # Bright blue
    BUTTON_HOVER = "#2980B9"    # Darker bright blue
    TEXT_COLOR = "#000000"      # Off-white
    ACCENT = "#E74C3C"          # Coral red
    SECONDARY_BG = "#2E4053"    # Slightly lighter than frame bg
    INPUT_BG = "#F1F0E8"        # Lighter shade for input fields
    BORDER_COLOR = "#F1F0E8"    # Subtle border color

    @staticmethod
    def apply_styles(root):
        
        style = ttk.Style()
        
        
        style.configure('Custom.TFrame', 
                       background=CustomStyle.FRAME_BG)
        
        style.configure('Custom.TLabelframe', 
                       background=CustomStyle.FRAME_BG)
        
        style.configure('Custom.TLabelframe.Label', 
                       background=CustomStyle.FRAME_BG,
                       foreground=CustomStyle.TEXT_COLOR,
                       font=('Sora', 11, 'bold'))
        
        
        style.configure('Custom.TButton',
                       background=CustomStyle.BUTTON_BG,
                       foreground=CustomStyle.TEXT_COLOR,
                       font=('Sora', 10, 'bold'),
                       padding=15,
                       relief='raised',
                       borderwidth=2)
        
        style.map('Custom.TButton',
                 background=[('active', CustomStyle.BUTTON_HOVER)],
                 foreground=[('active', CustomStyle.TEXT_COLOR)])
        
        
        style.configure('Custom.TCombobox',
                       background=CustomStyle.INPUT_BG,
                       foreground=CustomStyle.TEXT_COLOR,
                       fieldbackground=CustomStyle.INPUT_BG,
                       selectbackground=CustomStyle.BUTTON_BG,
                       selectforeground=CustomStyle.TEXT_COLOR,
                       padding=10)
        
        
        style.configure('Custom.TLabel',
                       background=CustomStyle.FRAME_BG,
                       foreground=CustomStyle.TEXT_COLOR,
                       font=('Sora', 10))
        
        
        root.configure(bg=CustomStyle.BACKGROUND)

class ImageTextExtractorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Text Extractor")
        self.root.geometry("1000x650")
        
        
        CustomStyle.apply_styles(root)
        
        
        padding_frame = ttk.Frame(root, style='Custom.TFrame')
        padding_frame.pack(expand=True, fill='both', padx=20, pady=20)
        
        
        self.selected_entity = tk.StringVar(value="Select entity")  # Set initial value
        self.image_path = None
        
        
        main_frame = ttk.Frame(padding_frame, padding="20", style='Custom.TFrame')
        main_frame.pack(fill='both', expand=True)
        
        
        self.create_header(main_frame)
        self.create_upload_section(main_frame)
        self.create_entity_selector(main_frame)
        self.create_preview_and_output_section(main_frame)
        self.create_process_button(main_frame)

    def create_header(self, parent):
        header_frame = ttk.Frame(parent, style='Custom.TFrame')
        header_frame.pack(fill='x', pady=(0, 20))
        
        header_label = ttk.Label(header_frame, 
                               text="Image Text Extractor",
                               style='Custom.TLabel',
                               font=('Sora', 16, 'bold'))
        header_label.pack()

    def create_upload_section(self, parent):
        upload_frame = ttk.LabelFrame(parent, text=" Image Upload ", 
                                    padding="15", style='Custom.TLabelframe')
        upload_frame.pack(fill='x', padx=50, pady=(0, 20))
        
        button_frame = ttk.Frame(upload_frame, style='Custom.TFrame')
        button_frame.pack(expand=True)
        
        upload_btn = ttk.Button(button_frame, text="Upload Image", 
                              command=self.upload_image, style='Custom.TButton')
        upload_btn.pack(side='left', padx=20)
        
        self.file_label = ttk.Label(button_frame, text="No file selected",
                                  style='Custom.TLabel')
        self.file_label.pack(side='left', padx=20)

    def on_entity_select(self, event):
        selected = self.selected_entity.get()
        print(f"Selected entity: {selected}")  # Debug print
        
        if self.image_path and selected != "Select entity":
            self.process_image_with_entity(self.image_path, selected)

    def process_image_with_entity(self, image_path, entity):
        try:
            ocr_text = MLfunctions.extract_ocr(image_path)
            post_pro_list = MLfunctions.postprocessing(ocr_text)
            # print(post_pro_list)
            match_unit_list = MLfunctions.match_units(post_pro_list, units_dict.units_dict, entity)
            # print("jinam12")
            # print(match_unit_list)
            final_output = MLfunctions.get_max(match_unit_list)
            # Update output text
            self.output_text.delete(1.0, tk.END)
            self.output_text.insert(tk.END, f"Processing results for {entity}:\n")
            self.output_text.insert(tk.END, f"Matched units: {final_output}\n")
            
        except Exception as e:
            self.output_text.delete(1.0, tk.END)
            self.output_text.insert(tk.END, f"Error processing image: {str(e)}")

    def create_entity_selector(self, parent):
        entity_frame = ttk.LabelFrame(parent, text=" Select Entity ", 
                                    padding="15", style='Custom.TLabelframe')
        entity_frame.pack(fill='x', padx=50, pady=(0, 20))
        
        entities = ['width', 'depth', 'height', 'item_weight', 
                   'maximum_weight_recommendation', 'voltage', 'wattage', 'item_volume']
        
        entity_dropdown = ttk.Combobox(entity_frame, 
                                     textvariable=self.selected_entity,
                                     values=entities, 
                                     state='readonly',
                                     style='Custom.TCombobox')
        entity_dropdown.pack(expand=True)
        
        entity_dropdown.bind('<<ComboboxSelected>>', self.on_entity_select)
        
        return self.selected_entity

    def create_preview_and_output_section(self, parent):
        container = ttk.Frame(parent, style='Custom.TFrame')
        container.pack(fill='both', expand=True, padx=50, pady=(0, 20))
        
        preview_frame = ttk.LabelFrame(container, text=" Image Preview ", 
                                     padding="15", style='Custom.TLabelframe')
        preview_frame.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        self.preview_label = ttk.Label(preview_frame, style='Custom.TLabel')
        self.preview_label.pack(expand=True, padx=10, pady=10)
        self.set_default_preview()
        
        output_frame = ttk.LabelFrame(container, text=" Output ", 
                                    padding="15", style='Custom.TLabelframe')
        output_frame.pack(side='right', fill='both', expand=True, padx=(10, 0))
        
        self.output_text = scrolledtext.ScrolledText(
            output_frame, 
            width=40, 
            height=15,
            font=('Sora', 10),
            bg=CustomStyle.INPUT_BG,
            fg=CustomStyle.TEXT_COLOR,
            insertbackground=CustomStyle.TEXT_COLOR
        )
        self.output_text.pack(fill='both', expand=True, padx=10, pady=10)

    def create_process_button(self, parent):
        process_btn_frame = ttk.Frame(parent, style='Custom.TFrame')
        process_btn_frame.pack(fill='x', pady=10)
        
        process_btn = ttk.Button(process_btn_frame, text="Process Image", 
                               command=self.process_image, style='Custom.TButton')
        process_btn.pack(pady=10)

    def set_default_preview(self):
        self.preview_label.config(text="Image preview will appear here")

    def upload_image(self):
        try:
            file_types = [('Image files', '*.png *.jpg *.jpeg *.gif *.bmp')]
            filename = filedialog.askopenfilename(title="Select Image", filetypes=file_types)

            if filename:
                self.image_path = filename
                self.file_label.config(text=os.path.basename(filename))
                self.display_preview(filename)
                
                current_entity = self.selected_entity.get()
                if current_entity != "Select entity":
                    self.process_image_with_entity(filename, current_entity)
                    
                with open("uploaded_image_path.txt", "w") as file:
                    file.write(filename)
            return filename
        except Exception as e:
            self.output_text.delete(1.0, tk.END)
            self.output_text.insert(tk.END, f"Error uploading image: {str(e)}")

    def display_preview(self, image_path):
        try:
            image = Image.open(image_path)
            display_size = (300, 300)
            image.thumbnail(display_size, Image.LANCZOS)
            
            photo = ImageTk.PhotoImage(image)
            self.preview_label.config(image=photo)
            self.preview_label.image = photo
        except Exception as e:
            self.set_default_preview()
            self.output_text.delete(1.0, tk.END)
            self.output_text.insert(tk.END, f"Error displaying preview: {str(e)}")

    def process_image(self):
        if not self.image_path:
            self.output_text.delete(1.0, tk.END)
            self.output_text.insert(tk.END, "Please upload an image first!")
            return

        selected_entity = self.selected_entity.get()
        if selected_entity == "Select entity":
            self.output_text.delete(1.0, tk.END)
            self.output_text.insert(tk.END, "Please select an entity.")
            return

        self.process_image_with_entity(self.image_path, selected_entity)

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageTextExtractorGUI(root)
    root.mainloop()