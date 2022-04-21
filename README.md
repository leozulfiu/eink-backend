# E-Ink Home Dashboard Backend

A dashboard consisting of an e-ink display showing the weather forecast for the next six days, 
the next garbage collection dates and some upcoming birthdays.

- The forecast is fetched from the [SRGSSR weather API](https://developer.srgssr.ch/apis/srf-weather)
- The garbage collection dates are extracted from an ics file which can be 
downloaded from the Stadt Zürich [recycling page](https://www.stadt-zuerich.ch/ted/de/index/entsorgung_recycling/entsorgen/persoenlicher_entsorgungskalender.html)
- The upcoming birthdays of my friends are stored in a sqlite database and can be managed by a simple frontend

## Todo

1. Make managing the birthdays a bit simpler via some nice interface

## How to build the docker image

Use the following command in the root project folder: `docker build -t eink-backend-image .`

## How to run the docker image

1. Create a folder in the home directory called `e-ink-backend`
2. Create a file `prod.env` within that directory to define the necessary environment variables. Copy the following content to it
and change the necessary variables.
```
SRGSSR_CLIENT_ID='client_id'
SRGSSR_CLIENT_SECRET='client_secret'
MOCK_FILE_NAME='data/mock_filename.json'
DATABASE_FILE_NAME='data/birthdays.db'
CALENDAR_FILE_NAME='data/calendar.ics'
DB_SECRET='12345678'
```
The mock env variable can be removed if the real API should be used.
A secret can be created with the following snippet: 

`dd if=/dev/urandom bs=32 count=1 2>/dev/null | openssl base64`

or

`python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key())"`
3. Get the ics calendar and save it in a new directory called `data` within the `e-ink-backend` directory.
Register the path to the calendar file as follows: `data/calendar.ics`
5. Start the container and pass the created file as an argument:
```
docker run -d --env-file ./prod.env --name eink-backend -v /data/folder/on/host:/app/data -p 9000:80 eink-backend-image
```

## What I learned

- The date of birth and name are according the GDPR regulations personal data and should be encrypted.
When using an encryption method including a salt, I noticed an id was indispensable to use, since I'm not able
to identify the relevant records when updating something.
- The value of 'build-once-deploy-everywhere': During the **deployment** it is the only time when environment
specific configurations should be made, since at that time I know to which environment I'm going to deploy.
The only downside which comes to my mind is, that the image contains possibly unnecessary things such as mock data.

## References
- https://dev.to/dev1721/do-you-wanna-keep-your-embedded-database-encrypted-5egk
- https://fastapi.tiangolo.com/deployment/docker/
