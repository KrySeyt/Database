# Task (with part of requirements)
*this is my assignment for university practice in the 2nd year*

Develop a program for working with the database "Employees of the Research Institute", which includes the following information: department
No., service number, last name, first name, patronymic, employee topic No., duration of work in months, position in the company ID,
titles, salary, etc. Develop a user-friendly interface and organize the creation, deleting, searching and updating database records.

Find the longest-lasting job, the highest-paid employee, the distribution of employees by topics, titles, etc. \
Create a graphical interpretation of the result using graphs, pie charts and histograms.

Find out the growth of employees with a certain title by year and make a forecast about their number for the next two years

# Requirements, architecture, database schema
You can find it in `/docs/`

# Run

## Run app with local backend

- Clone repo
```shell
git clone https://github.com/KrySeyt/StatisticsAndAnalysis.git
```

- Go to repo dir
```shell
cd StatisticsAndAnalysis
```

- Run app 
```shell
docker compose -f run-locally.yml up -d
```
In this case backend will be launched at the first app run

OR

- If you wanna shutdown backend on exit from app:
```shell
docker-compose -f run-locally.yml up --abort-on-container-exit
```