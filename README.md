# E-Ink Home Dashboard Backend

A dashboard consisting of an e-ink display showing the weather forecast for the next six days, 
the next garbage collection dates and some upcoming birthdays.

- The forecast is fetched from the [SRGSSR weather API](https://developer.srgssr.ch/apis/srf-weather)
- The garbage collection dates are extracted from an ics file which can be 
downloaded from the Stadt Zürich [recycling page](https://www.stadt-zuerich.ch/ted/de/index/entsorgung_recycling/entsorgen/persoenlicher_entsorgungskalender.html)
- The upcoming birthdays of my friends are stored in a sqlite database and can be managed by a simple frontend

## Todo

1. Containerize application
2. Make ics file mountable
3. Make managing the birthdays a bit simpler via a server side rendered page

## How to run the docker image

Multiple variables must be set when starting the container.
```
CLIENT_ID = '1234'
CLIENT_SECRET = '1234'
DB_SECRET = '1234='
ENVIRONMENT = 'local'
```
The environment variable can be set to `local` or `production`.
These vars can be either set as unix env variables or passed as arguments when starting the container.

## What I learned

- The date of birth and name are according the GDPR regulations personal data and should be encrypted.
When using an encryption method including a salt, I noticed an id was indispensable to use, since I'm not able
to identify the relevant records when updating something.
- The value of 'build-once-deploy-everywhere': During the **deployment** it is the only time when environment
specific configurations should be made, since at that time I know to which environment I'm going to deploy.
The only downside which comes to my mind is, that the image contains possibly unnecessary things such as mock data.