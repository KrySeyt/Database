<hr>

# Functional requirements

### I/O:
- Simple desktop GUI with any usable appearance for simple users
- (OPTIONAL) simplest web GUI with any appearance sufficient for work for simple users
- Show *Statistics* results in graphs, pie charts and histograms
- All I/O only with simple users and through desktop GUI and (OPTIONAL) web GUI
- Functions should be grouped by meaning, as in the list above
- All functions should be accessible for users by desktop GUI and (OPTIONAL) web GUI


### Data storage:

- Any long-term data storage

- #### Employee info:
	- Last name, first name, patronymic
	- Department number
	- Service number
	- Number of the topic that the he is working on
	- Duration of work in company in months
	- Code of position in company
	- Titles
	- Salary amount
	- etc


### Functions:
- Storage with company employees, statistics based on employees info in this storage, forecasts by arbitrary algorithm

- #### Storage:
	- Add employee entry
	- Delete employee entry
	- Update employee entry
	- Search for an employee entry by any attribute or combination thereof

- #### Statistics<a name="stats"></a>:
	- Find the longest-lasting job
	- Find the highest-paid employee
	- Find the distribution of employees by topics, titles and any another parameters, directly or indirectly related with employees
	- Find the growth of employees with a certain title by year

- #### Forecasts:
	- Find the growth of employees with a certain title for next two years


### Misc:
- User should be able to access his data storage on any computer with internet and with installed client or (OPTIONAL) even without installation (web client)
- Each user or group of users should have their own data storage, not one for everyone

<hr>

# Non-functional requirements

### Security:
- All user\`s data should be safe by default ways
- Access to user data should requires password
- (OPTIONAL) Network and other connections should be safe


<hr>

##### If there is no requirement for something, then an arbitrary solution that meets the rest of the requirements will do. Just do your best
