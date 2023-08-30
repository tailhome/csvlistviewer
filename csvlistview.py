""" View for csv file viewer application. """

import os
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk, ImageDraw

""" Utility class to have one line contents of cvs file. """
class ListRow:
    def __init__(self, image, texts):
        """ set instance variables """
        self.image = image.copy()
        self.photoimage = None
        self.texts = tuple(texts)

    def get_image(self, root):
        """ convert image(PIL.Image) to photoimage(PIL.ImageTK) """
        self.photoimage = ImageTk.PhotoImage(self.image, master=root)
        return self.photoimage

    def get_texts(self):
        """ get other column texts """
        return self.texts

""" Application view class to have widget and related data. """
class ListView(tk.Frame):

    def __init__(self, app, root=None, titletext="listview"):
        """ View constructor """
        if root is None:
            root = tk.Tk()
        super().__init__(root)
        root.title(titletext)
        geomstr = app.get_geometry()
        if geomstr is None:
            root.geometry('800x480')
        else:
            root.geometry(geomstr)
        self.root = root
        self.app = app
        self.pack()
        self.build_widgets()

    def get_icon_base64(self):
        """ Returns application ICON data. """
        base64str = """R0lGODlhQABAAMQAAP//////Zv/M/8z//8zM/5n//5nM/5mZ/2bM/2bMmWaZ/2Zm
zDOZ/zNm/wCZ/wBm/////wAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAACH5BAEHABAALAAAAABAAEAAAAX/ICSOZGmeaKqubOu+cCzP
dG3feK7vfO//wKBwSCwag4GkcslsJo8ip1QKhUyvSxIBYRiIAAYFQUTwfscxrHqk
eDAaj/Gb8VBADA02Q6bGkh9mDGKAEAR2A3EiDwZ8fVMiCnskAA8NCowigoUPAI2O
TiIGkiQDbZVeeBAKdp6fTKEPI4YCmAQOBxCUBoszrqC5dQSigwcFu5gKcDS+TbJ0
dZ0IcLywrFXX2Nna2y0L3t/g4eLef4poJgAIN+Ps7OV3nScHozTt9uDvZaEHBp2l
DWbq3bv3LlEbOnkOPFhoYyDBTeYg8ALAoNOqdQ7bFZRTp5+IeRgzjtuYK9LCMQjo
/c0Q6Q6ixH6YSu0B2ZCluI0DGjAQZgmCtHMrbYYjKWqhgk4ETnJbyrSp00Q9Ekid
SrWqVakp9EW9yvVqoYAAxhCIt+WAmbFkzAwAiqKrW6p38kDaY3AOrwaY3ECyluKt
XwiI0PCKYwtNUlV2CCiDgJeF37eZ7ODxEkcaA7tlOClAEGdXi8duYSFWZODALQQH
UHvByyAMgouOQXP9sohaZ05fPK7qrBPTCtmzIS2WONaNsDeh6GzCHRt41RG7rCUy
tHDniDqK+KpwbtWp9+/gw4svQqC8+fPo06tfz779eS3u48uf314W/fv449vPz79/
efj+BTjfeAQWaCAOIQAAOw=="""
        return base64str

    def build_widgets(self):
        """ Build containing widgets on this. """
        # set icon
        image_icon = tk.PhotoImage(data=self.get_icon_base64())
        self.root.iconphoto(False, image_icon)
        # create header/footer/container
        self.header = tk.Frame(master=self.root, bg="lightgray")
        self.footer = tk.Frame(master=self.root, bg="lightgray")
        self.container = tk.Frame(master=self.root, bg="lightgreen")
        self.container.rowconfigure(0, weight=1)
        self.container.columnconfigure(0, weight=1)

        self.header.pack(side="top", fill="both", expand=False)
        self.footer.pack(side="bottom", fill="both", expand=False)
        self.container.pack(side="left", fill="both", expand=True)

        # build widgets for header
        self.title_label = tk.Label(master=self.header, text = "Image Path:",
                                    bg=self.header["bg"])
        self.title_label.pack(side="left")
        ## dropdown-list
        self.combobox = ttk.Combobox(master=self.header, style="office.TCombobox")
        self.combobox.bind('<<ComboboxSelected>>' , self.app.combo_selected(self.combobox))
        self.combobox.pack(pady=2, side="left")

        # build widgets for footer, and set event handler for button.
        self.backward_cmd = tk.Button(self.footer, text = "<<backward", width=16,
                                      compound="right", command=self.app.backward_cmd_pressed)
        self.backward_cmd.pack(side="left")

        self.forward_cmd = tk.Button(self.footer, text = "forward>>", width=16,
                                     compound="right", command=self.app.forward_cmd_pressed)
        self.forward_cmd.pack(side="left")

        self.status_label = tk.Label(master=self.footer, text = "--", bg=self.footer["bg"], width=50)
        self.status_label.pack(side="left")

        # build widgets for container
        style = ttk.Style()
        if self.app.get_rowheight() is None:
            height = 40
        else:
            height = self.app.get_rowheight()
        style.configure('Treeview', rowheight=height)
        style.configure("Treeview.Heading",font=("",14,"bold"))
        self.treeview = ttk.Treeview(master=self.container, show='tree headings')
        # generate column ids
        columns = self.app.get_columns()
        column_ids = []
        for i,item in enumerate(columns):
            column_ids.append('id%02d' % (i))
        self.treeview['columns'] = column_ids
        # fill columns
        imagecolumnwidth = self.app.get_imagewidth()
        self.treeview.column('#0',anchor='w', stretch=0, width=imagecolumnwidth)
        for item in column_ids:
            self.treeview.column(item, anchor='w') #, width=80)
        # set label of columns
        self.treeview.heading('#0',text='image', anchor='center')
        for i,item in enumerate(column_ids):
            self.treeview.heading(item, text=columns[i], anchor='w')

        # set vertial scroll-bar for treeview
        self.vscroll = ttk.Scrollbar(self.container, command = self.treeview.yview, orient = tk.VERTICAL)
        self.vscroll.grid(row = 0, column = 1, sticky = tk.NS)
        self.treeview.configure(yscrollcommand = self.vscroll.set)
        self.treeview.grid(row = 0, column = 0, sticky = tk.NSEW, rowspan=5)

    def set_status_label(self, textval):
        """ Set text to status-label. """
        self.status_label.config(text = textval)

    def fill_combobox(self, items):
        """ fill combo-box items (from app). """
        copied_items = list(items)
        self.combobox['values'] = copied_items
        self.combobox.current(0)

    def fill_treeview(self, rows):
        """ fill treeview rows. """
        # delete items
        children = self.treeview.get_children()
        for item in children:
            self.treeview.delete(item)
        # insert items
        self.rows = rows        # keep instance
        for i, row in enumerate(rows):
            idx = str(i)
            name = 'picture' + idx
            self.treeview.insert("", 'end', iid=idx, values=row.get_texts(), image=row.get_image(self))
