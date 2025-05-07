from tkinter import *
from tkinter import messagebox
import os
import ctypes
import pathlib
import shutil

ctypes.windll.shcore.SetProcessDpiAwareness(True)

 #ивент
def path_change(*event):
    directory = os.listdir(current_path.get())
    list.delete(0, END)

    for file in directory:
        list.insert(0,file)

#открытие файла
def change_path_by_click(event=None):
    picked = list.get(list.curselection()[0])
    path = os.path.join(current_path.get(),picked)

    if os.path.isfile(path):
        os.startfile(path)
    else:
        current_path.set(path)

def go_back(event=None):
    new_path = pathlib.Path(current_path.get()).parent
    current_path.set(new_path)

#дочернее окно
def window_new_file_or_folder():
    global new_window
    new_window = Toplevel(root)
    new_window.geometry("250x150")
    new_window.resizable(0, 0)
    new_window.title("новый файл/папка")
    new_window.columnconfigure(0, weight=1)
    Label(new_window, text='Введите название нового файла/паки').grid()
    Entry(new_window, textvariable=new_file_name).grid(column=0, pady = 18, sticky=NSEW)
    Button(new_window, command=new_file_or_folder).grid(pady=10,sticky=NSEW)

def new_file_or_folder():
    if len(new_file_name.get().split('.')) != 1:
        open(os.path.join(current_path.get(), new_file_name.get()), 'w').close()
    else:
        os.mkdir(os.path.join(current_path.get(), new_file_name.get()))

    new_window.destroy()
    path_change()


#Удаление файла 
def delete_item():
    try:
        selected_index = list.curselection()[0]
        picked = list.get(selected_index)
        path = os.path.join(current_path.get(), picked)
        
        # Запрос подтверждения
        if not messagebox.askyesno(
            "Подтверждение удаления",
            f"Вы уверены, что хотите удалить {'папку' if os.path.isdir(path) else 'файл'}?\n{picked}"
        ):
            return
            
        if os.path.isfile(path):
            os.remove(path)
        elif os.path.isdir(path):
            shutil.rmtree(path)  # Удаляем папку рекурсивно
            
        path_change()  # Обновляем список файлов
        
    except IndexError:
        messagebox.showwarning("Ошибка", "Ничего не выбрано!")
    except Exception as e:
        messagebox.showerror("Ошибка", f"Не удалось удалить:\n{str(e)}")


root = Tk()
root.title("DocHawk")
root.iconbitmap(r"C:\Users\dokto\Downloads\icon.ico")
root.geometry("720x400")
root.grid_columnconfigure(1, weight=1)
root.grid_rowconfigure(1,weight=1)

new_window = ''

new_file_name = StringVar(root, "Блокнот.txt", 'new_name')
current_path = StringVar(root, name='current_path', value=pathlib.Path.cwd())

current_path.trace('w',path_change)
Button(root, text='назад', command=go_back).grid(sticky=NSEW, column=0, row=0)

#Первый биндт alt + left
root.bind("<Alt-Left>", go_back)
Button(root, text='создать', command=window_new_file_or_folder).grid(sticky=NSEW, column=0, row=1,)

#Удаление 
Button(root, text='удалить', command=delete_item).grid(sticky=NSEW, column=0, row=2)


root.bind("<Delete>", lambda e: delete_item())

Entry(root, textvariable=current_path).grid(sticky=NSEW, column=1, row=0, ipady=10, ipadx=10)
list = Listbox(root)
list.grid(sticky=NSEW, column=1, row=1, ipady=10, ipadx=10)
 
list.bind('<Double-1>', change_path_by_click)
list.bind('<Return>', change_path_by_click)

path_change('')
root.mainloop()