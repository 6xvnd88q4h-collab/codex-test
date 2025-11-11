from datetime import date

name = "DEIN NAME"
heute = date.today().strftime("%d.%m.%Y")
print(f"Hallo, {name} – {heute}")

