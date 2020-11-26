# PEDGAO

Small document which is going to describe the way I worked on the project, my thoughts and my reflexions during the codig process.

## Disclaimer

_This document contains all my thoughts and the way I processed during the development of the program. Dome of the things 
listed below may not be in the code or may be completely different but I decided not to remove anything for educational 
purpose. For real working of the code please refer to the comment in the code itself which are complete and comment the 
final code_

## Definition of a bad evaluation

First of all, what is a bad evaluation ? A bad evaluation is an evaluation that has not been done properly or at least 
doesn't respect the 42 standards. The standards exist to maintain a certain level of competence amongst the 42 students
and to preserve the reputation of 42 in the professional world but there is also a pedagogical aspect that is very
important. If the corrector and the corrected don't learn something from an evaluation than it has no real purpose. It is
important that the context and other factors are taken into account before considering that an evaluation is bad.

I see the following scenarios:
1. A corrector graded a project to pass but moulinette failed the project.
2. A corrector graded a project to pass and the corrected cancelled the project.
3. A correction lasted too short to be a real correction, depending on the project. (ex 42sh < 30min is not tested at all, just minimum requirements)
4. A corrected booked 2 corrections at the same time.

Let's see these cases more in detail.

Note: All the cases described below need to be reviewed by hand, there is a high chance that there is a very good reason
for this bad evaluation.

### Case 1
In this case the corrector graded a project to pass, green result, but the moulinette which came after the corrector graded the project a red grade.
In this case we have a bad evaluation because the student who corrected may have deliberately put a good note fo his friend
or didn't see a big problem in the code.

This case needs to be moderated and reconsidered before taking action on the bad student because some projects could be hard to detect anomalies especially
if the corrector didn't do the project. Again, issues such a norm errors etc should always be seen no matter the student.

Example:
```text
Thomas corrected Jens on his ft_printf 100 but moulinette graded Jens 50 because Jens did not implement the float converter which was asked in the pdf.
```

What is needed to detect this case ?
- grade of the evaluation
- final grade of the project
- flag given during the evaluation

### Case 2
If the corrector gives a good grade on a project but the corrected cancels his project it may be because the corrector 
found a problem in the code that he thinks is not worth a zero or crash but the corrected does. In this case manual verification 
should give all the needed information about the potential problem. Correctors need to be firm especially in the beginning of the cursus.µ

It might not be a big issue, but it is still important for a corrector not to be afraid of grading badly even if there is a minor issue.

Example:
```text
Thomas corrected Jens on his minishell where ctrl+c does not make the prompt reappear as it should.
```

What is needed to detect this case ?
- grade of the evaluation
- final grade of the project

### Case 3
This case only applies to big projects, it would otherwise be very hard to calibrate on small projects. Corrections can 
sometimes be very long for some projects and some students may simply skip some parts of the correction pdf to win some 
time but that is not something good.

Example:
```text
Thomas corrected Jens on 42sh for only 20 minutes where a good correction of 42sh should last 1 hour.
```

What is needed to detect this case ?
- estimated duration of the evaluation
- start time of evaluation
- end time of evaluation
- number of project retrys

### Case 4
In this case there is not too much to discuss. If the corrected booked 2 corrections at the same moment and the correctors
accepted to do them both at the same time, then both correctors and the corrected should be sanctioned.

Double corrections may interfere with the capability of one corrector to find an error in the code or to be to shy to 
say something if the other corrector takes too much space.

What is needed to detect this case ?
- time of booking evaluation

## How to detect

How to detect these bad evaluations is a very big question. How can we make efficient requests to the API ?
How many times will the program be called a day/week ? Are the api limits big enough for long term use ? 
Is there a different way to do it without using the api ?

All those questions came through my mind when I started the project. I described my toughts on different aspects of the
code bellow by category.

The system I use is a set of rules that are each declared as a function which will return true in case the given evaluation
is considered bad by this rule. Very easy to add a lot more, and you oby have to add the function in the function array 
and it is automatically integrated to the whole detection process.

The big advantage of this system is that a rule could very easily be updated and improved without giving the full 
code to someone else.

### Internal working

The problem here is that the **_scalte team_** endpoint contains a lot of information which takes a lot of time to gather 
from the api. From my tests, a ft_ssl_md5 correction needs 3 seconds on my connection to be downloaded. (20Mbs download)

The plan is to gather the id of all students of The Hive and to pass all of their ids into a function which will gather 
all the scale teams they have benn involved in. This may take a lot of time but is I think the best solution to be sure 
not to miss any data.

Once we have all the user ids, we could get all the scale teams and we the process each one by one by keeping the strict
minimum of information so that we do not work with too much data in RAM. Once the data is stored, our detection functions
would do the rest and print the result to the user.

If we can filter and sort in the request we may be able to reduce the number of requests done to the api which will 
increase the process speed and reduce wait time. After some research I found out that I can set a range on the 'created_at'
parameter to only grab what I need in the imposed timeframe. This is going to make life a lot easier and programs a lot
faster due to less requests to do. Apparently we can not really filter on anything interesting :/.

So for now, the program is going to ask for the timeframe in which it is supposed to search for 'bad evaluations'. The 
program then runs through all the api call and the transforms the gathered data. Results are shown on the screen and stored
in a file or database.

The logic behind everything would be like this:
```python
for each student:
    for each evaluation as corrected in the last timeframe:
        if bad evaluation:
            create bad_eval object
            store bad_eval in list
            continue
        else:
            continue

return list
```

The scale_team endpoint gives me the possibility to ask for the scale_teams as corrector or corrected. I first taught of
using both to be sure not to miss any scale_team. I realised that if you ask all the scales of all students from corrected
point of vue, you should normally not miss any.

### User Interactions

For the user interactions I first tought that the best solution to do it is to use a command line program. Efficient and
also a lot less memory consuming. Coding it will also be easier so I only see advantages but after thinking a bit I
decided that a graphical interface or a web interface would be a better solution for the input part. Not sure if I will 
code it though.

User Interfaces should have input boxes:
- Time to check back
- User credentials
- User secret
- Project ?
- School ?

In command line it would be first, second and third argument:
- first -> client_id
- second -> secret
- third -> time

Or use a config file for both possibilities.

Due to the asked support for a docker container, the best solution would be the UI but it asks a lot of code which is,
I think, absolutely not necessary for this program to work perfectly fine (although it as always nice to have a UI).
By using a config file it would be easier to support both Docker and non docker but with some docker magic it appears we
can pass arguments to our program. Hope it works, would be nice to support both config file and normal input.

Docker doesn't seem to be a problem after all. The command line interface is the best solution for the time I had and 
my previous knowledge of python. It wouldn't take too much effort to implement a graphical user interface and it would be
a lot more user-friendly.

argparse is the easiest way to handle the parameters.

### IO

First I only wanted to print the data in the console because I taught I had to setup a whole mysql server so I didn't 
want to. After reading the assignment multiple times it appears that it is SQLite and that by consequence it is a local 
file. Thanks to some beautiful packages, I am able to write with SQL query's to a SQLite file.

I think printing the solution is the way to do it because files are annoying but it is nice to be able to store your 
data in a file. I would prefer to have is stored in a json file for continuity with the 42api.

## Alternative/better solution

A better and more efficient solution would be to have webhooks. This way we can make sure that we make mistake in any requests
to the api server which could lead to missing some evaluations. Bad timestamps could also be a big issue.

The webhooks could give the opportunity to treat the problem directly when it appears and not once a day or once a week.
The content of the previous treated problems could be stored in a local database or file which would be much faster because
you can do a lot more requests to a database than the api and you could also decide how the data is structured which
is not possible with the current 42 api. Previous bad evaluations from a specific user could also be a lot easier to gather
from a database.

I think it would be a lot less effort to do it like this because it requires no human intervention except for investigating
a possible bad evaluation.

The investigation process could be enhanced by having a web app that shows all the relevant information in a pretty interface
and a lot of buttons to interact with these "reports".

## Other tools

- Tool for tutors to tig more easily during piscines
- Map of connected students
- discord bot that automatically creates a discord vocal channel for remote evaluations
- tool for exam statistics of ongoing exams (dashboard of current exams)