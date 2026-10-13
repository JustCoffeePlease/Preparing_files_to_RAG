import os
import re
from bs4 import BeautifulSoup

def convert_html_table_to_md(match):
    """Функция преобразования одной HTML-таблицы в Markdown"""
    html_str = match.group(0)
    soup = BeautifulSoup(html_str, 'html.parser')
    table = soup.find('table')
    if not table:
        return html_str
    
    md_lines = []
    rows = table.find_all('tr')
    
    for i, row in enumerate(rows):
        cells = row.find_all(['th', 'td'])
        # Очищаем текст, убираем переносы строк внутри ячеек и экранируем символы '|'
        cell_texts = [
            cell.get_text(strip=True).replace('\n', ' ').replace('|', '\\|') 
            for cell in cells
        ]
        
        if not cell_texts:
            continue
            
        # Формируем строку Markdown-таблицы
        md_lines.append("| " + " | ".join(cell_texts) + " |")
        
        # После первой строки добавляем разделитель (шапку)
        if i == 0:
            md_lines.append("| " + " | ".join(["---"] * len(cell_texts)) + " |")
            
    return "\n".join(md_lines)

def process_markdown_files(directory_path):
    """Проход по всем MD файлам в папке и ее подпапках"""
    # Регулярное выражение для поиска блоков <table>...</table>
    table_pattern = re.compile(r'<table.*?>.*?</table>', re.IGNORECASE | re.DOTALL)
    
    print(f"🔍 Начинаю сканирование папки: {directory_path}\n")
    
    # Собираем все MD файлы
    md_files = []
    for root, _, files in os.walk(directory_path):
        for filename in files:
            if filename.lower().endswith('.md'):
                md_files.append(os.path.join(root, filename))
    
    total_files = len(md_files)
    print(f"📁 Найдено {total_files} файлов\n")
    
    if total_files == 0:
        print("❌ MD файлы не найдены в указанной папке!")
        return
    
    files_with_tables = 0
    total_tables_converted = 0
    
    for filepath in md_files:
        filename = os.path.basename(filepath)
        print(f"🔎 Начинаю анализ: {filename}")
        
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Подсчитываем количество таблиц
        tables_found = table_pattern.findall(content)
        table_count = len(tables_found)
        
        if table_count > 0:
            print(f"   📊 Найдено {table_count} таблиц")
            
            # Заменяем таблицы
            new_content = table_pattern.sub(convert_html_table_to_md, content)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print(f"   ✅ Все таблицы заменены на формат markdown")
            files_with_tables += 1
            total_tables_converted += table_count
        else:
            print(f"   ⏭️ Таблиц не найдено")
        
        print()  # Пустая строка для читаемости
    
    print("=" * 60)
    print(f"🎉 Готово!")
    print(f"📈 Обработано файлов с таблицами: {files_with_tables} из {total_files}")
    print(f"🔄 Всего конвертировано таблиц: {total_tables_converted}")
    print("=" * 60)

if __name__ == "__main__":
    # Получаем путь к папке, где находится сам скрипт
    script_dir = os.path.dirname(os.path.abspath(__file__))
    process_markdown_files(script_dir)