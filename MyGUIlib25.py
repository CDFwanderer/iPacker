import tkinter.ttk as ttk
from tkinter import StringVar
from tkinter import font as tkFont
import numpy as np
from tkinter import *
from tkinter import messagebox
import sqlite3

class changeableEntry(ttk.Entry):
    """Class that defines the ttk.Style of the application"""

    def highlight_style(self):
        """Sets a widget to highlight mode"""

        self.style = ttk.Style()
        self.style.element_create("plain.field", "from", "clam")
        self.style.layout("Highlight.TEntry",
                      [('Entry.plain.field', {'children': [(
                          'Entry.background', {'children': [(
                              'Entry.padding', {'children': [(
                                  'Entry.textarea', {'sticky': 'nswe'})],
                                  'sticky': 'nswe'})], 'sticky': 'nswe'})],
                          'border': '2', 'sticky': 'nswe'})])

        self.style.configure("Highlight.TEntry",
                         background="green",
                         foreground="black",
                         bordercolor='red',
                         borderwidth=4)

        self['style'] = 'Highlight.TEntry'

        self.bind('<FocusIn>', self.default_style)  # <Enter> => mouse enters widget

    def default_style(self, event=None):
        self['style'] = 'TEntry' # ??
        self.unbind('<FocusIn>')

    def is_empty(self):
        """Returns True if the chabgeableEntry has no value in it, otherwise False"""

        val = self.get()

        if val is not None:
            return False
        else:
            return True

    def has_changed(self, val0):
        """Checks if the Entry has changed value since last value since val0 was enterd into the
           widget."""
        if self.get() != val0:
            self.default_style()
            return True
        else:
            return False

    # def callback(self, event=None):

class SearchableTree:
    """This is a widget with a treeview, and search-function for the
    treeview."""

    def __init__(self, master, result0=None, header=None, treeoption=None):
        """master is the widget (frame, root, toplevel..) that contains the
           SearchableTree. result0 is a list with the data that is to be inserted
           to the tree, on the form [[val1, val2, ..], [..., ...]]. treeoption
           is the browse option for the treeview, default is as for Treeview-widget
           ; options are: 'browse' = only one line can be selected, 'none' = no
           lines can be selected, and 'extended (default) = several lines can be
           selected using Ctrl."""

        self.result0 = result0
        self.master = master
        self.header = header

        self.item_values = []

        if treeoption is not None:
            self.treemode = treeoption
        else:
            self.treemode = 'extended'

        # Build the treeview-widget and populate it with stored items
        self.setup_tree(header, self.result0)
        if result0 is not None:
            self.update_tree(self.result0)

        self.tree.bind('<<TreeviewSelect>>', lambda
            name: self.tree_get_line())  # Bind a function to retrive selected line data to selection of a treeview line

    # --- Initialise the tree ---
    def update_tree(self, result):
        for row in result:
            self.tree.insert('', 'end', values=row)
            # print(row)

    def setup_tree(self, header, result):

        # --- Search area ---
        self.strVar = StringVar()
        self.strVar.set("Enter a search query")
        self.entr1 = ttk.Entry(self.master, text="Enter a search query", textvariable=self.strVar,
                               font=('Lato', 10, 'italic'), foreground="grey")
        self.entr1.grid(row=0, column=0, columnspan=9, sticky="WE", padx=(10, 10))
        self.strVar.trace("w", lambda name, mode, var: self.search_tree())

        def on_focus_out(event):
            """When the foucs leaves the searchbar, we reinput the deafult text and makes it so that the search-function
               is not triggered by the default text"""

            self.strVar.set("Enter a search query")  # needed?
            # self.entr1.unbind('<FocusOut>')
            self.entr1['font'] = ('Lato', 10, 'italic')
            self.entr1['foreground'] = "grey"

        def delete_default_search_text(event):
            """ Deletes the deafult text in the searchbar (which is set in StrVar)
                , unbinds event from entr1 (so that you can click on the seacrhbar without
                deleting what you have written, and unbinds the mouse-click event."""

            if self.entr1.get() == self.strVar.get():
                self.entr1.delete(0, END)
                # self.entr1.unbind('<Button-1>')
                self.entr1['font'] = ('Lato', 10, 'normal')
                self.entr1['foreground'] = "black"

        self.entr1.bind('<Button-1>', delete_default_search_text)  # FocusIn
        self.entr1.bind('<FocusOut>', on_focus_out)

        # --- Treeview-widget + Scrollbar ---
        self.tree = ttk.Treeview(self.master, columns=header, show="headings", selectmode=self.treemode)
        vsb = ttk.Scrollbar(self.tree, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.grid(column=0, row=1, columnspan=9, rowspan=8, sticky="nsew", in_=self.master, pady=10, padx=(10, 0))
        vsb.pack(side="right", fill=Y)
        vsb.grid_columnconfigure(0, weight=1)

        for row in np.arange(10):  # Make the treeview expand in x- and y-direction
            self.master.grid_columnconfigure(row, weight=1)
            self.master.grid_rowconfigure(row, weight=1)

        for col in header:  # Create the COLUMN-Headers in the TRREVIEW-widget
            self.tree.heading(col, text=col.title(), command=lambda c=col: self.sortby(self.tree, c, 0))
            self.tree.column(col, width=tkFont.Font().measure(col.title()))

        if result is not None:
            for i in result:
                colnum = i[1:len(result) + 1]  # Right now i = [ID, ProdName, Weight] and ID is not column in tree

                # adjust column's width if needed to fit each value
                for ix, val in enumerate(colnum):
                    col_w = tkFont.Font().measure(val)
                    if self.tree.column(header[ix], width=None) < col_w:
                        self.tree.column(header[ix], width=col_w)

    # --- METHODS used after initialisation ---
    def sortby(self, tree, col, decending):
        """Sort tree contents when a column header is clicked on"""
        # Grab values to sort
        data = [(tree.set(child, col), child) for child in tree.get_children('')]

        # if the data to be sorted is numeric change to float data =  change_numeric(data)
        # now sort the data in place

        data.sort(reverse=decending)
        for ix, i in enumerate(data):
            tree.move(i[1], '', ix)

        # switch the heading so it will sort in the opposite direction
        tree.heading(col, command=lambda col=col: self.sortby(tree, col, int(not decending)))

    def tree_get_line(self, event=None):
        items = self.tree.selection()

        # Should maybe do something with item_values instead?
        self.item_values = []
        for item in items:
            self.item_values.append(self.tree.item(item)['values'])

        # print(items)


        return items

    # --- Search-function ---
    def search_tree(self):
        """Function for searching the treeview"""
        query = self.entr1.get()  # Valued entered in widget, to be searched
        query = query.lower()  # Make sure all data is in lowercase

        query_ids = self.tree.get_children()  # Gets the items from TREEVIEW (ex. 'I001' etc)

        item_values = []  # list for all item values

        # Read the data from the 'values'-section for each item and store in list
        # item = {...,..., 'values':[whats in the columns],..}
        for item in query_ids:
            item_values.append([self.tree.item(item)['values'][0], item])

        i = 0
        for val in item_values:
            item_values[i][0] = val[0].lower()  # convert all fetched values to lowercase
            i += 1

        # Sort the items. For all items, if item not not equal query, then discard
        # list => converts filter-output to list. filter(rule to filter according to, list to filter)
        sorted_items = list(filter(lambda selected_item: selected_item[0].startswith(query), item_values))

        # Get the id of the item(s) that fullfill the query
        sort_id = []
        for i in np.arange(len(sorted_items)):
            sort_id.append(sorted_items[i][1])

        # Get the id(s) of the item(s) that are to be detached from the TREEVIEW and store them
        # so as to be able to reattach later
        to_be_detached = []
        for item_id in np.arange(len(query_ids)):
            if query_ids[item_id] not in sort_id:  # For all items, if not in equal to query, store in to_be_detached
                to_be_detached.append(query_ids[item_id])

        # Detach items not in query
        for item in to_be_detached:
            self.tree.detach(item)

        self.to_be_detached = to_be_detached  # Move to init?

        self.strVar.trace_add(("write"), lambda name, index, mode: self.reattach_to_tree(self.to_be_detached))
        # self.strVar.trace_add("write", lambda name, index, mode: self.search_tree)

    def reattach_to_tree(self, to_reattach):
        for i in to_reattach:
            self.tree.reattach(i, '', 0)  # self.tree.index(item)
        self.to_be_detached = []

        # Use the sort function to restore TREEVIEW to original sorting
        self.sortby(self.tree, 0, 0)


# Treeview-widget
class ItemList(SearchableTree):
    """This is a widget with a treeview, and search-function for the
    treeview."""

    def __init__(self, master, result0, header, db_conn, treeoption=None):
        super().__init__(master, result0, header, treeoption)

        #
        self.db_conn = db_conn
        self.master = master

        # Get the stored items from the databse
        # self.result0 = result0

        # Area for displaying the total inventory weight
        self.w_label = Label(self.master, bg="white")  # Label displaying weight
        self.w_label.grid(column=8, row=9, sticky="NE")
        self.update_weight()
        w_label_str = Label(self.master, text="Total inventory weight [g]:")
        w_label_str.grid(column=7, row=9, sticky="NE", padx=2, pady=2)

        # print(self.tree.item('I001')['values'])

    def get_line_data(self):
        """Method that returns the values of selected treview-item"""
        selected_item = self.tree.selection()  # selection gets the selected line (with mouse) from tree
        return self.tree.item(selected_item)['values']  # .item(...) returns a dict, use key 'values' to get the data

    def tree_edit_line(self, data):
        line_to_edit = list(self.tree.selection())  # Select the line to change (maybe unneded, since already selected?)
        self.tree.item(line_to_edit, values=data)  # Change the values property of the selected line, to data

        # Update weight
        self.update_weight()  # try-except clause here!

        # Update db
        # print(self.tree.item(line_to_edit))
        n_data, item_dbid = self.get_data_and_id(self.tree.item(line_to_edit))
        self.update_db("edit", n_data, item_dbid)

    def remove_from_tree(self):

        to_delete = self.tree.selection()
        data_to_delete_in_db = self.tree.item(to_delete)['values']
        # print(data_to_delete_in_db)
        self.tree.delete(to_delete)
        self.deleted = to_delete

        # Get the data and id for the item that is to be deleted
        data, item_dbid = self.get_data_and_id(data_to_delete_in_db)

        # Update db
        self.update_db("delete", data, item_dbid)

        # Update weight
        self.update_weight()

        # Creates a hotkey (ctrl-z), which undoes the deletion of an item.
        # You need to slice away last entry in list, because this is internal treeview-index (?) and is not inputted
        # in the add_to_tree-method
        self.master.bind_all('<Control-Key-z>', lambda event: self.add_to_tree(data_to_delete_in_db[:-1]))

    @staticmethod
    def get_data_and_id(data0):  # data0 is data to transform

        # make prettier!!!
        try:
            data0 = data0['values']
        except:
            pass

        id = data0[-1]  # careful (!) id is also python-specific command, like 'list' or 'for'
        # print(id)
        data = {}
        keys = ["ProductName", "Weight", "Brand", "Name", "Category"]
        i = 0
        for val in data0:
            try:
                data[keys[i]] = val
                i += 1
            except IndexError:
                pass
        return data, str(id)

    def update_tree(self, result):
        for row in result:
            # In the DB, items are stored with the following attributes (in this order): ID, ProductName, ...
            # The ID is used to identify an item (if you do not want to use its name. However, this ID is not
            # displayed in the GUI and is instead "hidden" in a sixth column in the treeview, effectively moving
            # the ID from the first position to the last, which is done below.

            row = list(row)
            row.append(row.pop(0))
            self.tree.insert('', 'end', values=row)

    def update_weight(self):
        tot_weight = 0
        for line in self.tree.get_children():
            tot_weight += self.tree.item(line)['values'][1]

        self.w_label["text"] = str(tot_weight)

    def is_in_tree(self, val):
        """Checks if val is in the tree and returns a list for true and false"""

        in_tree = np.zeros(len(self.tree.get_children()))

        for i, v in enumerate(self.tree.get_children()):
            in_tree[i] = self.tree.item(v)['values'][0:4]  # We have hidden values in the tree


    def add_to_tree(self, data_to_add, event=None):

        # Check if data_to_add is in tree
        # if not: in tree => add the data to the tree
        # else: raise a showwarning message box + indicate the entries, which already exists in
        # the tree.


        try:
            # print(data_to_add)
            # If we don't have any data_to_add, or data_to_add is empty/none.
            data = {}
            keys = ["ProductName", "Weight", "Brand", "Name", "Category"]
            i = 0
            for val in data_to_add:
                data[keys[i]] = val
                i += 1

            data["Weight"] = int(data_to_add[1])

            # Update DB
            self.update_db("add", data)

            # Update weight
            self.theCursor = self.db_conn.cursor()
            self.update_weight()
            self.theCursor.execute("SELECT * FROM Items")

            self.theCursor.execute("SELECT ID FROM Items WHERE ProductName=?", (data["ProductName"],))
            id = self.theCursor.fetchone()

            data_to_add.append(id)
            self.tree.insert('', 'end', values=data_to_add)
        except:
            pass

    def update_db(self, type, data, ID=None):
        """Read the TRREVIEW and update the DB accordingly"""

        # This is for the table "Items"
        if type == "add":  # if new item => add to db
            self.db_conn.execute("INSERT INTO Items (ProductName, Weight, Brand, Name, Category)"
                                 " VALUES (:ProductName, :Weight, :Brand, :Name, :Category)", data)
            self.db_conn.commit()
        elif type == "edit":  # if edit item => change item in db
            # Need to have ID (SQL-id) of item
            # print(data)
            self.db_conn.execute("UPDATE Items SET"
                                 " ProductName = :ProductName, Weight = :Weight, Brand = :Brand, Name = :Name, "
                                 "Category = :Category WHERE ID=" + ID, data)
            self.db_conn.commit()
        elif type == "delete":  # if delete item => delete in db
            # Need to have ID (SQL-id) of item
            # This deletes the item from the ItemPack-table
            self.db_conn.execute("DELETE FROM Items WHERE ID=" + ID)
            self.db_conn.commit()

            # Here we delete the item from the ItemPack-table
            self.db_conn.execute("DELETE FROM ItemPack WHERE ID=" + ID)

    def get_list_of_items(self):
        """Retuns a list of all items in the treeview-widget"""
        items_in_tree = self.tree.get_children()  # Treeview-items in tree
        list_of_tree_items = [None] * len(items_in_tree)  # Initialise a list with none-enties
        for i, v in enumerate(items_in_tree):
            list_of_tree_items[i] = self.tree.item(v)['values']

        return list_of_tree_items


class NewTab(ItemList):
    def __init__(self, master, db_conn, theCursor, result0=None, header=None, treeoption=None, open_pack=False):
        super().__init__(master, result0, header, treeoption)

        self.is_saved = bool

        # ----- Database-thingies -----
        self.theCursor = theCursor
        self.db_conn = db_conn

        mainframe = Frame(master)
        mainframe.grid()

        # Create a grid for master
        for row in np.arange(2):
            mainframe.rowconfigure(row, weight=1)
            mainframe.columnconfigure(row, weight=1)

        # ----- Initialise frames for widgets -----
        self.tree_frame = ttk.Frame(mainframe)
        self.note_frame = ttk.LabelFrame(mainframe, text="Comment Area")
        self.bttn_frame = Frame(mainframe)

        self.tree_frame.grid(row=0, column=0, rowspan=2, sticky="NWES")
        self.note_frame.grid(row=1, column=1, sticky="NSWE", pady=10, padx=10)
        self.bttn_frame.grid(row=0, column=1, sticky="NSWE", pady=10, padx=10)

        # # Create a grid for tree-frame
        for row in np.arange(10):
            self.tree_frame.rowconfigure(row, weight=1)
            self.tree_frame.columnconfigure(row, weight=1)

        # bttn_area = ButtonsArea(self.bttn_frame, self)

        if open_pack == True:
            self.open_pack()
            self.is_saved = True
        else:
            self.is_saved = False

    def open_pack(self):
        try:
            result = self.theCursor.execute("SELECT PackName FROM PackTravel")
            data = result.fetchall()

            # Open a dialog-win with all saved packs and get the user to open one of those,
            # set treview to selectmode="browse". Once a pack is selected, the button "open
            open_pack_win = Toplevel()  # Create a TopLevel-widget, in which to place the dialog-win
            local_frame = Frame(open_pack_win)
            local_frame.pack(fill=BOTH, expand=True)

            load_p = LoadPacks(local_frame, data, header=["Pack Name"], treeoption='browse', parent=open_pack_win)
            pack_to_load = load_p.get_data()  # Get the name of the pack to load

            items_to_load0 = self.theCursor.execute("SELECT ID, ProductName FROM ItemPack WHERE PackName=?",
                                                    (pack_to_load[0][0],))
            items0 = items_to_load0.fetchall()

            result = []
            for item in items0:
                self.theCursor.execute(
                    "SELECT ID, ProductName, Weight, Brand, Name, Category FROM Items WHERE ProductName=?", (item[1],))
                result.append(self.theCursor.fetchall()[0])
        except AttributeError:
            pass

    def create_new_pack(self):
        try:
            # Entry for pack-name
            entr_pack_name = ttk.Entry(bttn_frame)
            entr_pack_name.pack()
            bttn_get_name = ttk.Button(bttn_frame, text="Update pack-name",
                                       command=lambda: self.update_name(entr_pack_name))
            bttn_get_name.pack()

            # new_pack_name = popupWindow(self.new_tab)
            self.nb.tab(self.nb.index("current"), text=self.default_pack_name)  # new_pack_name.value

            # Variable to keep track if current pack is saved
            is_pack_saved = False

            # Add to the tablist-dict [tab-object, is_pack_saved, NewTab-obj]

            self.tablist[self.nb.index("current")] = [self.new_tab, is_pack_saved, self.new_pack]
        except AttributeError:
            pass

    def save_pack(self):
        # check all items in TREEVIEW
        # if item is new => add to db
        # if item exists in db for this pack => do nothing

        curr_pack_name = self.nb.tab(self.nb.select(), "text")

        result = self.theCursor.execute("SELECT PackName FROM PackTravel")
        in_table = result.fetchall()
        to_check = [n[0] for n in in_table]

        if curr_pack_name in to_check:
            answer = messagebox.showwarning("",
                                            " " + curr_pack_name + " already exists! Do you want to override it? \n If no, please edit the pack-name and press save again.",
                                            type="yesno")
            if answer == "yes":

                # In this case, we need to UPDATE the database where it is needed. That means, overwriting the values for
                # product names that were previously associated with another pack with the current packname

                # Get the data from the ItemPack-table (that is the table connecting items with packs)
                result = self.theCursor.execute("SELECT ProductName, PackName FROM ItemPack")
                in_table = result.fetchall()
                # print(in_table)

                # Set the is_saved-variable for this tab to True, thereby indicating that this tab is saved
                # is_saved MUST BE UPDATED the same way as self.tablist!!!!!!!!!!!
                self.tablist[self.nb.index("current")][1] = True

                # curr_pack = self.tablist[self.nb.index("current")]
                curr_items = self.new_pack.tree.get_children()

                for item in curr_items:
                    curr_item_value = self.new_pack.tree.item(item)['values']
                    if curr_item_value in in_table:
                        # self.db_conn.execute("UPDATE ItemPack SET ProductName= :ProductName WHERE PackName= :PackName",
                        #                      {"ProductName": curr_item_value[0], "PackName": curr_pack_name})
                        # self.db_conn.commit()
                        pass
                    elif (curr_item_value[0], curr_pack_name) not in in_table:
                        self.db_conn.execute("INSERT INTO ItemPack (ProductName, PackName) VALUES (?, ?)",
                                             (curr_item_value[0], curr_pack_name))
                        self.db_conn.commit()

                # Set the is_saved-variable to True, thereby allowing the user to to exit tab
                # without displaying a warning-msgbox
                self.tablist[self.nb.index("current")][1] = True
            elif answer == "no":
                # Just continue back to the current tab
                pass
        else:
            # Get the data from the ItemPack-table (that is the table connecting items with packs)
            result = self.theCursor.execute("SELECT ProductName, PackName FROM ItemPack")
            in_table = result.fetchall()
            # print(in_table)

            # Set the is_saved-variable for this tab to True, thereby indicating that this tab is saved
            # is_saved MUST BE UPDATED the same way as self.tablist!!!!!!!!!!!
            self.tablist[self.nb.index("current")][1] = True

            # curr_pack = self.tablist[self.nb.index("current")]
            curr_items = self.new_pack.tree.get_children()
            for item in curr_items:
                curr_item_value = self.new_pack.tree.item(item)['values']
                if [curr_item_value, curr_pack_name] not in in_table:
                    self.db_conn.execute("INSERT INTO ItemPack (ProductName, PackName) VALUES (?, ?)",
                                         (curr_item_value[0], curr_pack_name))
                    self.db_conn.commit()

            self.db_conn.execute("INSERT INTO PackTravel (PackName) VALUES (?)", (curr_pack_name,))
            self.db_conn.commit()

            # Set the is_saved-variable to True, thereby allowing the user to to exit tab
            # without displaying a warning-msgbox
            self.tablist[self.nb.index("current")][1] = True

    def quit_rutine(self):
        """Upon exiting a tab, this method is called to ask check if the user has saved the
           current pack. If the user has saved the current pack, the tab is closed; if not
           the user is asked if he or she wants to exit anyway or save the pack"""

        def update_tabs():
            """This function updates the dictionary keys for the dictionary (self.tablist)
               that contains all the tabs that are open. OBS tab_id changes if tabs are
               deleted"""
            curr_pack_id = self.nb.index("current")  # get the id of the currently selected tab
            num_keys = list(self.tablist.keys())  # get a list of all tab ids, which are the keys in self.tablist
            for key in num_keys:
                if key > curr_pack_id:
                    # if the key > curr_tab_id, we have to decrease key with 1. e.g total tabs is 5,
                    # tab to be deleted is 3 => tabs 4 & 5 will get id (key-value) 3 & 4 resp.
                    self.tablist[key - 1] = self.tablist[key]
                    del self.tablist[key]
                elif key == curr_pack_id:
                    curr_pack, a, b = self.tablist[self.nb.index("current")]
                    del self.tablist[key]
                    curr_pack.destroy()

        if self.tablist[self.nb.index("current")][1] == True:  # self.is_saved[self.nb.index("current")] == True:
            update_tabs()
        else:
            answer = messagebox.askyesno("Save?", "Do you want to cancel without saving?")
            if answer == True:  # Answered "Yes" to "Do you want to cancel without saving?"
                update_tabs()
            elif answer == False:  # Answered "No" to "Do you want to cancel without saving?"
                curr_pack, a, b = self.tablist[self.nb.index("current")]
                self.save_pack()
                # MAYBE DO NOTHING, and let the user press save?

    def remove_item(self):
        self.tablist[self.nb.index("current")][1] = False

        curr_tab_obj = self.tablist[self.nb.index("current")][2]
        curr_tab_obj.remove_from_tree()

        # to_delete = curr_tab_obj.item_values
        # data_to_delete_in_db = curr_tab_obj.tree.item(to_delete) #?
        # curr_tab_obj.remove_from_tree(data_to_delete_in_db)

    def add_items(self):
        """Open a window containing all items in the inventory, with add buttons"""
        curr_pack = self.tablist[self.nb.index("current")][2]  # Is the current NewTab-object that we work with
        curr_new_tab = self.tablist[self.nb.index("current")][0]  # Is the current tab in the notebook
        # self.data is the all the items stored in the db
        # self.items_table is the name of the table in the db, where all items are stored
        self.tablist[self.nb.index("current")][1] = False  # We have now added items, thus is_saved is False

        # self.tablist[self.nb.index("current")] Get the current tab and update WEIGHT!

        add_items_win = ChoiceInventory(curr_new_tab, self.data, self.db_conn, self.theCursor, self.items_table,
                                        curr_pack)

    def add_to_tree(self, data_to_add):
        # Check if item already exists in Treeview, if not in treeview => add
        for line in data_to_add:
            if len(self.tree.get_children()) == 0:
                self.tree.insert('', 'end', values=line)
            else:
                check_names = []
                for item in self.tree.get_children():
                    check_names.append(self.tree.item(item)['values'][0])
                if line[0] not in check_names:
                    self.tree.insert('', 'end', values=line)

    def update_name(self, entr_pack_name):
        old_pack_name = self.nb.tab(self.nb.index("current"))['text']
        new_pack_name = entr_pack_name.get()

        # --- Clear entry-box and update tab-text ---
        self.nb.tab(self.nb.index("current"), text=new_pack_name)
        entr_pack_name.delete(0, 'end')

        #  --- UPDATE old name, in db, for this pack to new nam ---
        # Change name in PackTravel-table
        self.db_conn.execute("UPDATE PackTravel SET PackName= :PackName WHERE PackName= :OldPackName",
                             {"PackName": new_pack_name, "OldPackName": old_pack_name})
        self.db_conn.commit()

        # Change name in ItemPack-table
        result = self.theCursor.execute("SELECT ProductName FROM ItemPack WHERE PackName= :PackName",
                                        {"PackName": old_pack_name})
        result.fetchall()

        for i in result:
            self.db_conn.execute("UPDATE ItemPack SET PackName= :PackName", {"PackName": new_pack_name})
            self.db_conn.commit()

    @property  # ???
    def default_pack_name(self):
        """initialises with self.deafult_pack_no = "00" and then updates with 1 for each
        new pack that is created, e.g. first new pack that is created gets the
        pack_no = "01", the next pack gets "02" and so on."""

        if int(self.default_pack_no) + 1 > 10:
            self.default_pack_no = str(int(self.default_pack_no) + 1)
        else:
            self.default_pack_no = "0" + str(int(self.default_pack_no) + 1)

        return "pack" + self.default_pack_no


class LoadPacks(SearchableTree):
    def __init__(self, master, result0, header, treeoption, parent):
        """Build a list of all saved packs with an "open pack"-button"""
        super().__init__(master, result0, header, treeoption)
        self.parent = parent

        parent.geometry("400x300")

        self.bttn_open_pack = ttk.Button(master, text="Open selected pack", command=self.get_data, state=DISABLED)
        self.bttn_open_pack.grid(row=1, column=9, padx=10)

        parent.focus_set()  # Focus on popup window
        parent.wait_window()  # Wait with further operations until widget is

    def get_data(self):
        """Send the selected pack-name + data to a NewTab-obj"""
        self.parent.destroy()
        return self.item_values

    def tree_get_line(self, event=None):
        super().tree_get_line(event=None)
        self.bttn_open_pack["state"] = ACTIVE  # Only allow the user to press the button if a new pack is selected!


class ButtonsArea:
    def __init__(self, master_gui, master_obj):
        # --- Create buttons ---
        # bttn_frame = ttk.Frame(master_gui)
        # bttn_frame.grid(row=0, column=1)
        bttn_add_item = ttk.Button(master_gui, text="Add new items", command=master_obj.add_items)
        bttn_add_item.pack()
        bttn_remove_item = ttk.Button(master_gui, text="Remove item", command=master_obj.remove_item)
        bttn_remove_item.pack()
        bttn_save_pack = ttk.Button(master_gui, text="Save pack", command=master_obj.save_pack)
        bttn_save_pack.pack()
        bttn_exit_pack = ttk.Button(master_gui, text="Exit pack",
                                    command=master_obj.quit_rutine)  # Should trigger messagebox, if not saved!
        bttn_exit_pack.pack()

        # --- Entry for pack-name ---
        entr_pack_name = ttk.Entry(master_gui)
        entr_pack_name.pack()
        bttn_get_name = ttk.Button(master_gui, text="Update pack-name",
                                   command=lambda: master_obj.update_name(entr_pack_name))
        bttn_get_name.pack()

# ------- POPUP-windows ---------
# Window for nameing new pack
class popupWindow:
    def __init__(self, parent):
        self.pack_name_win = Toplevel(parent)
        self.pack_name_win.geometry("250x100")
        for row in np.arange(10):
            self.pack_name_win.rowconfigure(row, weight=1)
            self.pack_name_win.columnconfigure(row, weight=1)
        self.l = ttk.Label(self.pack_name_win, text="What is the name of your new pack")
        self.l.grid(row=0, column=0, padx=10, pady=10)
        self.e = ttk.Entry(self.pack_name_win)
        self.e.grid(row=1, column=0, columnspan=2, padx=10, pady=(0, 10))
        self.b = Button(self.pack_name_win, text='Ok', command=self.cleanup)
        self.b.grid(row=2, column=0, columnspan=2)
        self.pack_name_win.focus_set()  # Focus on popup window
        self.pack_name_win.wait_window()  # Wait with further operations until widget is destroyed

    def cleanup(self):
        self.value = self.e.get()
        self.pack_name_win.destroy()


# Window for getting items for your pack
class ChoiceInventory:
    """A popup-window, in which you can choose items for individual packs"""

    def __init__(self, master, db_data, db_conn, theCursor, table, new_pack):

        self.new_pack = new_pack
        self.master = master

        # Create a TopLevel-widget and set focus to it
        self.add_items_win = Toplevel(master)
        self.add_items_win.geometry("500x300")

        self.add_items_win_frame = ttk.Frame(self.add_items_win)
        self.add_items_win_frame.pack(fill=BOTH, expand=True)

        self.add_items_win.title("Add items to pack")
        self.add_items_win.focus_set()

        # Get the name of the columns in table
        theCursor.execute("PRAGMA TABLE_INFO(" + table + ")")
        header = [nameTuple[1] for nameTuple in theCursor.fetchall()]
        del header[-1]  # deletes the comment-column header in the list
        del header[0]

        self.db_conn = db_conn

        # Get the stored items from the databse
        self.db_data = db_data

        # Build the treeview-widget and populate it with stored items
        self.setup_tree(header, self.db_data)
        self.update_tree(self.db_data)
        self.tree.bind('<<TreeviewSelect>>', lambda
            name: self.tree_get_line())  # Bind a function to retrive selected line data to selection of a treeview line

        # Add to Pack-button
        bttn_add_to_pack = ttk.Button(self.add_items_win_frame, text="Add items to pack",
                                      command=lambda: self.new_pack.add_to_tree(self.item_values))
        bttn_add_to_pack.grid(row=5, column=9, padx=10, pady=10)

        self.selected_items = []

    def tree_get_line(self, event=None):
        items = self.tree.selection()
        self.item_values = []
        for item in items:
            self.item_values.append(self.tree.item(item)['values'])

    @staticmethod
    def get_data_and_id(data0):  # data0 is data to transform
        id = data0['values'][5]
        data = {}
        keys = ["ProductName", "Weight", "Brand", "Name", "Category"]
        i = 0
        for val in data0["values"]:
            try:
                data[keys[i]] = val
                i += 1
            except IndexError:
                pass
        return data, str(id)

    def update_tree(self, result):
        for row in result:
            item_id = row[0]
            item_prodname = row[1]
            item_weight = row[2]
            item_brand = row[3]
            item_name = row[4]
            item_cat = row[5]
            self.tree.insert('', 'end', values=[item_prodname, item_weight, item_brand, item_name, item_cat, item_id])

    def setup_tree(self, header, result):
        # Search area
        self.strVar = StringVar()
        self.entr1 = ttk.Entry(self.add_items_win_frame, text="Enter a search query", textvariable=self.strVar,
                               font=('Arial', 10, 'italic'), foreground="grey")

        self.entr1.grid(row=0, column=0, columnspan=8, sticky="WE", padx=(10, 10))
        self.strVar.trace("w", lambda name, mode, var: self.search_tree())

        # Treeview-widget + Scrollbar
        self.tree = ttk.Treeview(self.add_items_win_frame, columns=header, show="headings")
        vsb = ttk.Scrollbar(self.tree, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.grid(column=0, row=1, columnspan=9, rowspan=8, sticky=N + W + E + S, pady=10, padx=(10, 0))
        for row in np.arange(9):
            self.add_items_win_frame.grid_rowconfigure(row, weight=1)
            self.add_items_win_frame.grid_columnconfigure(row, weight=1)
        vsb.pack(side="right", fill=Y)
        vsb.grid_columnconfigure(0, weight=1)

        # print(self.add_items_win_frame.grid_size())

        # Make the treeview expand in x- and y-direction
        # self.add_items_win_frame.grid_columnconfigure(0, weight=1)
        # self.add_items_win_frame.grid_rowconfigure(0, weight=1)

        # Create the COLUMN-Headers in the TRREVIEW-widget
        for col in header:
            self.tree.heading(col, text=col.title(), command=lambda c=col: self.sortby(self.tree, c, 0))
            self.tree.column(col, width=tkFont.Font().measure(col.title()))

        for i in result:
            colnum = i[1:len(result) + 1]  # Right now i = [ID, ProdName, Weight] and ID is not column in tree

            # adjust column's width if needed to fit each value
            for ix, val in enumerate(colnum):
                # print(ix, val)
                col_w = tkFont.Font().measure(val)
                if self.tree.column(header[ix], width=None) < col_w:
                    self.tree.column(header[ix], width=col_w)

        # print(self.add_items_win_frame.grid_size())

    def sortby(self, tree, col, decending):
        """Sort tree contents when a column header is clicked on"""
        # Grab values to sort

        data = [(tree.set(child, col), child) for child in tree.get_children()]

        # if the data to be sorted is numeric change to float data =  change_numeric(data)
        # now sort the data in place

        data.sort(reverse=decending)
        for ix, i in enumerate(data):
            tree.move(i[1], '', ix)

        # switch the heading so it will sort in the opposite direction
        tree.heading(col, command=lambda col=col: self.sortby(tree, col, int(not decending)))

    # --- Search-function ---
    def search_tree(self):
        """Function for searching the treeview"""
        query = self.entr1.get()  # Valued entered in widget, to be searched
        query = query.lower()  # Make sure all data is in lowercase

        query_ids = self.tree.get_children()  # Gets the items from TREEVIEW (ex. 'I001' etc)

        item_values = []  # list for all item values

        # Read the data from the 'values'-section for each item and store in list
        # item = {...,..., 'values':[whats in the columns],..}
        for item in query_ids:
            item_values.append([self.tree.item(item)['values'][0], item])

        i = 0
        for val in item_values:
            item_values[i][0] = val[0].lower()  # convert all fetched values to lowercase
            i += 1

        # Sort the items. For all items, if item not not equal query, then discard
        # list => converts filter-output to list. filter(rule to filter according to, list to filter)
        sorted_items = list(filter(lambda selected_item: selected_item[0].startswith(query), item_values))

        # Get the id of the item(s) that fullfill the query
        sort_id = []
        for i in np.arange(len(sorted_items)):
            sort_id.append(sorted_items[i][1])

        # Get the id(s) of the item(s) that are to be detached from the TREEVIEW and store them
        # so as to be able to reattach later
        to_be_detached = []
        for item_id in np.arange(len(query_ids)):
            if query_ids[item_id] not in sort_id:  # For all items, if not in equal to query, store in to_be_detached
                to_be_detached.append(query_ids[item_id])

        # Detach items not in query
        for item in to_be_detached:
            self.tree.detach(item)

        self.to_be_detached = to_be_detached  # Move to init?

        self.strVar.trace_add(("write"), lambda name, index, mode: self.reattach_to_tree(self.to_be_detached))
        # self.strVar.trace_add("write", lambda name, index, mode: self.search_tree)

    def reattach_to_tree(self, to_reattach):
        for i in to_reattach:
            self.tree.reattach(i, '', 0)  # self.tree.index(item)
        self.to_be_detached = []

        # Use the sort function to restore TREEVIEW to original sorting
        self.sortby(self.tree, 0, 0)


class LoadPacks(SearchableTree):
    def __init__(self, main, master, result0, header, treeoption, parent, get_pack_action):
        """Build a list of all saved packs with an "open pack"-button
           main = Main-class
           master = local_frame,
           result0 = data (input from db)
           treeoption = how the user can brows the reeview
           parent = in this case, a Toplevel-widget"""
        super().__init__(master, result0, header, treeoption)

        self.parent = parent
        self.main = main
        self.get_pack_action = get_pack_action

        parent.geometry("400x300")

        self.bttn_open_pack = ttk.Button(master, text="Open selected pack", command=self.get_data, state=DISABLED)
        self.bttn_open_pack.grid(row=1, column=9, padx=10)

        # --- Sets foucs to the first row in the treeview with packs to load ---
        parent.focus_set()  # Focus on popup window
        default_foucus_item = self.tree.get_children()[0]
        self.tree.focus_set()
        self.tree.selection_set((default_foucus_item, default_foucus_item))
        self.tree.focus(default_foucus_item)

        self.tree.bind('<Return>', self.get_data)  # Bind return-key to the same method as bttn_open_pack

        parent.wait_window(parent)  # Wait with further operations until widget is destroyed?

    def get_data(self, event=None):
        """Send the selected pack-name + data to a NewTab-obj"""
        pack_to_load = self.tree.item(self.tree.selection())['values'][0]
        self.get_pack_action(pack_to_load)
        self.parent.destroy()
        # return pack_to_load

    def tree_get_line(self, event=None):
        super().tree_get_line(event=None)
        self.bttn_open_pack["state"] = ACTIVE  # Only allow the user to press the button if a new pack is selected!

# Window for adding new items
class ChildWindow:
    """A popup-window for inputing new items"""

    def __init__(self, root, parent,
                 items):  # (self [this class], root [main window], parent [Inventory-obj], items [ItemList-obj])

        self.parent = parent
        self.root = root
        self.items = items

        self.new_win = Toplevel(master=root, width=300, height=200)
        self.new_win.title("Add new item")
        # self.new_win.geometry("300x200")
        self.new_win.focus_set()  # Focus on popup window

        # ENTRY-widgets
        self.ent_pn = ttk.Entry(self.new_win)
        vcmd = (root.register(self.onValidate), '%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
        self.ent_weight = ttk.Entry(self.new_win, validate="key", validatecommand=vcmd)
        self.ent_brand = changeableEntry(self.new_win) # , style='Highlight.TEntry')
        self.ent_name = ttk.Entry(self.new_win)
        # self.ent_cat = ttk.Entry(self.new_win)

        # How to ad a combo-box
        self.boxVal = StringVar()
        self.combo = ttk.Combobox(self.new_win, textvariable=self.boxVal)
        self.combo['values'] = ('X', 'Y', 'Z')

        # LABEL-widgets
        self.lb_ent_pn = ttk.Label(self.new_win, text="Product Name")
        self.lb_ent_weight = ttk.Label(self.new_win, text="Weight [g]")
        self.lb_ent_brand = ttk.Label(self.new_win, text="Brand")
        self.lb_ent_name = ttk.Label(self.new_win, text="Name")
        self.lb_ent_cat = ttk.Label(self.new_win, text="Category")

        # Pack widgets
        self.lb_ent_pn.grid(row=0, column=0, padx=10, pady=(10, 0))
        self.lb_ent_weight.grid(row=0, column=1, padx=10, pady=(10, 0))
        self.lb_ent_brand.grid(row=0, column=2, padx=10, pady=(10, 0))
        self.lb_ent_name.grid(row=0, column=3, padx=10, pady=(10, 0))
        self.lb_ent_cat.grid(row=0, column=4, padx=10, pady=(10, 0))

        self.ent_pn.grid(row=1, column=0, padx=10, pady=(5, 10))
        self.ent_weight.grid(row=1, column=1, padx=10, pady=(5, 10))
        self.ent_brand.grid(row=1, column=2, padx=10, pady=(5, 10))
        self.ent_name.grid(row=1, column=3, padx=10, pady=(5, 10))
        # self.ent_cat.grid(row=1, column=4, padx=10, pady=(5, 10))
        self.combo.grid(row=1, column=4, padx=10, pady=(5, 10))

        # Button adding item to TREEVIEW
        self.btn_text = StringVar()
        self.btn_text.set("Add item to Inventory")
        self.add_bttn = ttk.Button(self.new_win, textvariable=self.btn_text,
                                   command=lambda: items.add_to_tree(self.get_entries()))

        self.add_bttn.bind('<Return>', lambda event: items.add_to_tree(
            self.get_entries()))  # Allow user to hit enter to input item in inventory, e.g after tabbing to bttn
        self.add_bttn.grid(row=1, column=5, padx=10, pady=(5, 10))
        self.new_win.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.ent_pn.focus_set()  # Sets the user's focus to ent_pn
        self.ent_brand.highlight_style()


    def onValidate(self, d, i, P, s, S, v, V, W):
        try:
            S = float(S)  # Try to convert S [value in weight-entry] to float, if float => allow user to input S
            return True
        except:
            self.root.bell()
            return False

    def get_entries(self):
        """Returns the entered values in a list"""

        if {self.ent_pn.get()}.issubset([i[0] for i in
                                         self.items.get_list_of_items()]):  # in this case '{..}' creates a set, which is slightly faster
            # The product name for the new item, that we want to add, already exists in the treeview, so
            # we must choose a new item name
            messagebox.showerror("Error", "The product name already exists, please choose a new product name.")
            self.ent_pn.focus_set()
        else:
            # There is no duplicate productname in the treeview, so we can add the new item to the inventory
            return [self.ent_pn.get(), self.ent_weight.get(), self.ent_brand.get(),
                    self.ent_name.get(), self.combo.get()]  # ent_cat is alt., if we don not use combobox

    def on_closing(self):
        """When closing the ChildWindow-object, execute the following"""
        self.parent.bttn_add_item[
            "state"] = NORMAL  # Access bttn2 (aka "Remove Item" and set to NORMAL state, aka clickable
        self.parent.bttn_remove_item["state"] = NORMAL
        self.new_win.destroy()  # Quit the TOPLEVEL-widget, aka the ChildWindiw for inputing new items


# Window for editing items
class ChildWindowEdit(ChildWindow):
    def __init__(self, root, parent, items, data):
        super().__init__(root, parent, items)
        # idea: save entries form above in a list, and iterate over it

        self.orig_pn = data[0]

        # --- Get original data, which we want to edit, from tree ---
        self.ent_pn.insert(END, data[0])
        self.ent_weight.insert(END, data[1])
        self.ent_brand.insert(END, data[2])
        self.ent_name.insert(END, data[3])
        # self.ent_cat.insert(END, data[4])
        # self.combo.

        # --- Reconfigure the button ---
        self.btn_text.set("Edit item")
        self.add_bttn.configure(
            command=self.parent.edit_tree)  # parent = Inventory-obj, invoke edit_tree-method when pressing button
        self.add_bttn.bind('<Return>', lambda event: self.parent.edit_tree())  # Allow user to hit enter to input item in inventory, e.g after tabbing to bttn
        self.new_win.grab_set()  # lock the parent window (Inventory), so that it is not clickabe when TopView-win is open

        def update_orig_pn(event):
            self.orig_pn = self.ent_pn.get()

        # update the original product name-variable, when left-click or return is released
        self.add_bttn.bind('<ButtonRelease-1><KeyRelease-Return>', update_orig_pn)

    def get_entries(self):
        """Returns the entered values in a list"""

        # Ok to use tuple?
        data_to_return = [self.ent_pn.get(), self.ent_weight.get(), self.ent_brand.get(),
                          self.ent_name.get(), self.combo.get()]  # ent_cat is alt., if we don not use combobox

        # Can this be the same in both ChildWindows? So no need to override method?
        if self.ent_pn.get() != self.orig_pn:
            if {self.ent_pn.get()}.issubset([i[0] for i in
                                             self.items.get_list_of_items()]):  # in this case '{..}' creates a set, which is slightly faster
                # The product name for the new item, that we want to add, already exists in the treeview, so
                # we must choose a new item name
                messagebox.showerror("Error", "The product name already exists, please choose a new product name.")
                self.ent_pn.focus_set()
            else:
                # There is no duplicate productname in the treeview, so we can add the new item to the inventory
                return data_to_return
        else:
            return data_to_return
