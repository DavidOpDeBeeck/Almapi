
**Due to changes to alma.be this scraper does not work anymore!**

# Almapi
A RESTful API for the menus on alma.be written in python.

## Web Scraper
```sh
crontab -e
```
```sh
* 23 * * * python /path/to/script/scraper.py
```
Add the `clean` argument to reset the database.
## Web API
```sh
python /path/to/script/web.py
```
The web API will by default listen on all public IP addresses.
```python
app.run(host='0.0.0.0')
```
## Endpoints
### Get information about all the available alma's
```
/almas
```
**Example Output**
```json
[
    {
        "id": 1, 
        "name": "Gasthuisberg"
    }, 
    {
        "id": 2, 
        "name": "Pauscollege"
    }, ...
]
```
### Get information about a specific alma
```
/almas/:id
```
**Example Output**
```json
{
    "id": 1, 
    "name": "Gasthuisberg"
}
```
### Get the week menu of a specific alma
```
/almas/:id/menu
/almas/:id/menu/:week
/almas/:id/menu/:week/:year
```
**Example Output**
```json
[
    {
        "date": "2015-09-14",
        "menu": {
            "Soup": [
                {
                    "name": "Bloemkoolroomsoep",
                    "price": 2.4,
                    "vegetarian": 1
                }, ...
            ],
            "Main Course": [
                {
                    "name": "Kalkoensteak met boontjes",
                    "price": 3.2,
                    "vegetarian": 0
                }, ...
            ]
        }
    }, ...
]
```
### Test endpoints
* [almapi.davidopdebeeck.be/almas](http://almapi.davidopdebeeck.be/almas)
* [almapi.davidopdebeeck.be/almas/1](http://almapi.davidopdebeeck.be/almas/1)
* [almapi.davidopdebeeck.be/almas/1/menu](http://almapi.davidopdebeeck.be/almas/1/menu)
* [almapi.davidopdebeeck.be/almas/1/menu/39](http://almapi.davidopdebeeck.be/almas/1/menu/39)
* [almapi.davidopdebeeck.be/almas/1/menu/39/2015](http://almapi.davidopdebeeck.be/almas/1/menu/39/2015)
