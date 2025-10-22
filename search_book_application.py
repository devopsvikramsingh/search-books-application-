import tkinter as tk
from tkinter import ttk, messagebox
import threading
import requests
from PIL import Image, ImageTk
from io import BytesIO


# -------------------- API FUNCTION --------------------
def get_book_data(book_name, no_books):
    """Fetch book data from Google Books API."""
    try:
        url = f"https://www.googleapis.com/books/v1/volumes?q={book_name}&maxResults={no_books}"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Network Error", f"Failed to fetch data: {e}")
        return None


# -------------------- CREATE BOOK CARD --------------------
def create_book_card(parent, book_data):
    """Create and display a single book card."""
    frame = tk.Frame(parent, bg="#F7F9FC", bd=2, relief="groove", padx=10, pady=10)
    frame.pack(fill="x", pady=8)

    volume_info = book_data.get("volumeInfo", {})
    title = volume_info.get("title", "N/A")
    authors = ", ".join(volume_info.get("authors", ["Unknown Author"]))
    publisher = volume_info.get("publisher", "N/A")
    published_date = volume_info.get("publishedDate", "N/A")
    description = volume_info.get("description", "No description available.")[:200]
    thumbnail_url = volume_info.get("imageLinks", {}).get("thumbnail")

    # ---- Book Thumbnail ----
    if thumbnail_url:
        try:
            img_data = requests.get(thumbnail_url).content
            img = Image.open(BytesIO(img_data)).resize((80, 120))
            photo = ImageTk.PhotoImage(img)
            img_label = tk.Label(frame, image=photo, bg="#F7F9FC")
            img_label.image = photo
            img_label.grid(row=0, column=0, rowspan=4, padx=10)
        except Exception as e:
            print("Image Load Error:", e)

    # ---- Book Info ----
    tk.Label(frame, text=f"📖 {title}", font=("Segoe UI", 12, "bold"), bg="#F7F9FC", anchor="w", justify="left").grid(row=0, column=1, sticky="w")
    tk.Label(frame, text=f"👨‍💻 Author(s): {authors}", bg="#F7F9FC", anchor="w").grid(row=1, column=1, sticky="w")
    tk.Label(frame, text=f"🏢 Publisher: {publisher}", bg="#F7F9FC", anchor="w").grid(row=2, column=1, sticky="w")
    tk.Label(frame, text=f"📅 Published: {published_date}", bg="#F7F9FC", anchor="w").grid(row=3, column=1, sticky="w")

    tk.Label(frame, text=f"📝 {description}...", wraplength=600, justify="left", bg="#F7F9FC").grid(row=4, column=0, columnspan=2, sticky="w", pady=(10, 0))


# -------------------- MAIN APP CLASS --------------------
class BookFinderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("📚 Real-Time Book Finder")
        self.root.geometry("900x650")
        self.root.config(bg="#EAF0F6")

        title_label = tk.Label(root, text="📚 Real-Time Book Finder", font=("Segoe UI", 18, "bold"), bg="#EAF0F6")
        title_label.pack(pady=15)

        # --- Input Frame ---
        input_frame = tk.Frame(root, bg="#EAF0F6")
        input_frame.pack(pady=10)

        tk.Label(input_frame, text="🔎 Enter Book Name:", bg="#EAF0F6").grid(row=0, column=0, padx=5, pady=5)
        self.book_entry = tk.Entry(input_frame, width=40, font=("Segoe UI", 11))
        self.book_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(input_frame, text="📘 No. of Books:", bg="#EAF0F6").grid(row=0, column=2, padx=5, pady=5)
        self.limit_entry = tk.Entry(input_frame, width=10, font=("Segoe UI", 11))
        self.limit_entry.grid(row=0, column=3, padx=5, pady=5)

        search_btn = tk.Button(input_frame, text="Search", bg="#4A90E2", fg="white", font=("Segoe UI", 10, "bold"), command=self.start_search_thread)
        search_btn.grid(row=0, column=4, padx=10)

        clear_btn = tk.Button(input_frame, text="Clear", bg="#FF6B6B", fg="white", font=("Segoe UI", 10, "bold"), command=self.clear_results)
        clear_btn.grid(row=0, column=5, padx=5)

        # --- Status Label ---
        self.status_label = tk.Label(root, text="", font=("Segoe UI", 10, "italic"), bg="#EAF0F6", fg="#333")
        self.status_label.pack()

        # --- Scrollable Frame for Results ---
        result_frame = tk.Frame(root)
        result_frame.pack(fill="both", expand=True, pady=10)

        canvas = tk.Canvas(result_frame, bg="#EAF0F6", highlightthickness=0)
        scrollbar = ttk.Scrollbar(result_frame, orient="vertical", command=canvas.yview)
        self.scrollable_frame = tk.Frame(canvas, bg="#EAF0F6")

        self.scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    # -------------------- CLEAR RESULTS --------------------
    def clear_results(self):
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.book_entry.delete(0, tk.END)
        self.limit_entry.delete(0, tk.END)
        self.status_label.config(text="")

    # -------------------- START SEARCH THREAD --------------------
    def start_search_thread(self):
        thread = threading.Thread(target=self.search_books)
        thread.start()

    # -------------------- SEARCH FUNCTION --------------------
    def search_books(self):
        book_name = self.book_entry.get().strip()
        limit = self.limit_entry.get().strip()

        if not book_name:
            self.status_label.config(text="⚠️ Please enter a book name.")
            return

        try:
            limit = int(limit)
            if limit <= 0:
                self.status_label.config(text="⚠️ Enter a positive number for book limit.")
                return
        except ValueError:
            self.status_label.config(text="⚠️ Enter a valid number for book limit.")
            return

        self.status_label.config(text="⏳ Fetching books... please wait.")
        self.clear_results()

        data = get_book_data(book_name, limit)
        if not data or "items" not in data:
            self.status_label.config(text="⚠️ No books found. Try another search.")
            return

        for book in data["items"]:
            create_book_card(self.scrollable_frame, book)

        self.status_label.config(text=f"✅ Found {len(data['items'])} books for '{book_name}'.")


# -------------------- RUN APP --------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = BookFinderApp(root)
    root.mainloop()
