import customtkinter as ctk

app = ctk.CTk()
app.geometry("1920x1080")
app.title("Aplikacja do zarządzania budżetem domowym")


#tworzenie elementow
section_top = ctk.CTkFrame(app, width=1265, height=70)

section_left = ctk.CTkFrame(app, width=200, height=625)
desktop_btn = ctk.CTkButton(section_left, text="Pulpit", corner_radius=45, width=175, height=50)
transactions_btn = ctk.CTkButton(section_left, text="Transakcje", corner_radius=45, width=175, height=50)
categories_btn = ctk.CTkButton(section_left, text="Kategorie", corner_radius=45, width=175, height=50)
goals_btn = ctk.CTkButton(section_left, text="Cele", corner_radius=45, width=175, height=50)
raports_btn = ctk.CTkButton(section_left, text="Raporty", corner_radius=45, width=175, height=50)
settings_btn = ctk.CTkButton(section_left, text="Ustawienia", corner_radius=45, width=175, height=50)

section_right = ctk.CTkFrame(app, width=300, height=625)
text_right_placeholder = ctk.CTkLabel(section_right, text="Tu beda jakies tabelki lub wykresy")

section_bottom = ctk.CTkFrame(app, width=735, height=165)
text_bottom_placeholder = ctk.CTkLabel(section_bottom, text="Tu będzie wykres słupkowy wydatkow i budzetu na kazdy dzień")

section_left_top = ctk.CTkFrame(app, width=360, height=220)
text_left_top_placeholder = ctk.CTkLabel(section_left_top, text="Pozostały budżet na dzisiaj (?):")

section_right_top = ctk.CTkFrame(app, width=360, height=220)
text_right_top_placeholder = ctk.CTkLabel(section_right_top, text="Wydatki:")

section_left_bottom = ctk.CTkFrame(app, width=360, height=220)
text_left_bottom_placeholder = ctk.CTkLabel(section_left_bottom, text="Cel:")

section_right_bottom = ctk.CTkFrame(app, width=360, height=220)
text_right_bottom_placeholder = ctk.CTkLabel(section_right_bottom, text="Przychody:")

#dodawanie elementow do okna
section_top.place(x=10, y=10)

section_left.place(x=10, y=90)
desktop_btn.place(relx=0.5, y=50, anchor="center")
transactions_btn.place(relx=0.5, y=150, anchor="center")
categories_btn.place(relx=0.5, y=250, anchor="center")
goals_btn.place(relx=0.5, y=350, anchor="center")
raports_btn.place(relx=0.5, y=450, anchor="center")
settings_btn.place(relx=0.5, y=550, anchor="center")

section_right.place(x=975, y=90)
text_right_placeholder.place(relx=0, rely=0.5)

section_bottom.place(x=225, y=550)
text_bottom_placeholder.place(relx=0, rely=0.5)

section_left_top.place(x=225, y=90)
text_left_top_placeholder.place(relx=0, rely=0.5)

section_right_top.place(x=600, y=90)
text_right_top_placeholder.place(relx=0, rely=0.5)

section_left_bottom.place(x=225, y=320)
text_left_bottom_placeholder.place(relx=0, rely=0.5)

section_right_bottom.place(x=600, y=320)
text_right_bottom_placeholder.place(relx=0, rely=0.5)

#app.mainloop()