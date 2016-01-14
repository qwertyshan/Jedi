# MapMove: Where is the Jedi? 

MapMove is a web app that lets you put a Star Wars character anywhere on the world map. You can select one of 12 characters and enter a location in free-text. The app does a geo-location lookup for your specified location and places your selected character at that location on the map.

**Live URL: http://shanrao-mapmove.appspot.com**

**Technology Stack**
* Frontend
  * Bootstrap
* Backend Application
  * Python
  * Jinja
* APIs and Services
  * Google Maps Geocoding API
  * Google Maps Javascript API
* Compute
  * Google App Engine
* Datastore
  * NDB (non-SQL)

![MapMove](/doc/MapMove_Initial.png)

## Beautiful Frontend

All views are beautifully designed using Bootstrap based CSS. Feedback and application errors are elegantly presented using Javascript handlers.

![MapMove](/doc/MapMove_Selection.png)

## Python Backend

The app is written in Python. Jinja enables frontend templating. Google Map APIs are used to get geo-location information.

![MapMove](/doc/MapMove_History.png)

## Massively Scalable Compute and Datastore

The application is built on Google App Engine, with features such as auto-scaling, caching, and sophisticated management dashboards. 

The datastore uses NDB, a schemaless object datastore providing robust, scalable storage.

![MapMove](/doc/MapMove_GAE.png)

