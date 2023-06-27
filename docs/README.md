# My Flask Application

Welcome! This document will guide you through the installation and running of the lead and domain navigation app.

## Prerequisites

Make sure you have Python installed on your system. You can download Python from [the official website](https://www.python.org/downloads/).

It's also recommended to use a virtual environment. You can use `virtualenv`:

```shell
pip install virtualenv
virtualenv myenv
source myenv/bin/activate  # On MacOS/Linux, use this. On Windows, use `myenv\Scripts\activate`
```

## Cloning the Repository from Heroku

To clone the repository from Heroku, you will need to have a Heroku account and the Heroku CLI installed. You also need to be given access to the Safe Ship Heroku account as an admin. If you do not have the Heroku CLI installed, you can download it from the [Heroku website](https://devcenter.heroku.com/articles/heroku-cli).

Once the Heroku CLI is installed, you need to login to your Heroku account:

```shell
heroku login
```

After logging in, you can clone the repository by using the heroku git:clone command
```shell
heroku git:clone -a lead-nav
```

This will clone the repository into a new directory named after your app. Navigate into the directory:
```shell
cd your-app-name
```

Now, you are in the cloned repository and you can start working with the code.


