import requests
import os

def clear_screen():
    """Clear the console screen."""
    os.system("cls" if os.name == "nt" else "clear")


def get_book_data(book_name, no_books):
    """Fetch book data from Google Books API."""
    try:
        url = f"https://www.googleapis.com/books/v1/volumes?q={book_name}&maxResults={no_books}"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"\n Network Error: {e}")
        return None


def display_book_details(data):
    """Display all book information sequentially."""
    print("\n📚 ====== Books ======\n")

    items = data.get("items", [])
    if not items:
        print("⚠️ No books found. Try another title.")
        return

    for index, item in enumerate(items, start=1):
        volume_info = item.get("volumeInfo", {})

        # ---- Book Information ----
        print(f"\n📘 Book {index}")
        print("=" * 60)
        book_title = volume_info.get("title", "N/A")
        authors = volume_info.get("authors", ["N/A"])
        publisher = volume_info.get("publisher", "N/A")
        published_date = volume_info.get("publishedDate", "N/A")
        description = volume_info.get("description", "No description available.")
        small_thumb = volume_info.get("imageLinks", {}).get("smallThumbnail", "No Image")
        thumb = volume_info.get("imageLinks", {}).get("thumbnail", "No Image")

        print(f"📖 Title: {book_title}")
        print(f"👨‍💻 Author(s): {', '.join(authors)}")
        print(f"🏢 Publisher: {publisher}")
        print(f"📅 Published Date: {published_date}")
        print(f"📝 Description: {description[:200]}...")
        print(f"🖼️ Small Thumbnail: {small_thumb}")
        print(f"📘 Thumbnail: {thumb}")

        # ---- Additional Information ----
        print("\n📂 Additional Information")
        print("-" * 60)
        book_kind = item.get("kind", "N/A")
        book_id = item.get("id", "N/A")
        book_etag = item.get("etag", "N/A")
        book_self_link = item.get("selfLink", "N/A")

        print(f"📚 Kind: {book_kind}")
        print(f"🆔 ID: {book_id}")
        print(f"🔖 ETag: {book_etag}")
        print(f"🔗 Self Link: {book_self_link}")
        print("=" * 60)

    print("\n✅ All book details displayed successfully!")


def main():
    clear_screen()
    print("=" * 60)
    print("📚 Welcome to Real-Time Book Finder 📚")
    print("=" * 60)

    book_name = input("\n🔎 Enter the book name to search: ").strip()
    if not book_name:
        print(" Book name cannot be empty!")
        return

    try:
        no_books = int(input("📘 Enter how many books you want to see: "))
        if no_books <= 0:
            print(" Please enter a positive number.")
            return
    except ValueError:
        print(" Invalid input! Please enter a number.")
        return

    print("\n⏳ Fetching book data... Please wait...\n")

    data = get_book_data(book_name, no_books)
    if not data:
        print("⚠️ No data received from the API.")
        return

    display_book_details(data)


if __name__ == "__main__":
    main()
