import tkinter as tk
from tkinter import messagebox
import requests
import threading

API_URL = "https://clinicaltables.nlm.nih.gov/api/icd10cm/v3/search"

class ICD10SearchApp:
    def __init__(self, root):
        self.root = root
        self.root.title("ICD-10 Live Search")
        self.root.geometry("600x400")
        self.root.configure(bg="#0f172a")

        # Search Entry
        self.entry = tk.Entry(root, font=("Arial", 14), bg="#1e293b", fg="white", insertbackground="white")
        self.entry.pack(fill="x", padx=10, pady=10)
        self.entry.bind("<KeyRelease>", self.on_key_release)

        # Results Listbox
        self.listbox = tk.Listbox(root, font=("Arial", 12), bg="#1e293b", fg="white", selectbackground="#3b82f6")
        self.listbox.pack(fill="both", expand=True, padx=10, pady=5)
        self.listbox.bind("<Double-Button-1>", self.copy_selected)

        # Status Label
        self.status = tk.Label(root, text="", fg="#94a3b8", bg="#0f172a", anchor="w")
        self.status.pack(fill="x", padx=10, pady=(0, 5))

        # Copy Button
        self.copy_btn = tk.Button(root, text="Copy Selected", command=self.copy_selected, bg="#3b82f6", fg="white")
        self.copy_btn.pack(pady=5)

        self.search_delay = None

    def on_key_release(self, event):
        """Debounce ke sath search trigger karega"""
        if self.search_delay:
            self.root.after_cancel(self.search_delay)
        query = self.entry.get().strip()
        if query:
            self.search_delay = self.root.after(300, lambda: self.search(query))
        else:
            self.listbox.delete(0, tk.END)
            self.status.config(text="")

    def search(self, query):
        """Thread me API call run karega taaki UI freeze na ho"""
        threading.Thread(target=self.fetch_results, args=(query,), daemon=True).start()

    def fetch_results(self, query):
        self.status.config(text="Searching...")
        self.listbox.delete(0, tk.END)
        try:
            params = {
                'sf': 'code,name',
                'terms': query,
                'maxList': 20
            }
            response = requests.get(API_URL, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()
            results = data[3]  # [[code, name], ...]

            if results:
                for code, name in results:
                    self.listbox.insert(tk.END, f"{code} - {name}")
                self.status.config(text=f"Found {len(results)} results for '{query}'")
            else:
                self.status.config(text="No results found.")
        except Exception as e:
            self.status.config(text="Error fetching data.")
            print("Error:", e)

    def copy_selected(self, event=None):
        """Selected result ko clipboard me copy karega"""
        selection = self.listbox.curselection()
        if selection:
            text = self.listbox.get(selection[0])
            self.root.clipboard_clear()
            self.root.clipboard_append(text)
            self.status.config(text=f"Copied: {text}")
        else:
            messagebox.showinfo("Copy", "Please select a result to copy.")

if __name__ == "__main__":
    root = tk.Tk()
    app = ICD10SearchApp(root)
    root.mainloop()
