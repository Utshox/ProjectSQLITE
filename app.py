# Import necessary modules from Flask and Flask-SQLAlchemy
from flask import Flask, render_template, request, redirect, url_for # request, redirect, url_for are needed for CUD operations
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import Integer, String, Float

# Create the Flask application instance
app = Flask(__name__) # Use 'app' here

# --- Database Configuration ---
class Base(DeclarativeBase):
    pass
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///books.db"
db = SQLAlchemy(model_class=Base)
db.init_app(app)
# --- End Database Configuration ---


# --- Database Model Definition ---
class Book(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(250), unique=True, nullable=False)
    author: Mapped[str] = mapped_column(String(250), nullable=False)
    rating: Mapped[float] = mapped_column(Float, nullable=False)
# --- End Database Model Definition ---


# --- Create Database Table ---
with app.app_context():
    db.create_all()
# --- End Create Database Table ---


# --- Routes ---
@app.route('/')
def home():
    # === Read all records from the database ===
    select_query = db.select(Book).order_by(Book.title)
    result = db.session.execute(select_query)
    all_books = result.scalars().all()
    # =========================================
    # === Render the HTML template ===
    return render_template("index.html", books=all_books)
    # ==============================

# === Create Route ===
@app.route("/add", methods=["GET", "POST"]) # Allow both GET and POST requests
def add():
    if request.method == "POST":
        # --- Handle POST Request (Form Submission) ---
        # Create a new Book object using data from the submitted form
        # request.form is a dictionary-like object containing form data
        new_book = Book(
            title=request.form["title"],
            author=request.form["author"],
            rating=request.form["rating"]
        )
        # Add the new book object to the database session
        db.session.add(new_book)
        # Commit the changes to save them permanently in the database
        db.session.commit()

        # Redirect the user back to the home page after adding the book
        return redirect(url_for('home'))
        # --- End POST Request Handling ---

    # --- Handle GET Request (Displaying the Form) ---
    # If the request method is GET, just display the add.html form
    return render_template("add.html")
    # --- End GET Request Handling ---
# ====================

# === Update Route ===
@app.route("/edit", methods=["GET", "POST"]) # Allow both GET and POST
def edit():
    if request.method == "POST":
        # --- Handle POST Request (Update Submission) ---
        # Get the book ID from the hidden input field in the form
        book_id = request.form["id"]
        # Fetch the specific book from the database using its ID
        # db.get_or_404() is convenient: gets the book or returns a 404 Not Found error
        book_to_update = db.get_or_404(Book, book_id)
        # Update the rating of the fetched book object
        book_to_update.rating = request.form["rating"]
        # Commit the changes to the database
        db.session.commit()
        # Redirect back to the home page to see the updated list
        return redirect(url_for('home'))
        # --- End POST Request Handling ---

    # --- Handle GET Request (Displaying Edit Form) ---
    # Get the book ID from the URL query parameter (e.g., /edit?id=1)
    # request.args is used for parameters in the URL
    book_id = request.args.get('id')
    # Fetch the specific book to edit
    book_selected = db.get_or_404(Book, book_id)
    # Render the edit_rating.html template, passing the selected book's data
    return render_template("edit_rating.html", book=book_selected)
    # --- End GET Request Handling ---
# ====================

# === Delete Route ===
@app.route("/delete")
def delete():
    # Get the book ID from the URL query parameter (e.g., /delete?id=1)
    book_id = request.args.get('id')
    # Fetch the book to delete, or return 404 if not found
    book_to_delete = db.get_or_404(Book, book_id)
    # Remove the book from the database session
    db.session.delete(book_to_delete)
    # Commit the deletion to the database
    db.session.commit()
    # Redirect back to the home page
    return redirect(url_for('home'))
# ====================

# --- End Routes ---


# --- Run the Application ---
if __name__ == "__main__":
    app.run(debug=True)
# --- End Run the Application ---
