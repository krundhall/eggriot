Final Project Report
Student(s): Ilir Jusufi – ilir.jusufi@bth.se
Maria Martins – mm@bth.se
1. Project Idea
Here you should discuss your idea. For instance:
For this assignment we have designed and implemented a system to store data about the
COVID vaccination. We have downloaded the data from this source: www.somesource.com
(alternatively you can generate your own data). Our tool enables users to track this data but
also provide various statistics and visualizations of the data. ….
2. Schema Design
Here you present your schema design. You can use softwares such as
https://app.diagrams.net to draw your schema. Explain all the tables/relations and different
connections they have.
3. SQL Queries
Here you present and discuss the most interesting queries. Make sure you have 5 of them at
least and check the specification in the assignment sheet. One example is found below:
Q: List the name, last name and job title of the employee from a given city.
The following query is a multirelation query and uses JOIN. We pass the argument of the city
name (marked with ? in the query) and the query should give us all the employees of the
corresponding shop. We join table Employees on table Shops by matching the Shops.ID to
the foreign key
Employees.shopID
SELECT firstname, lastname, jobtitle
FROM Employees
JOIN Shops ON Employees.shopID = Shops.ID
WHERE city=?;
4. Discussion and Resources
Here you can write anything you might think it is important and provide the link to the
required resources. For example:
We had issues with the missing and inconsistent data. We decided to remove/insert NULLS
in the missing/corrupted attributes/tuples…...
The project uses xyz library, please check readme.txt for installation details.
Source code: [github/... link]
Video demonstration: [youtube/vimeo/... link]
Changelog
Person Task Date
Ilir Setting-up server environment and Git repository 2018-08-20
Ilir Implemented module for loading the data 2018-08-20
Maria Designing and implementing the home-page 2018-08-20
Maria Implementing Ouath authentication for Twitter 2018-08-21
Maria Documented my changes/contributions in the
assignment report
2018-08-21
Ilir Documented my changes/contributions in the
assignment report
2018-08-21
