import os
import sys

import customtkinter as ctk

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BUILD_DIR = os.path.join(BASE_DIR, "build")
DATA_DIR = os.path.join(BASE_DIR, "data")

sys.path.insert(0, BUILD_DIR)

import bibliotheque_py


class LibraryApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Bibliothèque")
        self.geometry("1000x700")
        self.minsize(800, 560)

        self.library = bibliotheque_py.Library()
        self.file_manager = bibliotheque_py.FileManager(
            os.path.join(DATA_DIR, "books.txt"),
            os.path.join(DATA_DIR, "users.txt"),
        )

        self.title_var = ctk.StringVar()
        self.author_var = ctk.StringVar()
        self.isbn_var = ctk.StringVar()
        self.user_id_var = ctk.StringVar()
        self.status_var = ctk.StringVar(value="")

        self._build_ui()
        self._load_data()
        self.refresh_books()

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(4, weight=1)

        header = ctk.CTkLabel(
            self,
            text="Gestion de la bibliothèque",
            font=ctk.CTkFont(size=24, weight="bold"),
        )
        header.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")

        form = ctk.CTkFrame(self)
        form.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        form.grid_columnconfigure((1, 3), weight=1)

        self._add_field(form, "Titre", self.title_var, 0, 0)
        self._add_field(form, "Auteur", self.author_var, 0, 2)
        self._add_field(form, "ISBN", self.isbn_var, 1, 0)
        self._add_field(form, "ID utilisateur", self.user_id_var, 1, 2)

        actions = ctk.CTkFrame(self, fg_color="transparent")
        actions.grid(row=2, column=0, padx=20, pady=5, sticky="ew")

        ctk.CTkButton(actions, text="Ajouter un livre", command=self.add_book).pack(
            side="left", padx=(0, 10)
        )
        ctk.CTkButton(actions, text="Emprunter", command=self.borrow_book).pack(
            side="left", padx=10
        )
        ctk.CTkButton(actions, text="Retourner", command=self.return_book).pack(
            side="left", padx=10
        )
        ctk.CTkButton(actions, text="Sauvegarder", command=self.save_data).pack(
            side="left", padx=10
        )

        list_header = ctk.CTkFrame(self, fg_color="transparent")
        list_header.grid(row=3, column=0, padx=20, pady=(15, 0), sticky="ew")
        self._configure_book_columns(list_header)
        for index, text in enumerate(("Titre", "Auteur", "ISBN", "Statut")):
            ctk.CTkLabel(
                list_header, text=text, font=ctk.CTkFont(weight="bold"), anchor="w"
            ).grid(row=0, column=index, padx=8, sticky="ew")

        self.books_frame = ctk.CTkScrollableFrame(self, label_text="Livres")
        self.books_frame.grid(row=4, column=0, padx=20, pady=(5, 10), sticky="nsew")
        self._configure_book_columns(self.books_frame)

        self.status_label = ctk.CTkLabel(self, textvariable=self.status_var, anchor="w")
        self.status_label.grid(row=5, column=0, padx=20, pady=(0, 15), sticky="ew")

    def _add_field(self, parent, label, variable, row, column):
        ctk.CTkLabel(parent, text=label).grid(
            row=row, column=column, padx=(10, 5), pady=8, sticky="e"
        )
        ctk.CTkEntry(parent, textvariable=variable).grid(
            row=row, column=column + 1, padx=(5, 10), pady=8, sticky="ew"
        )

    def _configure_book_columns(self, container):
        container.grid_columnconfigure(0, weight=3)
        container.grid_columnconfigure(1, weight=2)
        container.grid_columnconfigure(2, weight=2)
        container.grid_columnconfigure(3, weight=1)

    def _load_data(self):
        try:
            self.file_manager.loadLibraryData(self.library)
            self._set_status("Données chargées.", success=True)
        except Exception as error:
            self._set_status(f"Erreur de chargement : {error}", success=False)

    def refresh_books(self):
        for widget in self.books_frame.winfo_children():
            widget.destroy()

        books = self.library.getAllBooks()
        if not books:
            ctk.CTkLabel(self.books_frame, text="Aucun livre.").grid(
                row=0, column=0, columnspan=4, pady=10
            )
            return

        for row, book in enumerate(books):
            available = book.getAvailability()
            status = "Disponible" if available else f"Emprunté ({book.getBorrowerId()})"
            values = (book.getTitle(), book.getAuthor(), book.getISBN(), status)

            item = ctk.CTkFrame(
                self.books_frame,
                fg_color=("gray90", "gray20") if row % 2 == 0 else "transparent",
            )
            item.grid(row=row, column=0, columnspan=4, sticky="ew", pady=1)
            self._configure_book_columns(item)

            for column, value in enumerate(values):
                label = ctk.CTkLabel(
                    item,
                    text=value,
                    anchor="w",
                    text_color="#2fa572" if column == 3 and available else
                    ("#d9534f" if column == 3 else None),
                )
                label.grid(row=0, column=column, padx=8, pady=6, sticky="ew")
                label.bind(
                    "<Button-1>",
                    lambda _event, isbn=book.getISBN(): self.isbn_var.set(isbn),
                )
            item.bind(
                "<Button-1>",
                lambda _event, isbn=book.getISBN(): self.isbn_var.set(isbn),
            )

    def add_book(self):
        title = self.title_var.get().strip()
        author = self.author_var.get().strip()
        isbn = self.isbn_var.get().strip()

        if not title or not author or not isbn:
            self._set_status("Titre, auteur et ISBN sont obligatoires.", success=False)
            return

        if self.library.findBookByISBN(isbn) is not None:
            self._set_status("Un livre avec cet ISBN existe déjà.", success=False)
            return

        try:
            book = bibliotheque_py.Book(title, author, isbn)
            self.library.addBook(book)
            self.refresh_books()
            self._set_status(f"Livre « {title} » ajouté.", success=True)
        except Exception as error:
            self._set_status(f"Erreur : {error}", success=False)

    def borrow_book(self):
        isbn = self.isbn_var.get().strip()
        user_id = self.user_id_var.get().strip()

        if not isbn or not user_id:
            self._set_status("ISBN et ID utilisateur sont obligatoires.", success=False)
            return

        try:
            if self.library.checkOutBook(isbn, user_id):
                self.refresh_books()
                self._set_status(f"Livre {isbn} emprunté par {user_id}.", success=True)
            else:
                self._set_status(
                    "Emprunt impossible : livre indisponible, ISBN ou utilisateur inconnu.",
                    success=False,
                )
        except Exception as error:
            self._set_status(f"Erreur : {error}", success=False)

    def return_book(self):
        isbn = self.isbn_var.get().strip()

        if not isbn:
            self._set_status("L'ISBN est obligatoire.", success=False)
            return

        try:
            if self.library.returnBook(isbn):
                self.refresh_books()
                self._set_status(f"Livre {isbn} retourné.", success=True)
            else:
                self._set_status("Retour impossible : livre inconnu ou déjà disponible.", success=False)
        except Exception as error:
            self._set_status(f"Erreur : {error}", success=False)

    def save_data(self):
        try:
            os.makedirs(DATA_DIR, exist_ok=True)
            if self.file_manager.saveLibraryData(self.library):
                self._set_status("Données sauvegardées.", success=True)
            else:
                self._set_status("La sauvegarde a échoué.", success=False)
        except Exception as error:
            self._set_status(f"Erreur : {error}", success=False)

    def _set_status(self, message, success):
        self.status_var.set(message)
        self.status_label.configure(text_color="#2fa572" if success else "#d9534f")


if __name__ == "__main__":
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    app = LibraryApp()
    app.mainloop()
