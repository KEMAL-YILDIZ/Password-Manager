from tkinter import *
from tkinter import messagebox
import pyperclip
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import random
import string

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///data.db"

db = SQLAlchemy(app)


class Data(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    website = db.Column(db.String(250), nullable=False, unique=True)
    email = db.Column(db.String(250), nullable=False)
    password = db.Column(db.String(250), nullable=False)


# with app.app_context():
#     db.create_all()


# ------------------------------- ENCRYPTION ------------------------------- #

chars = string.punctuation + string.digits + string.ascii_letters
chars = list(chars)
encrypted_list = ['L', '2', '>', '\\', 'j', 'E', '/', ')', '~', 'D', '#', 'x', "'", 'M', 'N', '"', 'P', 'o', '_', 'z',
                  'n', 'q', '{', 'm', '=', 'A', '&', 'K', 'G', 'd', 'u', '|', 'V', '8', 'g', '}', 's', '9', ']', '<',
                  'T', 'X', 'y', 'W', '3', 'w', 'Q', '(', 'Z', '4', '-', '@', 'I', 'c', 'S', '[', '*', '.', 'v', ':',
                  '!', '6', 'B', 'H', 'r', '?', ';', 'Y', 'a', 'k', 'U', 'f', '5', '^', '+', '%', 'i', ',', '`', 'e',
                  'O', 'F', 'p', 'h', '1', 'b', 't', '7', '0', 'R', 'l', 'C', 'J', '$']


def encrypt(message: str):
    """This is a function that will encrypt text according to the index of each letter of the text inside the chars
     list and produce it as the letter in it's index inside the encrypted_list."""
    cipher_text: str = ""
    for letter in message:
        index = chars.index(letter)
        cipher_text += encrypted_list[index]
    return cipher_text


def decrypt(cipher_text: str):
    """This is a funcation that will decrypt codings according to the index of each letter of the coding inside the
     encrypted_list list and produce it as the letter in it's index inside the chars list."""
    message: str = ""
    for letter in cipher_text:
        index = encrypted_list.index(letter)
        message += chars[index]
    return message


# ---------------------------- PASSWORD GENERATOR ------------------------------- #
def generate_password():
    """This fucntion will generate a random password and insert it in the password field, additionally it
     will copy the password into the clipboard."""
    letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q',
               'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H',
               'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z']
    numbers = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    symbols = ['!', '#', '$', '%', '&', '(', ')', '*', '+']

    nr_letters = random.randint(8, 10)
    nr_symbols = random.randint(2, 4)
    nr_numbers = random.randint(2, 4)

    letters_password = [random.choice(letters) for _ in range(nr_letters)]
    symbol_password = [random.choice(symbols) for _ in range(nr_symbols)]
    number_password = [random.choice(numbers) for _ in range(nr_numbers)]

    password_list = letters_password + symbol_password + number_password

    random.shuffle(password_list)
    password = "".join(password_list)

    pyperclip.copy(password)
    password_entry.insert(0, password)
    messagebox.showinfo(title="Clipboard", message="Password copied!")


# ---------------------------- DELETE PASSWORD ---------------------------- #

def delete():
    """This function will delete a account according to the Website a user has typed inside the website entry,
     the website account's credentials will be deleted if it's found."""
    website = website_entry.get()
    if len(website) == 0:
        messagebox.showerror(title="Search", message="The Website Field is Required")
    else:
        with app.app_context():
            try:
                result = db.session.execute(db.Select(Data).where(Data.website == website)).scalar()
                email = result.email
                password = decrypt(cipher_text=result.password)
            except:
                messagebox.showerror(title="Error", message=f"Sorry, we couldn't find an account on {website}")
            else:
                if messagebox.askokcancel(title="Delete an Account",
                                          message="Are you sure you want to delete an account with these credentials\n"
                                                  f"Website: {website}\nEmail: {email}\n"
                                                  f"Password: {password}"):
                    db.session.delete(result)
                    db.session.commit()
                    messagebox.showinfo(title="Success", message="Account deleted successfully")
                    website_entry.delete(0, END)
                    email_entry.delete(0, END)
                    password_entry.delete(0, END)


# ---------------------------- EDIT ACCOUNT DETAILS ------------------------------- #

def edit():
    """This function will allow the user to edit a website credentials on another window that shows
    the old credentails and the new credentials entries.. if the user doesn't want to edit anything he
     can leave the entries blank and press submit."""
    website = website_entry.get()
    if len(website) == 0:
        messagebox.showerror(title="Search", message="The Website Field is Required")
    else:
        try:
            with app.app_context():
                result = db.session.execute(db.Select(Data).where(Data.website == website)).scalar()
                email = result.email
                password = decrypt(cipher_text=result.password)
        except:
            messagebox.showerror(title="Error", message=f"Sorry, we couldn't find an account on {website}")
        else:
            def submit_clicked():
                with app.app_context():
                    data_result = db.session.execute(db.Select(Data).where(Data.website == website)).scalar()
                    are_blank: bool = False
                    new_email = new_email_entry.get().strip()
                    new_password = new_password_entry.get().strip()
                    if len(new_password) == 0 and len(new_email) == 0:
                        are_blank = True
                    if len(new_email) == 0:
                        new_email = data_result.email
                    if len(new_password) == 0:
                        new_password = decrypt(cipher_text=data_result.password)
                    data_result.email = new_email
                    data_result.password = encrypt(message=new_password)
                    db.session.commit()

                    if are_blank:
                        messagebox.showinfo(title="Success", message="Account Credentails Saved Successfully!\n"
                                                                     "No Changes Made.")
                    else:
                        messagebox.showinfo(title="Success", message="Account Credentails Edited Successfully!")
                    new_email_entry.delete(0, END)
                    new_password_entry.delete(0, END)
                    edit_window.destroy()
                    website_entry.delete(0, END)
                    email_entry.delete(0, END)
                    password_entry.delete(0, END)

            edit_window = Toplevel()
            edit_window.title("Account Editor")
            edit_window.config(padx=5, pady=5, bg="#cccccc")

            note_label = Label(edit_window, text="NOTE: leave a field blank, if you don't want to edit it",
                               font=("Arial", 8, "bold"), bg="#cccccc")
            note_label.grid(row=0, column=0, columnspan=4, sticky=NW)
            old_label = Label(edit_window, text="Old Credentials", bg="#cccccc", font=("Arial", 10, "bold"))
            new_label = Label(edit_window, text="New Credentials", bg="#cccccc", font=("Arial", 10, "bold"))
            old_label.grid(row=2, column=1)
            new_label.grid(row=2, column=3)
            filler_element = Label(edit_window, text="", bg="#cccccc", fg="#cccccc")
            filler_element.grid(row=1, column=1)
            website_label_edit = Label(edit_window, text=f"Website: {website}", padx=10, pady=5,
                                       font=("Arial", 14, "bold"), bg="#cccccc")
            website_label_edit.grid(row=3, column=1, sticky=W)
            email_label_edit = Label(edit_window, text=f"Email: {email}", padx=10, pady=5,
                                     font=("Arial", 14, "bold"), bg="#cccccc")
            email_label_edit.grid(row=4, column=1, sticky=W)
            password_label_edit = Label(edit_window, text=f"Password: {password}", padx=10, pady=5,
                                        font=("Arial", 14, "bold"), bg="#cccccc")
            password_label_edit.grid(row=5, column=1, sticky=W)

            submit_button = Button(edit_window, text="Submit", bg="green", command=submit_clicked)
            submit_button.grid(row=6, column=2)

            new_website_entry = Entry(edit_window, width=35, state="disabled", bg="#cccccc", fg="#cccccc")
            new_website_entry.grid(row=3, column=3, padx=10, pady=5)
            new_email_entry = Entry(edit_window, width=35)
            new_email_entry.grid(row=4, column=3, padx=10, pady=5)
            new_password_entry = Entry(edit_window, width=35)
            new_password_entry.grid(row=5, column=3, padx=10, pady=5)


# ---------------------------- SAVE PASSWORD ------------------------------- #


def save():
    """This function will save a account credentails a user has entered."""
    website = website_entry.get().strip()
    email = email_entry.get().strip()
    password = password_entry.get().strip()

    if len(website) == 0 or len(password) == 0 or len(email) == 0:
        messagebox.showerror(title="Error", message="Please don't leave any fields empty!")

    else:
        with app.app_context():
            try:
                password = encrypt(message=password)
                new_data = Data(website=website, email=email, password=password)
                db.session.add(new_data)
            except:
                messagebox.showerror(title="Error", message=f"You already have an account on {website}")
            else:

                db.session.commit()
                messagebox.showinfo(title="Success", message="Account added successfully")
            finally:
                website_entry.delete(0, END)
                email_entry.delete(0, END)
                password_entry.delete(0, END)


# ---------------------------- Search Password ---------------------------- #

def find_password():
    """This function will search for a website credentails a user has entered."""
    website = website_entry.get()
    if len(website) == 0:
        messagebox.showerror(title="Search", message="The Website Field is Required")
    else:
        try:
            with app.app_context():
                result = db.session.execute(db.Select(Data).where(Data.website == website)).scalar()
                email = result.email
                password = decrypt(cipher_text=result.password)
        except:
            messagebox.showerror(title="Error", message=f"Sorry, we couldn't find an account on {website}")
        else:
            messagebox.showinfo(title="Account details",
                                message=f"Website: {website}\nEmail: {email}\nPassword: {password}")
            website_entry.delete(0, END)
            email_entry.delete(0, END)
            password_entry.delete(0, END)


# ---------------------------- UI SETUP ------------------------------- #


window = Tk()
window.title("Password Manager")
window.config(padx=50, pady=50)

canvas = Canvas(height=200, width=200)
logo_img = PhotoImage(file="logo.png")
canvas.create_image(100, 100, image=logo_img)
canvas.grid(row=0, column=1)

# Labels
website_label = Label(text="Website:", width=12, anchor="w")
website_label.grid(row=1, column=0, sticky=W)
email_label = Label(text="Email/Username:", width=12, anchor="w")
email_label.grid(row=2, column=0, sticky=W)
password_label = Label(text="Password:", width=12, anchor="w")
password_label.grid(row=3, column=0, sticky=W)

# Entries
website_entry = Entry(width=35)
website_entry.grid(row=1, column=1, columnspan=2, sticky=W)
website_entry.focus()
email_entry = Entry(width=35)
email_entry.grid(row=2, column=1, columnspan=2, sticky=W)
password_entry = Entry(width=35)
password_entry.grid(row=3, column=1, sticky=W)

# Buttons
generate_password_button = Button(text="Generate Password", command=generate_password, width=16, bg="#a4a7ab")
generate_password_button.grid(row=3, column=2, sticky=W)

edit_button = Button(text="Edit", width=16, command=edit, bg="#cccccc")
edit_button.grid(row=2, column=2, sticky=W)

add_button = Button(text="Add", width=29, command=save, bg="#a4a7ab")
add_button.grid(row=4, column=1, columnspan=2, sticky=W)

search_button = Button(text="Search", width=16, command=find_password, bg="#a4a7ab")
search_button.grid(row=1, column=2, sticky=W)

delete_button = Button(text="Delete", width=16, command=delete, bg="#cccccc")
delete_button.grid(row=4, column=2)

window.mainloop()
