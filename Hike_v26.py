from tkinter import *
import sqlite3
import numpy as np
import tkinter.font as tkFont
import tkinter.ttk as ttk
from tkinter import messagebox
from MyGUIlib25 import ItemList, ChoiceInventory, LoadPacks, ChildWindow, ChildWindowEdit, NewTab

"""
IDEAS:
- Use class for the treeview (class ItemList:)
- USE more functions for initialisation
- Use the child window for both adding and editing items
- Ability for the user to choose which columns should be displayed in the TREEVIEW
- Prevent error from occuring when pressing "Edit item", before selecting a line in the TREEVIEW
  maybe by using a messagebox to instruct the user to select a line to change?
- Error-handling if weight not numbers in add_to_tree (ItemsList)
- Close add-window upon pressing: Add to Inventory?
- use dump (SQL) to backup db?
- html or Markdown or LaTeX for printing of packing lists?
- Work with consistent names and data structures!
- Paint "function-flow", i.e. what functions invoke each other and what data do they communicate and in which form?
- Test default name for new pack, and let the user change it later!
- Changed name => update old pack or create a new pack?
- Make everything in the tabs internal to either Inventory-class or NewTab-classs
- Delete multiple items at once
- Make a Ctrl-z like command, e.g. if you have deleted a n item in db and regret the deletion
- Edited items should not be have same name as existing items; you should be able to update existing item weight
- tag packs, e.g. #winter or #summer-vacation
- Make it so that the 'category'-column gets some extra space to the right when the app is launched
- See to it, that all toplevel-widgets get the same icon as main-window (idea: extra input-var for this)
"""


# Credit for icon
# <div>Icons made by <a href="http://www.freepik.com" title="Freepik">Freepik</a> from <a href="https://www.flaticon.com/" title="Flaticon">www.flaticon.com</a> is licensed by <a href="http://creativecommons.org/licenses/by/3.0/" title="Creative Commons BY 3.0" target="_blank">CC 3.0 BY</a></div>
#

# ------------- Class definitions ---------------

# Main application
class Main:
    """Main app"""

    def __init__(self, root):
        """Create menus and the main tab"""

        self.default_pack_no = "00"
        self.items_table = "Items"

        # A dict of all tabs
        self.tablist = {}

        # Configure main window (root)
        root.title("pyKer - the smart hiker's choice")  # Sassy slogan - always good
        root.geometry("1000x500")

        # Set the icon for the program. OBS must be .ico (use Gimp to edit icon file)
        # root.iconbitmap('rucksack.ico')

        self.root = root

        # --- INITIALISE Menus ---
        the_menu = Menu(root)
        file_menu = Menu(the_menu, tearoff=0)
        data_menu = Menu(the_menu, tearoff=0)

        # Configure the file-menu
        file_menu.add_command(label="Create New Pack", command=self.create_new_pack, accelerator='ctrl+n')
        file_menu.add_command(label="Open Pack", command=self.open_pack, accelerator='ctrl+o')
        file_menu.add_command(label="Define categories", command=self.define_cat)
        file_menu.add_separator()
        file_menu.add_cascade(label="Data Source", menu=data_menu)
        file_menu.add_separator()
        file_menu.add_command(label="Quit", command=self.root.quit)

        # Hotkeys for file-menu
        root.bind_all('<Control-Key-o>', self.open_pack)  # Allows user to press ctrl+o. Needs event in open_pack(..)
        root.bind_all('<Control-Key-n>', self.create_new_pack)

        # Configure data-menu
        # This is where you are supposed to be able to choose data-source, from which to import your packs
        # if you already have a pack
        data_menu.add_command(label="Import from excel")
        data_menu.add_command(label="Import from existing database")

        # Configure help-menu
        help_menu = Menu(the_menu, tearoff=0)
        help_menu.add_command(label="Show Short-cuts")
        help_menu.add_command(label="How to import existing packs (excel)")
        the_menu.add_cascade(label="File", menu=file_menu)
        the_menu.add_cascade(label="Help", menu=help_menu)
        root.config(menu=the_menu)

        # --- MAIN TAB ---
        # which contains the Inventory-obj (which displays all pack-items in the db (table-name: 'Items')
        maintabframe = ttk.Frame(root)
        maintabframe.pack(fill=BOTH, expand=True)
        self.nb = ttk.Notebook(maintabframe)
        self.nb.pack(fill=BOTH, expand=True)

        # Get the data from database, a cursor, and db-connection
        self.data, self.theCursor, self.db_conn = self.setup_db()

        mainpage = ttk.Frame(self.nb)
        inv = Inventory(mainpage, self.data, self.theCursor, self.db_conn)
        self.nb.add(mainpage, text="Inventory")

        self.tablist[self.nb.index("current")] = mainpage # Add mainpage (i.e. the window with inventory in it) to the tablist

    def define_cat(self):
        pass

    def open_pack(self, event=None):
        """Open database and send, in order to send info to open_pack-win"""

        try: # if db-table with PackTravels contains anything
            result = self.theCursor.execute("SELECT PackName FROM PackTravel")
            data = result.fetchall()

            # Open a dialog-win with all saved packs and get the user to open one of those,
            # set treview to selectmode="browse". Once a pack is selected, the button "open
            open_pack_win = Toplevel()  # Create a TopLevel-widget, in which to place the dialog-win
            local_frame = Frame(open_pack_win)
            local_frame.pack(fill=BOTH, expand=True)

            # Cool! You can pass object methods as parameters!
            self.load_p = LoadPacks(main=self, master=local_frame, result0=data, header=["Pack Name"], treeoption='browse', parent=open_pack_win, get_pack_action=self.get_open_pack)
            # print(self.pack_to_load)

            items_to_load0 = self.theCursor.execute("SELECT ID, ProductName FROM ItemPack WHERE PackName=?", (self.pack_to_load,))
            items0 = items_to_load0.fetchall()

            result = []
            for item in items0:
                self.theCursor.execute("SELECT ID, ProductName, Weight, Brand, Name, Category FROM Items WHERE ProductName=?", (item[1],))
                # print(self.theCursor.fetchall())
                result.append(self.theCursor.fetchall()[0])

            self.new_tab = ttk.Frame(self.nb)
            self.new_tab.pack(fill=BOTH, expand=True)

            # Create a grid for frame-frame
            for row in np.arange(2):
                self.new_tab.rowconfigure(row, weight=1)
                self.new_tab.columnconfigure(row, weight=1)

            try:
                self.nb.add(self.new_tab, text=self.pack_to_load)
                tree_frame = ttk.Frame(self.new_tab)
                tree_frame.grid(row=0, column=0, rowspan=2, sticky="NWES")

                # --- Create a grid for frame-frame ---
                for row in np.arange(10):
                    tree_frame.rowconfigure(row, weight=1)
                    tree_frame.columnconfigure(row, weight=1)

                self.new_pack = NewTab(tree_frame, self.db_conn, self.theCursor, header=["Product Name", "Weight", "Brand", "Name", "Category"], result0=result, treeoption="browse")
                self.nb.select(self.new_tab)

                # --- Create buttons ---
                bttn_frame = ttk.Frame(self.new_tab)
                bttn_frame.grid(row=0, column=1)
                bttn_add_item = ttk.Button(bttn_frame, text="Add new items", command=self.add_items)
                bttn_add_item.pack()
                bttn_remove_item = ttk.Button(bttn_frame, text="Remove item", command=self.remove_item)
                bttn_remove_item.pack()
                bttn_save_pack = ttk.Button(bttn_frame, text="Save pack", command=self.save_pack)
                bttn_save_pack.pack()
                bttn_exit_pack = ttk.Button(bttn_frame, text="Exit pack",
                                            command=self.quit_rutine)  # Should trigger messagebox, if not saved!
                bttn_exit_pack.pack()

                # --- Entry for pack-name ---
                entr_pack_name = ttk.Entry(bttn_frame)
                entr_pack_name.pack()
                bttn_get_name = ttk.Button(bttn_frame, text="Update pack-name",
                                           command=lambda: self.update_name(entr_pack_name))
                bttn_get_name.pack()

                # Variable to keep track if current pack is saved
                is_pack_saved = False

                # Add to the tablist-dict [tab-object, is_pack_saved, NewTab-obj]
                self.tablist[self.nb.index("current")] = [self.new_tab, is_pack_saved, self.new_pack]
            except AttributeError:
                pass
        except:
            messagebox.showinfo(title="No Packs exist yet", message="You have not created any packs yet.")

    def create_new_pack(self, event=None):
        """Open a new tab in the notebook-widget and populate it with a tree and buttons."""
        self.new_tab = ttk.Frame(self.nb)
        self.new_tab.pack(fill=BOTH, expand=True)

        # Create a grid for frame-frame
        for row in np.arange(2):
            self.new_tab.rowconfigure(row, weight=1)
            self.new_tab.columnconfigure(row, weight=1)

        try:
            self.nb.add(self.new_tab)
            tree_frame = ttk.Frame(self.new_tab)
            tree_frame.grid(row=0, column=0, rowspan=2, sticky="NWES")

            # Create a grid for frame-frame
            for row in np.arange(10):
                tree_frame.rowconfigure(row, weight=1)
                tree_frame.columnconfigure(row, weight=1)

            self.new_pack = NewTab(master=tree_frame, db_conn=self.db_conn, theCursor=self.theCursor, header=["Product Name", "Weight", "Brand", "Name", "Category"])
            self.nb.select(self.new_tab)

            # --- Create buttons --- Needed, if we have a buttonArea-obj?
            bttn_frame = ttk.Frame(self.new_tab)
            bttn_frame.grid(row=0, column=1)
            bttn_add_item = ttk.Button(bttn_frame, text="Add new items", command=self.add_items)
            bttn_add_item.pack()
            bttn_remove_item = ttk.Button(bttn_frame, text="Remove item")
            bttn_remove_item.pack()
            bttn_save_pack = ttk.Button(bttn_frame, text="Save pack", command=self.save_pack)
            bttn_save_pack.pack()
            bttn_exit_pack = ttk.Button(bttn_frame, text="Exit pack", command=self.quit_rutine)  # Should trigger messagebox, if not saved!
            bttn_exit_pack.pack()

            # --- Entry for pack-name ---
            entr_pack_name = ttk.Entry(bttn_frame)
            entr_pack_name.pack()
            bttn_get_name = ttk.Button(bttn_frame, text="Update pack-name", command=lambda:self.update_name(entr_pack_name))
            bttn_get_name.pack()

            # new_pack_name = popupWindow(self.new_tab)
            self.nb.tab(self.nb.index("current"), text=self.default_pack_name) # new_pack_name.value

            # Variable to keep track if current pack is saved
            is_pack_saved = False

            # Add to the tablist-dict [tab-object, is_pack_saved, NewTab-obj]

            self.tablist[self.nb.index("current")] = [self.new_tab, is_pack_saved, self.new_pack]
        except AttributeError:
            pass

    def update_name(self, entr_pack_name):
        """Update the name of a pack, both in the GUI and in the DB"""

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

        # print(result)

        for i in result:
            self.db_conn.execute("UPDATE ItemPack SET PackName= :PackName", {"PackName": new_pack_name})
            self.db_conn.commit()

    def save_pack(self):
        """ Routine for saving packs to the DB.
            1. check all items in TREEVIEW
            2. if item is new => add to db
            3. if item exists in db for this pack => do nothing
        """

        curr_pack_name = self.nb.tab(self.nb.select(), "text")

        result = self.theCursor.execute("SELECT PackName FROM PackTravel")
        in_table = result.fetchall()
        to_check = [n[0] for n in in_table]  # list of all Packs

        if curr_pack_name in to_check:  # Check if current pack is in list of allready saved packs
            answer = messagebox.showwarning("", " "+curr_pack_name+" already exists! Do you want to override it? \n If no, please edit the pack-name and press save again.", type="yesno")
            if answer == "yes":

                # In this case, we need to UPDATE the database where it is needed. That means, overwriting the values for
                # product names that were previously associated with another pack with the current packname

                # Get the data from the ItemPack-table (that is the table connecting items with packs)

                # Get all Products from DB that belong to the Current pack
                result = self.theCursor.execute("SELECT ProductName FROM ItemPack WHERE PackName=" + "'" + curr_pack_name + "'" + ";")
                in_DB_table = result.fetchall()

                # Set the is_saved-variable for this tab to True, thereby indicating that this tab is saved
                # is_saved MUST BE UPDATED the same way as self.tablist!!!!!!!!!!!
                self.tablist[self.nb.index("current")][1] = True

                curr_items = self.new_pack.tree.get_children()  # The items that are in the treeview

                reess = self.theCursor.execute("select count(1) from Items where ProductName = 'Hiking pants';")
                in_DB = reess.fetchone()[0]

                for item in curr_items:
                    curr_item_value = self.new_pack.tree.item(item)['values']  # values of looped through items from tree
                    if curr_item_value in in_DB_table:
                        self.db_conn.execute("UPDATE ItemPack SET ProductName= :ProductName WHERE PackName= :PackName",
                                             {"ProductName": curr_item_value[0], "PackName": curr_pack_name})
                        self.db_conn.commit()
                        pass
                    elif (curr_item_value[0], curr_pack_name) not in in_DB_table:
                        self.db_conn.execute("INSERT INTO ItemPack (ProductName, PackName) VALUES (?, ?)",
                                             (curr_item_value[0], curr_pack_name))
                        self.db_conn.commit()

                # self.db_conn.execute("UPDATE PackTravel SET PackName= :PackName", {"PackName": curr_pack_name})
                # self.db_conn.commit()

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

            self.db_conn.execute("INSERT INTO PackTravel (PackName) VALUES (?)", (curr_pack_name, ))
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
                    self.tablist[key-1] = self.tablist[key]
                    del self.tablist[key]
                elif key == curr_pack_id:
                    curr_pack, a, b  = self.tablist[self.nb.index("current")]
                    del self.tablist[key]
                    curr_pack.destroy()

        if self.tablist[self.nb.index("current")][1] == True:  # self.is_saved[self.nb.index("current")] == True:
            update_tabs()
        else:
            answer = messagebox.askyesno("Save?", "Do you want to cancel without saving?")
            if answer == True:  # Answered "Yes" to "Do you want to cancel without saving?"
                update_tabs()
            elif answer == False:  # Answered "No" to "Do you want to cancel without saving?"
                curr_pack, a, b  = self.tablist[self.nb.index("current")]
                self.save_pack()
                # MAYBE DO NOTHING, and let the user press save?

    def remove_item(self):
        self.tablist[self.nb.index("current")][1] = False
        curr_tab_obj = self.tablist[self.nb.index("current")][2] # curr_tab_obj is the currently selected Newtab-object
        curr_tab_obj.remove_from_tree()

    def add_items(self):
        """Open a window containing all items in the inventory, with add buttons"""
        curr_pack = self.tablist[self.nb.index("current")][2]     # Is the current NewTab-object that we work with
        curr_new_tab = self.tablist[self.nb.index("current")][0]  # Is the current tab in the notebook
        # self.data is the all the items stored in the db
        # self.items_table is the name of the table in the db, where all items are stored
        self.tablist[self.nb.index("current")][1] = False  # We have now added items, thus is_saved is False

        # self.tablist[self.nb.index("current")] Get the current tab and update WEIGHT!

        add_items_win = ChoiceInventory(curr_new_tab, self.data, self.db_conn, self.theCursor, self.items_table, curr_pack)

    def setup_db(self):
        """Open the database with all stored items and pass along all data """

        # Open DB (Created in external file: Db_setup.db
        db_conn = sqlite3.connect('HikeDB.db')

        # Create Cursor
        theCursor = db_conn.cursor()

        # Table to use:
        table = "Items"

        # Headings to use in TREEVIEW:
        PName = "ProductName"
        Weight = "Weight"
        Brand = "Brand"
        Name = "Name"
        Category = "Category"
        Comment = ""

        # data stored in db
        data = theCursor.execute("SELECT ID, " + PName + ", " + Weight + ", " + Brand + ", " + Name +
                                 ", " + Category + " FROM " + table)

        theCursor = db_conn.cursor()

        return data.fetchall(), theCursor, db_conn

    def get_open_pack(self, pack_to_load):
        self.pack_to_load = pack_to_load

    @property  # ???
    def default_pack_name(self):
        """initialises with self.deafult_pack_no = "00" and then updates with 1 for each
        new pack that is created, e.g. first new pack that is created gets the
        pack_no = "01", the next pack gets "02" and so on."""

        if int(self.default_pack_no)+1 > 10:
            self.default_pack_no = str(int(self.default_pack_no)+1)
        else:
            self.default_pack_no = "0"+str(int(self.default_pack_no)+1)

        return "pack" + self.default_pack_no

# Main window
class Inventory:
    """An object for displaying the inventory"""

    # --- Class Variables ---
    # if change for all instances use Inventory.[classVar] = something
    # change for one instance, use [instance name].[class var] = something

    # SQL-variables
    curr_item = 0
    theCursor = 0
    db_conn = 0

    def __init__(self, root, data, theCursor, db_conn):
        # Initialise frames for widgets

        self.root = root

        tree_frame = ttk.Frame(root)
        note_frame = ttk.LabelFrame(root, text="Comment Area")
        bttn_frame = Frame(root)

        tree_frame.grid(row=0, column=0, rowspan=2, columnspan = 2, sticky="NWES")
        note_frame.grid(row=1, column=2, sticky="NSWE", pady=10, padx=10)
        bttn_frame.grid(row=0, column=2, sticky="NSWE", pady=10, padx=10)

        # Create a grid for frame-frame
        for row in np.arange(10):
            tree_frame.rowconfigure(row, weight=1)
            tree_frame.columnconfigure(row, weight=1)

        # Create a grid for root
        for row in np.arange(2):
            root.rowconfigure(row, weight=1)
            root.columnconfigure(row, weight=1)

        test_lb = Label(note_frame, text="test")
        test_lb.pack()

        # Initialise an area for comments
        scrollbar = Scrollbar(note_frame)
        self.text_area = Text(note_frame, yscrollcommand=scrollbar.set, padx=10, pady=10, height=15, width=25)

        scrollbar.config(command=self.text_area.yview)
        scrollbar.pack(side="right", fill="y")
        self.text_area.pack()

        # Setup the db and retrive the stored data
        # result = self.setup_db()

        # Make better
        header = ["Product Name", "Weight", "Brand", "Name", "Category"]

        # Create an ITEMS-obect (ie. the list with all items)
        self.items = ItemList(tree_frame, data, header, db_conn)

        # Buttons for adding and removing items in Inventory
        self.bttn_add_item = ttk.Button(bttn_frame, text="Add Item", command=self.create_add_to_tree_window)
        self.bttn_remove_item = ttk.Button(bttn_frame, text="Remove Item", command=self.items.remove_from_tree)
        self.bttn_edit_item = ttk.Button(bttn_frame, text="Edit Item", command=self.create_edit_item_window)

        self.bttn_add_item.pack(side="left")
        self.bttn_remove_item.pack(side="left")
        self.bttn_edit_item.pack(side="left")

    def edit_tree(self):
        data = self.edit_item_win.get_entries()  # get the values from the entry-boxes in ChildWindowEdit-obj

        if data is not None:
            # print(data)
            id = self.items.tree.item(self.items.tree.selection())['values'][5]
            data.append(id)
            # print(data)
            self.items.tree_edit_line(data)  # pass the data to the ItemList-obj and invoke method to change the data in the TREEVIEW

    def create_add_to_tree_window(self):
        self.new_item_win = ChildWindow(self.root, self, self.items)
        # print(self.items)
        self.bttn_remove_item["state"] = DISABLED  # Makes bttn_remove_item unclickable

    def create_edit_item_window(self):
        data = self.items.get_line_data()
        self.edit_item_win = ChildWindowEdit(root, self, self.items, data)

    def setup_db(self):
        # Open DB (Created in external file: Db_setup.db
        self.db_conn = sqlite3.connect('HikeDB.db')

        # Create Cursor
        self.theCursor = self.db_conn.cursor()

        # Table to use:
        table = "Items"

        # Headings to use in TREEVIEW:
        PName = "ProductName"
        Weight = "Weight"
        Brand = "Brand"
        Name = "Name"
        Category = "Category"
        Comment = ""

        return self.theCursor.execute("SELECT ID, " + PName + ", " + Weight + ", " + Brand + ", " + Name +
                                      ", " + Category + " FROM " + table)

    def printdb(self):
        try:
            result = self.theCursor.execute(
                "SELECT ID, ProductName, Weight, Brand, Name, Category, Comment FROM  Items")

            for row in result:
                print("ID :", row[0])
                print("ProductName :", row[1])
                print("Weight :", row[2])
                print("Brand: ", row[3])
                print("Name: ", row[4])
                print("Category: ", row[5])
                print("Comment: ", row[6])
        except sqlite3.OperationalError:
            print("Could not retrieve data..")

    def update_comment(self):
        pass


# ---------- Start the application ----------

root = Tk()
Inv = Main(root)
root.mainloop()

# mii