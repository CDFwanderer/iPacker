# **pyKer**
This is my humble little pack manager for hikers, or basically any traveller. My aim is to create a GUI, from which the user can manage their packs in a quick and easy way that hopefully will save them work and keep them from forgetting stuff. Hope you enjoy!

*This project is mainly intended for my own learning, so please be gentle with any misstakes or bad coding structure :)*

Currently, my aim is to create a local app with the following properties:
* Manage an inventory with all your items
* Create, store and edit packs, based on your inventory

The project is, at the moment based on an sqlite3-database for storing the data, with tree tables:

Items | Item Pack | PackTravel
------------ | ------------- | -------------
Table containing all<br/>items in the inentory | Table connecting a<br/>specific pack with items | Table connecting a<br/>specific travel to a pack

## Long-term ideas
* Tags for packs, e.g. #winter or #summmer
* Excel-integration
* Ability to print a checklist
* Ability to score different items/packs
* Different types of wights
* Convert to .exe, so as to be able to run the app without using python
