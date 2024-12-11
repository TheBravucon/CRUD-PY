import sqlite3
import tkinter.messagebox
from tkinter import *

create_productos_table = '''create table products (
        id integer primary key autoincrement,
        descripcion text not null,
        precio real not null,
        cantidad integer not null
    )'''

conexion = sqlite3.connect("inventario")
try:
    conexion.execute(create_productos_table)
except sqlite3.OperationalError:
    print('Ya existen las tablas')

font = 'Comic Sans MS'
input_config = {'padx': 5, 'pady': 5, 'bg': 'lightgray', 'font': (font, 10)}
root_bg = 'white'

ventana = Tk()

ventana.title('Inventario')

ventana.geometry('1280x720')

ventana.iconbitmap('youtube.ico')

ventana.config(bg='white')

ventana.state("zoomed")

frame = LabelFrame(ventana, bg='lightgray', text='Creación - Edición')
frame.pack(padx=10, pady=10)

id_producto_valor = IntVar()
nombre_producto_valor = StringVar()
precio_producto_valor = DoubleVar()
cantidad_producto_valor = IntVar()
boton_formulario_valor = StringVar(value='Crear Producto')

nombre_producto_label = Label(frame, text='Nombre de producto', bg='lightgray')
nombre_producto_label.grid(row=0, column=0, sticky= 'ew', padx = 5, pady = 5)
nombre_producto_entry = Entry(frame, textvariable=nombre_producto_valor)
nombre_producto_entry.grid(row=0, column=1, padx = 5, pady = 5)


precio_producto_label = Label(frame, text='Precio', bg='lightgray')
precio_producto_label.grid(row=1, column=0, sticky= 'ew', padx = 5, pady = 5)
precio_producto_entry = Entry(frame, textvariable=precio_producto_valor)
precio_producto_entry.grid(row=1, column=1, padx = 5, pady = 5)

cantidad_producto_label = Label(frame, text='Cantidad', bg='lightgray')
cantidad_producto_label.grid(row=2, column=0, sticky= 'ew', padx = 5, pady = 5)
cantidad_producto_entry = Entry(frame, textvariable=cantidad_producto_valor)
cantidad_producto_entry.grid(row=2, column=1, padx = 5, pady = 5)

def reset_form():
    global editando
    global nombre_producto_valor
    global precio_producto_valor
    global cantidad_producto_valor
    global boton_formulario_valor

    boton_formulario_valor.set('Crear Producto')
    nombre_producto_valor.set('')
    precio_producto_valor.set(0.0)
    cantidad_producto_valor.set(0)
    editando = False

def guardar_producto():
    global editando
    global nombre_producto_valor
    global precio_producto_valor
    global cantidad_producto_valor

    nombre_producto = nombre_producto_valor.get()
    precio_producto = precio_producto_valor.get()
    cantidad_producto = cantidad_producto_valor.get()

    if nombre_producto == '' or precio_producto == 0.0 or cantidad_producto == 0:
        tkinter.messagebox.showerror('Error','¡Coloque valor en todas las casillas porfavor!')
        return

    if editando:
        global id_producto_valor
        query = 'update products set descripcion = ?, precio = ?, cantidad = ? where id = ?'

        conexion.execute(query, (nombre_producto, precio_producto, cantidad_producto, id_producto_valor.get()))

    else:
        query = 'insert into products (descripcion, precio, cantidad) values (?, ?, ?)'

        conexion.execute(query, (nombre_producto, precio_producto, cantidad_producto))

    conexion.commit()
    productos = obtener_productos()
    refresh_products(productos)
    action = 'editado' if editando else 'creado'
    tkinter.messagebox.showinfo(f'Producto {action}', f'El producto fue {action} con exito')
    reset_form()

def refresh_products(productos):
    global listado_frame

    for widget in listado_frame.winfo_children():
        widget.destroy()
    mostrar_productos(productos)

def preparar_edicion(id):
    global nombre_producto_valor
    global precio_producto_valor
    global cantidad_producto_valor
    global boton_formulario_valor
    global editando

    print(f'Editanto producto con id: {id}')

    editando = True

    boton_formulario_valor.set('Editar producto')
    query = 'select descripcion, precio, cantidad from products where id = ?'
    producto = conexion.execute(query, (id, )).fetchone()
    id_producto_valor.set(id)
    nombre_producto_valor.set(producto[0])
    precio_producto_valor.set(producto[1])
    cantidad_producto_valor.set(producto[2])

def borrar_producto(id):
    query = 'delete from products where id = ?'
    conexion.execute(query, (id,))
    conexion.commit()
    productos = obtener_productos()
    refresh_products(productos)
    tkinter.messagebox.showinfo('Borrado', 'El producto ha sido borrado con exito')

def buscar():
    global buscador_valor
    nombre_producto = buscador_valor.get()

    query = ('select id, descripcion, precio, cantidad from products '
             'where id = cast(:searchTerm as text) or descripcion like \'%\' || cast(:searchTerm as text) || \'%\'')

    productos = conexion.execute(query, {'searchTerm': nombre_producto}).fetchall()
    refresh_products(productos)

def mostrar_todos_productos():
    productos = obtener_productos()
    refresh_products(productos)

nuevo_producto_button = Button(frame, text = 'Nuevo producto', font = (font, 10), command=reset_form)
nuevo_producto_button.grid(row = 0, column = 3, padx = 5, pady = 5)

button = Button(frame, textvariable=boton_formulario_valor, font=(font, 10), command=guardar_producto)
button.grid(row = 3, column = 0, columnspan = 2, padx=5, pady=5, sticky='ew')

frame_buscador = LabelFrame(ventana, text='Buscar')
frame_buscador.pack(padx=10, pady=10, ipadx=10, ipady=10)

buscador_valor = StringVar()

buscador_label = Label(frame_buscador, text='Buscar')
buscador_label.grid(row=0, column=0)
buscador_entry = Entry(frame_buscador, textvariable=buscador_valor)
buscador_entry.grid(row=0, column=1)

buscador_button = Button(frame_buscador, command=buscar, text='Buscar')
buscador_button.grid(row=1, column=0, columnspan=2, sticky='ew', padx=10, pady=10)

mostrar_todos_button = Button(frame_buscador, command=mostrar_todos_productos, text='Mostrar todos los productos')
mostrar_todos_button.grid(row=2, column=0, columnspan=2, sticky='ew', padx=10, pady=10)

editando = False

def scroll(canvas):
    canvas.configure(scrollregion=canvas.bbox('all'))

canvas = Canvas(ventana, bg='lightgray', bd=1, relief='raised')
canvas.pack(side=LEFT, padx=10, pady=10, fill=BOTH, expand=True)

listado_frame = LabelFrame(canvas, bg='lightgray', text='Listado de productos')
listado_frame.pack(fill=BOTH, padx=10, pady=10, expand=True)

scroll_bar = Scrollbar(ventana, command=canvas.yview)
scroll_bar.pack(side=RIGHT, fill=Y, padx=10, pady=10)

listado_frame.bind('<Configure>', lambda event: scroll(canvas))

canvas.config(yscrollcommand=scroll_bar.set)
canvas.create_window((0, 0), window=listado_frame, anchor='nw')

def mostrar_productos(productos):
    id_titulo = Label(listado_frame, text= 'Id del Producto',**input_config, bd= 2, relief='raised', width=30)
    id_titulo.grid(row= 0, column = 0, sticky= 'ew')
    nombre_producto = Label(listado_frame, text= 'Nombre del Producto',**input_config, bd= 2, relief='raised', width=30)
    nombre_producto.grid(row= 0, column = 1, sticky= 'ew')
    precio_producto = Label(listado_frame, text= 'Precio',**input_config, bd= 2, relief='raised', width=30)
    precio_producto.grid(row= 0, column = 2, sticky= 'ew')
    cantidad_producto = Label(listado_frame, text= 'Cantidad',**input_config, bd= 2, relief='raised', width=30)
    cantidad_producto.grid(row= 0, column = 3, sticky= 'ew')
    acciones = Label(listado_frame, text= 'Acciones',**input_config, bd= 2, relief='raised', width=60)
    acciones.grid(row= 0, column = 4, columnspan = 2, sticky = 'ew')

    for i in range(0, len(productos)):
        id_producto = Label(listado_frame, text = productos[i][0], **input_config, bd= 2, relief='raised', width=30)
        id_producto.grid(row = i + 1, column = 0, sticky = 'ew')

        nombre_producto = Label(listado_frame, text = productos[i][1], **input_config, bd= 2, relief='raised', width=30)
        nombre_producto.grid(row = i + 1, column = 1, sticky = 'ew')

        precio_producto = Label(listado_frame, text=f'$ {productos[i][2]:.2f}', **input_config, bd= 2, relief='raised', width=30)
        precio_producto.grid(row = i + 1, column = 2, sticky = 'ew')

        cantidad_producto = Label(listado_frame, text=productos[i][3], **input_config, bd= 2, relief='raised', width=30)
        cantidad_producto.grid(row = i + 1, column = 3, sticky = 'ew')

        id = int(productos[i][0])

        boton_editar = Button(listado_frame, text= 'Editar', bg='Gray', font = (font, 10),
                              command= lambda id = id: preparar_edicion(id), bd= 2, relief='raised', width=30)
        boton_editar.grid(row = i + 1, column = 4, sticky = 'ew')

        boton_borrar = Button(listado_frame, text='Borrar', bg='Gray', font=(font, 10),
                              command=lambda id=id: borrar_producto(id), bd=2, relief='raised', width=30)
        boton_borrar.grid(row=i + 1, column=5, sticky='ew')

def obtener_productos():
    return conexion.execute('select id, descripcion, precio, cantidad from products').fetchall()

productos = obtener_productos()
mostrar_productos(productos)

ventana.mainloop()
