# Jizzed

Run SQL queries and censor their output

## Files
```
.
├── Dockerfile
├── README.md
├── app.py
├── docker-compose.yml
├── requirements.txt
└── templates
    ├── head.html
    ├── index.html
    └── result.html
```

## Build and run
`docker-compose build && docker-compose up`

Open localhost:5003


## Limitations
* Can currently only process most basic queries like below
`SELECT * FROM Persons;`
`SELECT FirstName, LastName FROM Persons WHERE FirstName = 'John';`
