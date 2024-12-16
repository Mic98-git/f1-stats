# Formula 1 stats

- To install the needed dependencies, please run:
    - pip install -r requirements.txt

- To launch the project, the file main.py (in the API folder) should be executed as normal Python script with the command:
    - python main.py
    that will run the project in the development server on http://127.0.0.1:5000

- To test the API endpoints, you can visit the following URL:
    - http://127.0.0.1:5000/apidocs 
    that will open a swagger dashboard with all the available endpoints. Within this page, it's possible to make requests to the endpoints and see the results. It is also possible to see the documentation of each endpoint with the parameters and the return values. Another possibility is using a tool like Postman to send requests to the endpoints with the provided URL as base.

- The API folder also contains a file called unit_tests.py that contains some unit tests for the API endpoints. You can run them using the following command:
    - python unit_tests.py