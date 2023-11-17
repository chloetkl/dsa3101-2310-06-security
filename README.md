# DSA3101 Project

**Main Document Drive: https://drive.google.com/drive/folders/1SrP-2aTmh3UKO2TkNW3702NcpCmGaqGq?usp=sharing**
- Slides
- Meeting Minutes
- BRD

# NUSecure

The NUSecure project aims to enhance security by optimizing monitoring systems, ensuring the relevance of information, and improving operational efficiency through data science.

## How to Run

1. Make sure Docker is installed on your machine.
2. Build and run the Docker containers: `docker compose up --build`
3. Check Docker Desktop to ensure that the database_pop container has completed running and populated database.
4. Access the application in your browser at `http://localhost:9001`

## Login credentials
Type | Username | Password | Actions
--- | --- | --- | ---
Admin | admin | admin | Add new users
Security team | sec1 | sec1 | View incidents map. Add new incident reports
Analytics team | analytics1 | analytics1 | Generate and view analytics and predictions plots.
 

## API Testing with Postman
1. Make sure Postman installed on your local machine.
2. Download the provided Postman collection file in back/testing
3. Open Postman and click on the Import button.
4. Choose and open provided collection file. This will import the collection into your Postman workspace.
### Running the Tests
Open the collection from the Collections sidebar.
Choose an API request to test and click the Send button.
To run automated tests, go to the Tests tab within each request and click Send.
Review the test results in the bottom panel under the Test Results tab.

## Unit test of functions


