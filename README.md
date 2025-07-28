# Theatre Api

Api service for theatre management written on DRF   


# Installing using GitGub

Install PostgresSQL and create db
``` 
1. git clone https://github.com/MykytaKop/Theatre.git
2. cd Theatre
3. python - venv venv
4. For wondows: surce venv\Scripts\activate
   For macOS: source venv/bin/activate
5. pip install -r requirements.txt
6. set DB_HOST=<your db hostname>
7. set DB_NAME=<your db name>
8. set DB_USER=<your db username>
9. set DB_PASSWORD=<your db user password>
10. set SECRET_KEY=<your secret key>
11. python manage.py migrate
12. python manage.py runserver
```

# Run with docker

Docker should be installed

```
docker-compose build
docker-compose up
```

# Getting access:

- create user via /api/user/register/
- get access token /api/user/token/


# Features:
- JWT authenticated
- Admin panel /admin/
- Documentation is located at api/schema/swagger-ui/ or api/schema/redoc/
- Managing orders and tickets
- Creating plays with genres, actors
- Creating theatre halls
- Adding performances
- Filtering plays and performances
