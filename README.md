# Formula 1 stats

- To install the needed dependencies, please run:
    - pip install -r requirements.txt

- To launch the project, the file main.py (in the api folder) should be executed as normal python script with the command:
    - python main.py 
    that will run the project in the developemnet server on http://127.0.0.1:5000

- To test the api endpoints, you can visit the following url:
    - http://127.0.0.1:5000/apidocs 
    that will open a swagger dashboard with all the available endpoints. Within this page it's possible to make requests to the endpoints and see the results. It is also possibile to see the documentation of each endpoint with the parameters and the return values. Another possibility is to use a tool like Postman to send requests to the endpoints that have the provided url as base.

- The api folder contains also a file called unit_tests.py that contains some unit tests for the api endpoints. You can run them using the following command:
    - python unit_tests.py