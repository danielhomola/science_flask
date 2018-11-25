<p align="center">
  <img src="https://github.com/danielhomola/science_flask/blob/master/frontend/static/img/logo_medium.png?raw=true" alt="Science Flask"/>
</p>

# Science Flask

Science Flask is a web-app template for online scientific research tools built 
with Python Flask, JavaScript and Bootstrap CSS.

There are two main reasons for creating this template:

1. Unfortunately there's quite
a lot of horribly looking and barely functioning scientific tools online.
The reason behind this is simple: we are scientists and not
web-developers. Keeping up with the latest trends, learning CSS, HTML
and modern web dev practices is simply not in our job description
and certainly not in our salary or grant money. So most of the time we
just want the tool to be online, in almost any shape or form. This,
however leads to two things:
    - Many amazing projects simply are not made available online, as the
     authors didn't have time/know-how/energy/funding for doing that.
    - Many projects that do end up getting some form of online presence
     look hideo4us and are not very user-friendly.

2. I realised that there's an incredible amount of overhead involved with
creating a fully functioning website, with user management, file uploads,
form validation, etc. You can learn Flask in about a weekend to a level
that you can understand code examples and start hacking away. But it
takes a __long__ time to actually get a working website with all the
features listed above.

Here's the simple idea behind Science Flask:

<p align="center">
  <img src="https://github.com/danielhomola/science_flask/blob/master/frontend/static/img/sf_flowchart.png?raw=true" alt="Science Flask"/>
</p>

Notice how everything in blue is non-specific to any scientific app. So
then why are we keep re-developing it? Ideally, scientists need not
to work on anything else than the green bit. Then they can plug
that into Science Flask with a few hours of work and have their
tool online in a day or two, instead of weeks.

I hope that by open-sourcing Science Flask, the activation energy for
turning an offline science project or research tool into a functioning
web-app will be lowered significantly. Hopefully this will not only mean
there'll be more science tools published, but also they'll look and feel
nicer and will be easier to use.

## Features

So why shouldn't you just start hacking away, following Flask tutorials?
What exactly can Science Flask give you?

- __Academic registration process:__ User's are only allowed to register with a
valid academic email address. This is to ensure that your tool is mainly
used for academic and research purposes and not for commercial uses. If your
institution or department uses a mail server which alters the end of your mail
address from the cannonical one (e.g. mail.imperial.ac.uk instead of 
imperial.ac.uk), you'll still be recognised. 
- __Standard user management:__
Furthermore it comes with all the rest of it: email addresses are
confirmed, users can change passwords, get password reset request if they
forgot it, etc. Thanks Flask-Security, you can also assign roles to different 
users and easily build custom user management logic. For example you might 
decide that certain users  can only use a part of the application, while other
users can access all features.
- __SQL database__: All user, study and analysis data is stored in an
SQLite by defaul. This can be changed to MySQL or Postgre SQL easily and
the same code will work, thanks to `SQLAlchemy`. Thanks to Flask-Migrate if you
change your app's model, you can easily upgrade your database even when your
app is deployed.
- __Admin panel:__ The model (database tables and relations between them)
 of your app can be easily edited online, from anywhere using CRUD operations. 
 Thanks to Flask-Admin, setting up an admin user who can edit users, and other 
 databases is as simple as modifying 2 lines in the config file.  
- __Upload form:__ Getting the data from the user sounds super simple but
you'd be surprised how long does it take to get a decent upload page.
Also it's very easy to build complex form logic from the bricks Science-
Flask provides.
- __Profile page__: This collects the uploaded studies of each user and
 let's them submit analysis on their data.
- __Analysis form__: Just like with the upload form, you can build custom
logic to ensure you get the parameters from the user just right. The
analysis job is then submitted to the backend. This uses `Celery`. Once
the analysis is ready, the user is notified in email. Then they can
download or check out their results online.
- __Logging__: All errors and warning messages are sent to the admins via
email. All analysis exceptions and errors could  be catched so that the
program crashes gracefully, letting the user know what happened.
- __Runs on Bootstrap.css__: Modern, mobile friendly, responsive.
Bootstrap makes writing good looking HTML pages dead easy.
- __Tool tips and tours__: Explain to the user how your application works with 
interactive tours (available on all the above listed pages) and tooltips.
- __Python3__: The whole project is written in Python3.5 (because it's 2017).

## Example app

In it's current form Science Flask implements a really simple scientific app.
 1. Users can register with an academic email address. 
 2. Upload one or two datasets as .csv or .txt files. 
 3. A series of checks are performed on the uploaded datasets:
    - all columns have to be numerical
    - each dataset must have a feature and sample number that is between a 
    predefined (see config.py) minium and maximum
     - if we have two datasets uploaded by the user, they need a minimum number
     of intersecting samples.
     - missing values are imputed with their column-wise median
 4. Then the user can submit an analysis and select the number of columns with 
 highest variance, that will be selected from each dataset.
 5. These features are used to calculate the a correlation matrix between them.
 6. If there's only one dataset uploaded, the correlations are calculated 
 between the features of this one dataset. If two datasets are uploaded then
 three matrices/plots are produced: two for the features of the individual 
 datasets and another that shows the correlation between the features of the 
 two disperate datasets.
 7. The resulting p-values of the correlation matrix are filtered using one of 
 the user selected corrrection for multiple testing methods: Bonferroni or 
 Benjamini Hochberg. The user can also specify the the alpha-level for 
 hypothesis testing. Only correlations that pass both of these will be displayed.
 8. The tables and heatmap of correlations can be downloaded by the user or
 checked online.

The app used to run on AWS on a t2.micro instance, but I shut it down to save the £10 each month. The  [__deployment.md__](https://github.com/danielhomola/science_flask/blob/master/deployment.md) 
explains the necessary steps to get your app to this stage. 

Nonetheless here are some screenshots from the site:

<p align="center">
  <img src="https://github.com/danielhomola/science_flask/blob/master/frontend/static/img/sf_main.png?raw=true" alt="Science Flask main page"/>
</p>

<p align="center">
  <img src="https://github.com/danielhomola/science_flask/blob/master/frontend/static/img/sf_profile.png?raw=true" alt="Science Flask profile page"/>
</p>

<p align="center">
  <img src="https://github.com/danielhomola/science_flask/blob/master/frontend/static/img/sf_upload.png?raw=true" alt="Science Flask upload page"/>
</p>

<p align="center">
  <img src="https://github.com/danielhomola/science_flask/blob/master/frontend/static/img/sf_admin.png?raw=true" alt="Science Flask admin page"/>
</p>


## Installation

Here's how to get Science Flask working in 2 minutes on Linux. It should be 
fairly similar on OSX. Unfortunatly I don't have any experience with Python 
development on Windows, so please let me know if you figured out how to get 
it to work a Win machine. 

Clone the repo 
```
git clone https://github.com/danielhomola/science_flask.git
cd science_flask
```

Make a Python 3 virtual environment using virtalenv or virtualenvwrapper. If these 
are foreign concepts to you, have a look [here](http://python-guide-pt-br.readthedocs.io/en/latest/dev/virtualenvs/).

```
mkvirtualenv --python=/usr/bin/python3 science_flask
workon science_flask
```

Install all the required Python packages into your virtual environment. Also
install RabbitMQ, [here's how](https://www.rabbitmq.com/download.html) if you're not on Ubuntu.
```
pip install -r requirements.txt
sudo apt-get install rabbitmq-server
```

Customize `frontend/config_example.py` and rename it to `frontend/config.py`
1. Generate a secret key for your app like [this](https://gist.github.com/geoffalday/2021517)
2. Setup the username, email, password for the admin. You can then log in with
 these credentials and go to the Admin profile from the Profile page. Then you
 can edit all the tables of the database from online.
3. Setup mail sending. I used [AWS's SES service](http://docs.aws.amazon.com/ses/latest/DeveloperGuide/quick-start.html),
 but you can use [Gmail](http://stackoverflow.com/questions/37058567/configure-flask-mail-to-use-gmail) also. 


Create the SQLite database of the app and add the admin user.
```
python db_create.py
```

If you'd like to use Alembic to migrate your database if you update it's schema, 
then read [this blog post](https://blog.miguelgrinberg.com/post/flask-migrate-alembic-database-migration-wrapper-for-flask) 
and the docs [here](https://blog.miguelgrinberg.com/post/flask-migrate-alembic-database-migration-wrapper-for-flask) and do:

```
./manage.py db init
./manage.py db migrate
./manage.py db upgrade
```

Open up two terminals. In one of them we'll run the Flask app. Edit the `manage.py`
file and edit its 1st line so it points to your VM interpreter.
```
# make it executible - only need to do this once
chmod +x manage.py
./manage.py runserver
```

In the second terminal window start the Celery worker:  
```
celery worker -A frontend.analysis.celery --loglevel=info
```

Create three folders for the log files, uploaded files and for the failed analyses.
```
mkdir userData
mkdir failedAnalyses
mkdir logs
```

Now go to Chrome and type in: http://0.0.0.0:5055/ and voila you have 
Science Flask running on your computer. You should be able to do everything that
you can do on the online demo. Time to modify it to your needs.


## Deployment to the cloud (AWS)

See [__deployment.md__](https://github.com/danielhomola/science_flask/blob/master/deployment.md).  

## What do you need to get started with web-app development?

Science Flask - as the name suggests - is built on Flask which is a micro 
web-framework written in PYthon. Don't panic. The actual sciency bit of your 
project can be in any language it doesn't have to be Python.

You'll need to be familiar with Flask and application development in Flask at
 least a bit, if you want to  use this template. The good news is though, you 
 really don't need to be a Flask ninja, and getting to sufficient level will 
 not take longer than an a weekend. 

Have a look at [this mega tutorial](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world),
 and make sure you read the first 5 chapters. You can pick up the rest as you 
 go along. Btw, there are dozens of other tutorials on Flask and the community 
 is really active and helpful so use and abuse Google and StackOverflow :)

You'll also need a good editor. I'd definitely recommend PyCharm. There's a
 community edition which is completely free. It has amazing debugging, 
 refactoring, and developing capabilities that will make your life so much 
 easier. 

## Tech stack

- The user facing part of the __frontend__ is written in HTML, Bootstrap CSS, 
JS and Bootstro.js. The templating is done with Jinja2 (default engine by Flask).

- The website is running on __Flask__. This is serving the clients with the
requested content (HTML, CSS, JS). It also validates the forms, writes
and reads from the database via SQLAlchemy and does everything else
you would expect from a web-framework to do.

- The __upload__ uses a bit of AJAX.

- The __backend__ can be in any language as long as __Celery__ can execute the
 job and you figure out a way how to do that. Doing the actual science bit of
your app in Python however is probably the easiest. Celery will run the
submitted analyses as a job queue, while your web-app can continue to
serve HTTP requests (as it should). 

- __RabbitMQ__ is a message broker between the
Flask web-app and Celery. This is basically a messenger that let's Celery
know about any new submitted jobs, while it let's Flask now if any of
the submitted jobs have finished running.

- The models of the app connect to an __SQLite__ database by default but this
could be changed easily.

- The emails are sent through __Amazon's free SES servcice__, but this can be
changed to any mail server.

## Overall structure of Science Flask 

### frontend

Frontend holds all the website components (HTML, CSS, JS) and Flask app that
 handles the views, the database models, the forms and their validation scripts.
 In the following description all folders are marked with bold letters. 
 
 - __static__: holds all the content of the website that will not change 
     - __css__: CSS files are kept here
         - main.css: most of the site's look is defined here
         - forms.css: some custom elements for the forms
         - bootstro.js: you can modifiy the look of the tour here
     - __fonts__: icons and special fonts live here
     - __img__: any images that you'd like to use (logos, figures, etc)
     - __js__: all JavaScript is sourced from here
          - analysis.js and upload.js: two main JavaScript files that you should
           look into
     - __uni__: holds the university domain database to check user emails
     - robots.txt, sitemap.xml: both needed so search-bots can do their job
 - __templates__: all the individual pages of the website are here
     - __security__: user registration and related pages 
     - __utils__: standard error code pages and some custom error pages
     - \_\_init.py\_\_: setup/initialization and configuration of the Flask app
     - analysis.py: main script that is called when the user submits a new job
     - config.py: all configuration info of the Flask app is stored here, make
     sure to read it  and set everything up properly.
     - forms.py: upload, analysis and registration forms with their validators
     - models.py: database models/tables for users, studies, analyses
     - views.py: implements the main logic of the individual pages, such as 
     upload, analysis, profile
     - view_functions.py: additional functions that are called by views.py which
     are put here so that views.py doesn't get more bloated as it is already.
 
### backend

This is where you'd put the actual bits and pieces of your scientific tool that
 do the analysis. In the frontend, analysis.py will call functions your pipeline
 of functions from here to carry out what your app is advertised to be doing.
 
 - utils: some utility  functions already live here that are called by the frontend
     - check_uploaded_files.py: this will check the uploaded files and make sure
     all the values in there are sensible and numerical. You can modify this to
     your liking/needs.
     - io_params.py: while an analysis/job is running a dictionary/hash of 
     parameters are kept that holds all the information about the particular
     job and the user. This script reads those parameters in and returns them
     as a dictionary so analysis.py can use it.
 

### userData

Each user that registers have a folder. Each uploaded dataset is then placed
 in the given user's folder. Finally the results of an analysis are stored 
 under the folder of the given study. This results in a hierarchy like this:
 
 - user1
     - study1
         - analysis1
         - analysis2
     - study2
         - analysis1
 - user2
     - study1
         - analysis1
         - analysis2
         - analysis3
- ...

### failedAnalyses

When an analysis fails, the state of the run (intermediate files and parameters
 prior to the bug) is all saved here. 


## Cite Science Flask

