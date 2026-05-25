import customtkinter as ctk

app = ctk.CTk()
app.geometry("1920x1080")
app.title("Aplikacja do zarządzania budżetem domowym")


#tworzenie elementow
section_left = ctk.CTkFrame(app, width=200, height=700)
add_income_btn = ctk.CTkButton(section_left, text="Dochody", corner_radius=45, width=175, height=35)
add_expense_btn = ctk.CTkButton(section_left, text="Wydatki", corner_radius=45, width=175, height=35)
add_goal_btn = ctk.CTkButton(section_left, text="Cele", corner_radius=45, width=175, height=35)

section_right = ctk.CTkFrame(app, width=300, height=700)
text_right_placeholder = ctk.CTkLabel(section_right, text="Tu beda jakies tabelki lub wykresy")

section_bottom = ctk.CTkFrame(app, width=735, height=210)
text_bottom_placeholder = ctk.CTkLabel(section_bottom, text="Tu będzie wykres słupkowy wydatkow i budzetu na kazdy dzień")

section_left_top = ctk.CTkFrame(app, width=360, height=210)
text_left_top_placeholder = ctk.CTkLabel(section_left_top, text="Pozostały budżet na dzisiaj (?):")

section_right_top = ctk.CTkFrame(app, width=360, height=210)
text_right_top_placeholder = ctk.CTkLabel(section_right_top, text="Wydatki:")

section_left_bottom = ctk.CTkFrame(app, width=360, height=210)
text_left_bottom_placeholder = ctk.CTkLabel(section_left_bottom, text="Cel:")

section_right_bottom = ctk.CTkFrame(app, width=360, height=210)
text_right_bottom_placeholder = ctk.CTkLabel(section_right_bottom, text="Przychody:")

#dodawanie elementow do okna
section_left.place(x=10, y=10)
add_income_btn.place(relx=0.5, y=100, anchor="center")
add_expense_btn.place(relx=0.5, y=150, anchor="center")
add_goal_btn.place(relx=0.5, y=200, anchor="center")

section_right.place(x=975, y=10)
text_right_placeholder.place(relx=0, rely=0.5)

section_bottom.place(x=225, y=500)
text_bottom_placeholder.place(relx=0, rely=0.5)

section_left_top.place(x=225, y=10)
text_left_top_placeholder.place(relx=0, rely=0.5)

section_right_top.place(x=600, y=10)
text_right_top_placeholder.place(relx=0, rely=0.5)

section_left_bottom.place(x=225, y=250)
text_left_bottom_placeholder.place(relx=0, rely=0.5)

section_right_bottom.place(x=600, y=250)
text_right_bottom_placeholder.place(relx=0, rely=0.5)

app.mainloop()