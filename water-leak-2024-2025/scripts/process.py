import os

for i in range(1, 13):
    day = f'0{i}' if i < 10 else str(i)
    os.system(f'python scripts/transform.py --rawdata /Users/gil-arnaudcoche/Documents/admin/rue-des-solitaires/water-leak-2024-2025/data/raw/2024{day}.txt --outdir /Users/gil-arnaudcoche/Documents/admin/rue-des-solitaires/water-leak-2024-2025/data/cleaned')


for i in range(1, 4):
    day = f'0{i}' if i < 10 else str(i)
    os.system(f'python scripts/transform.py --rawdata /Users/gil-arnaudcoche/Documents/admin/rue-des-solitaires/water-leak-2024-2025/data/raw/2025{day}.txt --outdir /Users/gil-arnaudcoche/Documents/admin/rue-des-solitaires/water-leak-2024-2025/data/cleaned')