# Twitter-like API project

---

 
 ## Technologies

---
 Python | Django | DRF | Postgres | JWT auth middleware | Celery | RabbitMQ | PyTest | Docker 

 ## SUMMARY

---
 This API is created in educational purpose. Here i tried to reproduce the functionality of of Twitter app.


 ## API Schema

---

- **API defaults**:
    - GET `..api/v1/` - root
    - POST `../admin/` - enter the django admin panel
    - GET `../schema/` - API docs (Swagger)
___
 - **User endpoint:**
    - **GET** `../api/v1/user/`   - list all users (staff only)
    - **POST** `../api/v1/user/` - register new user
    - **POST** `../api/v1/user/login/` - authorization (JWT obtain)
    - **GET** `../api/v1/user/{user_id}/` - get user detailed view (owner or staff)
    - **PUT** `../api/v1/user/{user_id}/` - change user's info (owner or staff)
    - **PATCH** `../api/v1/user/{user_id}/` - change user's info (owner or staff)
    - **DELETE** `../api/v1/user/{user_id}/` - delete user's profile (owner or staff)
___
 - **Pages endpoint:**
    - **GET** `../api/v1/pages/` - list all pages
    - **POST** `../api/v1/pages/` - make a new page
    - **GET** `../api/v1/pages/{id}/` - detailed view on the page
    - **PUT** `../api/v1/pages/{id}/` - change page details
    - **PATCH** `../api/v1/pages/{id}/` - change page details
    - **DELETE** `../api/v1/pages/{id}/` - delete page
    - **PATCH** `../api/v1/pages/{id}/approve-request/` - approve subscribe request for page
    - **GET** `../api/v1/pages/{id}/follow-requests/` - list all subscribe requests for page
    - **GET** `../api/v1/pages/{id}/follow/` -follow (subscribe for) the page
    - **PATCH**`../api/v1/pages/{id}/followers-remove/` - remove the followers
    - **GET** `../api/v1/pages/{id}/followers/` - list all page subscribers
 ___
 - **Posts endpoint:**
    - **GET** `../api/v1/pages/{id}/posts/` - list all posts of the page
    - **POST** `../api/v1/pages/{id}/posts/` - make a new post on the page
    - **GET** `../api/v1/pages/{id}/posts/{id}/` - get the post
    - **PUT** `../api/v1/pages/{id}/posts/{id}/` - change the post
    - **PATCH** `../api/v1/pages/{id}/posts/{id}/` - change the post
    - **DELETE** `../api/v1/pages/{id}/posts/{id}/` - delete the post
    - **GET** `../api/v1/pages/{id}/posts/{id}/like-post-toggle/` - like/unlike the post
    - **GET** `../api/v1/pages/{id}/posts/{id}/replies/` - see the post's replies (thread)
 ___
 - **Feed endpoint:**
    - **GET** `../api/v1/feed/` - list all posts from the followed pages
    - **GET** `../api/v1/feed/{id}/` - get particular post from the followed pages
    
## Quickstart:
- git clone the project
 
      gh repo clone sheirand/Twitter-like-API
      
- or
    
      git clone https://github.com/sheirand/Twitter-like-API

- add everything needed to the .env file
- enter bash command inside project directory

      docker-compose up

- project is now available at yours  http://localhost:8000/

- API schema http://localhost:8000/schema/

- if you want to ensure that everything works fine - run tests:

      docker-compose exec web pytest
 
- if you want to create a superuser:
 
      docker-compose exec web python manage.py createsuperuser


## Closer look on project features
___

- PostgreSQL is used as database for:
  - user model
  - page model
  - post model
- RabbitMQ is used as message broker for Celery
- Application is async connected to the StatsMicroservice app for collecting stats (my other project) 
- Celery is used for async collecting daily stats and sending it to the StatsMicroservice 
- Flower is added to project for managing Celery tasks
- Custom User model and manager
- Authentication and authorization through JWT middleware (token in headers)
- Permissions
- Filtering is available through query params
- Pytest is used for testing (+fixtures in ./tests/conftest.py)
- Project is fully dockerized and can be up with one command
- Entrypoints for docker-compose instances
- Custom models admin panel 
- All sensitive info moved to .env file
- Codestyle: pep8, isort for imports
- OpenAPI schema (Swagger) is automatically generated with drf-yasg tool

## Contact info

___
Contact me via [email](mailto:eugene.osakovich@gmail.com) 
