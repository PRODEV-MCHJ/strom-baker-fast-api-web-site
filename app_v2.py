import os

# Papka nomi
folder_path = "Storm-Breaker"

# Fayl yo'llarini saqlash uchun ro'yxat
local_file_paths = []

# PHP fayllar uchun natijaviy fayl
output_file = "response_html.txt"

# Barcha fayl yo'llarini olish
for root, dirs, files in os.walk(folder_path):
    for file in files:
        file_path = os.path.join(root, file)
        local_file_paths.append(file_path)

# PHP fayllarni ajratib, natijani yozish
with open(output_file, "w", encoding="utf-8") as output:
    for file_path in local_file_paths:
        if file_path.endswith(".php"):
            with open(file_path, "r", encoding="utf-8") as php_file:
                output.write(f"File: {os.path.basename(file_path)}\n")
                output.write(php_file.read())
                output.write("\n\n")  # Kodlar orasiga bo'sh qatordan qo'shish

print(f"Barcha  fayllar qayta ishlanib, {output_file} fayliga yozildi.")
