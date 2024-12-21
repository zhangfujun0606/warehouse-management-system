import tkinter as tk
from tkinter import ttk, messagebox

logged_in_user = None

def login(window, load_data, setup_main_window):
    login_window = tk.Toplevel(window)
    login_window.title("登入")

    username_label = ttk.Label(login_window, text="帳號:")
    username_label.grid(row=0, column=0, padx=5, pady=5)
    username_entry = ttk.Entry(login_window)
    username_entry.grid(row=0, column=1, padx=5, pady=5)

    password_label = ttk.Label(login_window, text="密碼 (4位數字):")
    password_label.grid(row=1, column=0, padx=5, pady=5)
    password_entry = ttk.Entry(login_window, show="*")
    password_entry.grid(row=1, column=1, padx=5, pady=5)

    def check_login():
        username = username_entry.get()
        password = password_entry.get()
        if username == "0510" and password == "0000":
            login_window.destroy()
            global logged_in_user
            logged_in_user = "0510"
            load_data()
            setup_main_window(logged_in_user)  # 傳遞 logged_in_user
        else:
            messagebox.showerror("登入失敗", "帳號或密碼錯誤，請重新輸入")

    login_button = ttk.Button(login_window, text="登入", command=check_login)
    login_button.grid(row=2, column=0, columnspan=2, padx=10, pady=10)

    login_window.wait_window()

    return logged_in_user # 返回 logged_in_user