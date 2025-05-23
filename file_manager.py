from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import os
import ctypes
import pathlib
import shutil
from datetime import datetime

ctypes.windll.shcore.SetProcessDpiAwareness(True)

# Глобальные переменные
root = Tk()
new_window = ''
new_file_name = StringVar(root, "Блокнот.txt", 'new_name')
current_path = StringVar(root, name='current_path', value=pathlib.Path.cwd())
search_query = StringVar(root)  # Для поисковой строки

# Настройка стилей
style = ttk.Style()
style.theme_use('default')

# Стиль для таблицы файлов
style.configure("Treeview",
               background="#333333",
               foreground="white",
               fieldbackground="#333333",
               borderwidth=0,
               font=('Segoe UI', 11),
               rowheight=28)
style.map('Treeview', background=[('selected', '#0078d7')])

# Стиль для заголовков таблицы файлов
style.configure("Treeview.Heading",
               background="#555555",
               foreground="white",
               relief="flat",
               font=('Segoe UI', 11, 'bold'))
style.map("Treeview.Heading",
         background=[('active', '#666666'), ('pressed', '#444444')])

# Стиль для ползунка
style.configure("Vertical.TScrollbar",
               background="#555555",
               troughcolor="#333333",
               bordercolor="#333333",
               arrowcolor="white",
               gripcount=0)

# Функция обновления списка файлов
def path_change(*event):
    for item in tree.get_children():
        tree.delete(item)
    
    directory = os.listdir(current_path.get())
    query = search_query.get().lower()
    
    for file in directory:
        if not query or query in file.lower():
            full_path = os.path.join(current_path.get(), file)
            try:
                stat = os.stat(full_path)
                size = stat.st_size
                modified = datetime.fromtimestamp(stat.st_mtime).strftime('%d.%m.%Y %H:%M')
                
                if os.path.isdir(full_path):
                    icon = "📁"
                    ext = "Папка"
                    size_text = ""
                else:
                    icon = "📄"
                    ext = os.path.splitext(file)[1][1:].upper() or "Файл"
                    size_text = f"{size:,} байт" if size < 1024 else f"{size/1024:,.1f} KB" if size < 1048576 else f"{size/1048576:,.1f} MB"
                
                tree.insert("", "end", values=(f"{icon} {file}", ext, modified, size_text), tags=('dir' if os.path.isdir(full_path) else 'file'))
            except Exception as e:
                print(f"Ошибка при обработке файла {file}: {e}")

# Открытие файла/папки
def change_path_by_click(event=None):
    selected = tree.focus()
    if selected:
        item = tree.item(selected)
        file = item['values'][0].split(" ", 1)[1]  # Удаляем иконку из имени
        path = os.path.join(current_path.get(), file)

        if os.path.isfile(path):
            os.startfile(path)
        else:
            current_path.set(path)

# переход назад
def go_back(event=None):
    new_path = pathlib.Path(current_path.get()).parent
    current_path.set(new_path)

# Создание нового файла/папки
def window_new_file_or_folder():
    global new_window
    new_window = Toplevel(root)
    new_window.geometry("300x150")
    new_window.resizable(0, 0)
    new_window.title("Новый файл/папка")
    
    frame = Frame(new_window, bg="#333333")
    frame.pack(pady=20, padx=20, fill=BOTH, expand=True)
    
    Label(frame, text='Введите название:', bg="#333333", fg="white").pack(anchor=W)
    Entry(frame, textvariable=new_file_name, bg="#555555", fg="white", insertbackground="white").pack(fill=X, pady=5)
    
    btn_frame = Frame(frame, bg="#333333")
    btn_frame.pack(fill=X, pady=10)
    
    Button(btn_frame, text="Создать", command=new_file_or_folder, bg="#555555", fg="white").pack(side=RIGHT, padx=5)
    Button(btn_frame, text="Отмена", command=new_window.destroy, bg="#555555", fg="white").pack(side=RIGHT)

def new_file_or_folder():
    if len(new_file_name.get().split('.')) != 1:
        open(os.path.join(current_path.get(), new_file_name.get()), 'w').close()
    else:
        os.mkdir(os.path.join(current_path.get(), new_file_name.get()))
    new_window.destroy()
    path_change()

# Удаление файла/папки
def delete_item():
    selected = tree.focus()
    if selected:
        item = tree.item(selected)
        file = item['values'][0].split(" ", 1)[1]
        path = os.path.join(current_path.get(), file)
        
        if not messagebox.askyesno(
            "Подтверждение удаления",
            f"Вы уверены, что хотите удалить {'папку' if os.path.isdir(path) else 'файл'}?\n{file}"
        ):
            return
            
        try:
            if os.path.isfile(path):
                os.remove(path)
            elif os.path.isdir(path):
                shutil.rmtree(path)
            path_change()
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось удалить:\n{str(e)}")

# Переименование файла/папки
def rename_item():
    selected = tree.focus()
    if selected:
        item = tree.item(selected)
        old_name = item['values'][0].split(" ", 1)[1]
        old_path = os.path.join(current_path.get(), old_name)
        
        rename_window = Toplevel(root)
        rename_window.title("Переименовать")
        rename_window.geometry("350x120")
        rename_window.resizable(0, 0)
        
        frame = Frame(rename_window, bg="#333333")
        frame.pack(pady=15, padx=20, fill=BOTH, expand=True)
        
        Label(frame, text="Введите новое имя:", bg="#333333", fg="white").pack(anchor=W)
        new_name_var = StringVar(value=old_name)
        entry = Entry(frame, textvariable=new_name_var, bg="#555555", fg="white", insertbackground="white")
        entry.pack(fill=X, pady=5)
        entry.focus_set()
        
        btn_frame = Frame(frame, bg="#333333")
        btn_frame.pack(fill=X, pady=5)
        
        def perform_rename():
            new_name = new_name_var.get()
            if new_name and new_name != old_name:
                new_path = os.path.join(current_path.get(), new_name)
                try:
                    os.rename(old_path, new_path)
                    rename_window.destroy()
                    path_change()
                except Exception as e:
                    messagebox.showerror("Ошибка", f"Не удалось переименовать:\n{str(e)}")
        
        Button(btn_frame, text="Переименовать", command=perform_rename, bg="#555555", fg="white").pack(side=RIGHT, padx=5)
        Button(btn_frame, text="Отмена", command=rename_window.destroy, bg="#555555", fg="white").pack(side=RIGHT)

# Настройка интерфейса
root.title("DocHawk Explorer")
root.geometry("900x600")
root.iconbitmap(r"C:\Users\dokto\Downloads\icon.ico")
root.configure(bg="#333333")
root.grid_rowconfigure(2, weight=1)
root.grid_columnconfigure(0, weight=1)

# Путь
path_frame = Frame(root, bg="#333333")
path_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(5, 0))
path_frame.grid_columnconfigure(1, weight=1)

Label(path_frame, text="💻 Путь:", font=('Segoe UI', 10, 'bold'), bg="#333333", fg="white").grid(row=0, column=0, padx=5, pady=5, sticky="w")
path_entry = Entry(path_frame, textvariable=current_path, font=('Segoe UI', 10),
                   bd=0, relief="flat", bg="#555555", fg="white", insertbackground="white")
path_entry.grid(row=0, column=1, sticky="ew", padx=(0, 5), pady=5)

# Панель инструментов и поиск 
action_frame = Frame(root, bg="#333333")
action_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=0)
action_frame.grid_columnconfigure(1, weight=1)

#кнопки
toolbar = Frame(action_frame, bg="#333333")
toolbar.grid(row=0, column=0, sticky="w", padx=0, pady=5)

Button(toolbar, text='←', command=go_back, font=('Arial', 12, 'bold'), 
       bg="#555555", fg="white", bd=0, padx=10, activebackground="#666666").pack(side=LEFT, padx=2)
Button(toolbar, text='📄', command=window_new_file_or_folder, font=('Arial', 12), 
       bg="#555555", fg="white", bd=0, padx=10, activebackground="#666666").pack(side=LEFT, padx=2)
Button(toolbar, text='✏️', command=rename_item, font=('Arial', 12), 
       bg="#555555", fg="white", bd=0, padx=10, activebackground="#666666").pack(side=LEFT, padx=2)
Button(toolbar, text='🗑️', command=delete_item, font=('Arial', 12), 
       bg="#555555", fg="white", bd=0, padx=10, activebackground="#666666").pack(side=LEFT, padx=2)

#  поиск
search_frame = Frame(action_frame, bg="#333333")
search_frame.grid(row=0, column=1, sticky="e", padx=0, pady=5)

search_entry = Entry(search_frame, textvariable=search_query, font=('Segoe UI', 10), 
                    bg="#555555", fg="white", insertbackground="white", bd=0)
search_entry.pack(side=LEFT, fill=X, expand=True, padx=(0, 5), pady=0, ipady=2)
Button(search_frame, text='🔍', command=path_change, font=('Arial', 12), 
      bg="#555555", fg="white", bd=0, activebackground="#666666").pack(side=LEFT)

# Таблица файлов
tree_frame = Frame(root, bg="#333333")
tree_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=(0, 10))

tree = ttk.Treeview(tree_frame, columns=("Name", "Type", "Modified", "Size"), 
                   show="headings", selectmode="browse")
tree.heading("Name", text="Имя", anchor=W)
tree.heading("Type", text="Тип", anchor=W)
tree.heading("Modified", text="Изменен", anchor=W)
tree.heading("Size", text="Размер", anchor=W)

tree.column("Name", width=350, anchor=W)
tree.column("Type", width=120, anchor=W)
tree.column("Modified", width=180, anchor=W)
tree.column("Size", width=120, anchor=W)

scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
tree.configure(yscrollcommand=scrollbar.set)

tree.pack(side=LEFT, fill=BOTH, expand=True)
scrollbar.pack(side=RIGHT, fill=Y)

# Настройка тегов для цветов строк
tree.tag_configure('dir', foreground='white')
tree.tag_configure('file', foreground='white')

# бинды
current_path.trace('w', path_change)
root.bind("<Alt-Left>", go_back)
root.bind("<Delete>", lambda e: delete_item())
tree.bind('<Double-1>', lambda e: change_path_by_click())
tree.bind('<Return>', lambda e: change_path_by_click())
search_entry.bind('<Return>', lambda e: path_change())

# Начальное отображение
path_change()
root.mainloop()