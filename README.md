# Web map
Program that tracks locations
This program allows to get geolocations of places where films were made and put it on the map
Finds 10 closest to given places where film of certain year were filmed.

## Requirements
needs pip packages:
- folium 0.12.1.post1
- geopy 2.2.0

## Usage
Program uses standart argparce module from python to get arguments
```bash
>python3 main.py 2012 50.45 30.52 locator1.list
```
 
## Visuals
Uses folium to create map and show 10 closest locations and connects them with lines.

## Examples
![image](https://user-images.githubusercontent.com/92575534/153642018-13973a20-1c70-4e97-a079-c5881f7c9aaf.png)


