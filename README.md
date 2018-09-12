# **pyKer**
This is my humble little pack manager for hikers, or basically any traveller. My aim is to create a GUI, from which the user can manage their packs in a quick and easy way that hopefully will save them work and keep them from forgetting stuff. Hope you enjoy!

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
