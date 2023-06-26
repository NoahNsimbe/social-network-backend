# Social network API

A simple REST API based social network in Django where Users can sign up and create text posts, as well as view, like, and unlike other Users’ posts.

## Functional requirements

● on signup, validate email formatting and only allow signups with valid emails
● once signed up, enrich the User with geolocation data of the IP that the signup originated from
● based on geolocation of the IP, check if the signup date coincides with a holiday in the User’s country, and save that info

## Technical requirements

● use JWT for user authentication
● data enrichment must be performed asynchronously, i.e. independently of the signup route API request processing
● API endpoints functionality must be suitably covered with tests
● use django-rest-framework library for API
● implement retries for requests towards 3rd party API

Except for Django and DRF, the candidate is free to choose the rest of the solution stack (libraries, databases, etc.). Design of the API and data model is up to the candidate, with at least the following API endpoints:
● user signup
● user login
● get user data
● post CRUD
● post like/unlike

## Notes

● the candidate can decide on how to organize and write tests (framework, coverage, and similar), but must provide instructions for running tests in readme (ideally set up as a CI pipeline)
● the candidate is free to use any publicly available API for the email, geolocation, and holiday purposes, we recommend Abstractapi (<https://www.abstractapi.com/>)
● the solution must be submitted via a git repository url
● the visual aspect of the project is not relevant - clean and usable REST API is the point of this task
● the project is not defined in detail, the candidate should use their best judgment for every non-specified requirements (including chosen tech, third party apps, etc), as long as they explain their choices - ideally in a readme as it will allow for an easier review
