# BigDataClimateChange
A Python-based approach to answer the following question: how have countries' daily temperature ranges changed over time?

### How To Run

The project can be divided into two sections:
- The 

Download and extract all files from [this shapefile download](https://www.arcgis.com/home/item.html?id=fa510018bdd044b08fc64d2a16bc680a) into `/mapdata`.

### THE PLAN
- store file containing bounding box of each country in country matrix
- compute box plots for said country
- compute by year average for each year
- compute by month average for each year
    - spread out days in month
    - be able to pick month