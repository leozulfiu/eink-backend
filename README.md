# E-Ink Home Dashboard Backend

A dashboard consisting of an e-ink display showing the weather forecast for the next six days, 
the next garbage collection dates and some upcoming birthdays.

- The forecast is fetched from the [SRGSSR weather API](https://developer.srgssr.ch/apis/srf-weather)
- The garbage collection dates are extracted from an ics file which can be 
downloaded from the Stadt Zürich [recycling page](https://www.stadt-zuerich.ch/ted/de/index/entsorgung_recycling/entsorgen/persoenlicher_entsorgungskalender.html)
- The upcoming birthdays of my friends are stored in a sqlite database and can be managed by a simple frontend

## How to run locally

1. *(optional)* Create a virtual environment and activate it
2. Install all necessary requirements with pip: `pip install -r requirements.txt` 
3. Copy the .env_example file and paste it at the same location with the name `.env`
4. Start the main script within the `app` folder
5. Install all dependencies in the frontend folder via `npm install`
6. Start the frontend dev server via `npm run start`
7. Navigate to `http://localhost:3000`

## How to build the docker image

Use the following command in the root project folder: `docker build -t eink-backend-image .`

If the image should run on an arm64 host, use the following command: 
`docker buildx build --platform linux/arm64 -t eink-backend-image .`

## Export image as tar archive and import it onto another host

1. Export image as file: `docker save --output eink-backend-image.tar eink-backend-image`
2. Copy image to another host via `cp` or `scp`
3. Load image on the other host: `docker load -i <path to image tar file>`

Or everything in one command: `docker save eink-backend-image | bzip2 | pv | ssh user@host docker load`.
Note that this command doesn't work well when a password is required. Follow [this](https://linuxize.com/post/how-to-setup-passwordless-ssh-login/) guide to allow
ssh password free login.

## How to run the docker image in production

1. Create a directory on the host called `e-ink-backend`
2. Create a file `prod.env` within that directory to define the necessary environment variables. Copy the following content to it
and change the necessary variables.
```
SRGSSR_CLIENT_ID='client_id'
SRGSSR_CLIENT_SECRET='client_secret'
#MOCK_FILE_NAME='data/mock_filename.json'
DATABASE_FILE_NAME='data/birthdays.db'
CALENDAR_FILE_NAME='data/calendar.ics'
BOT_PASSWORD: 'some_secret'
ROOM_ID: 'some_room_id'
DB_SECRET='12345678'
```
The mock env variable can be completely removed if the real API should be used.
A secret can be created with the following snippet: 

`dd if=/dev/urandom bs=32 count=1 2>/dev/null | openssl base64`

or 

`python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key())"`

or

[by generating new fernet keys online](https://fernetkeygen.com/)

**Keep the secret somewhere safe!**

3. Get the ics calendar and save it in a new directory called `data` within the `e-ink-backend` directory.
Register the path to the calendar file as follows: `data/calendar.ics`

4. The folder structure should look as follows
```
.
├── data
│   └── calendar.ics
└── prod.env
```
6. Start the container and pass the created file as an argument:
```
docker run -d --env-file ./prod.env --name eink-backend -v /host/custom/dir/e-ink-backend/data:/data -p 9000:80 eink-backend-image
```

alternatively the required environment variables can be set one by one:
```
docker run -d --env DATABASE_FILE_NAME='data/birthdays.db' --env CALENDAR_FILE_NAME='data/calendar.ics' --name eink-backend -v /host/custom/dir/e-ink-backend/data:/data -p 9000:80 eink-backend-image
```

### Alternatively use docker-compose

Instead of the run command method above, a docker compose file can be used to start the service.
This has the advantage that no parameters have to be defined when starting up the container and thus increases the reproducibility.

1. Create a docker-compose.yml file within the `e-ink-backend` folder.
2. Copy the content of the projects docker-compose file to the newly created file
3. Change and extend the environment variables according to the doc above
4. Create a data folder and copy the necessary files (calendar at minimum and the mock response) to it
5. Execute `docker-compose up -d` to start the service with all configured parameters within the file

Note that since this is an image which does not exist on docker hub, it must be created manually beforehand.

## What I learned

- The date of birth and name are according the GDPR regulations personal data and should be encrypted.
When using an encryption method including a salt, I noticed an id was indispensable to use, since I'm not able
to identify the relevant records when updating a record.
- The value of 'build-once-deploy-everywhere': During the **deployment** it is the only time when environment
specific configurations should be made, since at that time I know to which environment I'm going to deploy.
The only downside which comes to my mind is, that the image contains possibly unnecessary things such as mock data.
But that can be mitigated by separating the application code and mock code in two clear applications.
- Docker images are built for specific CPU architectures. Running an image on an ARM host which was built by an
x86 machine won't work. Furthermore, it can happen that even some dependencies won't work for the target architecture
(example: cryptography).

## References
- https://dev.to/dev1721/do-you-wanna-keep-your-embedded-database-encrypted-5egk
- https://fastapi.tiangolo.com/deployment/docker/
