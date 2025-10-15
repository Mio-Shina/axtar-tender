# axtar-tender
A web application for searching tender information in a database.

This project automates data collection from the website etender.gov.az and stores it in a MySQL database. Users can search the collected data via a simple web interface.

## Main Features

- **Data Collection:** Automatically gathers tender information from the website and saves it to the MySQL database.  
- **Data Update:** The index page includes an "Yeniləyin" button, which re-collects new tender data and adds it to the database.
- **Data Auto-Update:** The index page includes auto-update, which re-collects new tender data and adds it to the database during time. 
- **Data Search:** Users can search the database using a form on the index page. Search results are displayed in a table on the `search_results.html` page with all relevant information.
