# Almapi
A RESTful API for the menus on alma.be written in python.

## Endpoints
### Get information about all the available alma's
```
/almas
```
**Example Output**
```
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
```
{
    "id": 1, 
    "name": "Gasthuisberg"
}
```
### Get the menu of a specific alma
```
/almas/:id/menu
/almas/:id/menu/:week
/almas/:id/menu/:week/:year
```
**Example Output**
```
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
