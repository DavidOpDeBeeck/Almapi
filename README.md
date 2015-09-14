# Almapi
A RESTful API for the menus on alma.be written in python.

## Endpoints
### 1
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
### 2
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
### 3
```
/almas/:id/menu/:week
/almas/:id/menu/:week/:year
```
**Example Output**
```
{
    "2015-09-14": {
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
    }, ...
}
```
