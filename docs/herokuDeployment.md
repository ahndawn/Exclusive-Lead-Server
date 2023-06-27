# Deploying Updates to Heroku

This document provides a guide on how to deploy updates from your local Git repository to Heroku.

## Prerequisites

- Ensure that you have the [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli) installed.
- Make sure you are logged into Heroku. You can use the following command to log in:

    ```shell
    heroku login
    ```

- Your project should already be a Git repository. If it's not, you can initialize it as a Git repository by running:

    ```shell
    git init
    ```

- Make sure that your repository is associated with the Heroku app. You can add a Heroku remote using the following command:

    ```shell
    heroku git:remote -a lead-nav
    ```

## Deploying to Heroku

1. Before deploying, ensure that all your changes are committed to the Git repository:

    ```shell
    git add .
    git commit -m "Your commit message here"
    ```

2. Once your changes are committed, you can deploy to Heroku by pushing your code to the Heroku remote:

    ```shell
    git push heroku master
    ```

3. Sometimes, you might have to migrate your database. You can run migrations (if applicable) like this:

    ```shell
    heroku run python manage.py db upgrade
    ```

4. Your application should now be deployed with the latest changes. You can open it in the web browser with the following command:

    ```shell
    heroku open
    ```

## Troubleshooting

If you encounter any issues during deployment, you can check the logs for any errors:

```shell
heroku logs --tail
```


## Creating and Deploying a New Heroku App

If you are starting with a fresh codebase and want to create a new Heroku app for deployment, follow these steps:

1. **Initialize the Git repository** if it's not already a Git repository:

    ```shell
    git init
    git add .
    git commit -m "Initial commit"
    ```

2. **Login to Heroku** if you haven't already:

    ```shell
    heroku login
    ```

3. **Create a new Heroku app**:

    ```shell
    heroku create your-new-app-name
    ```

    Note: Replace `your-new-app-name` with the desired name for your Heroku app. If you want Heroku to assign a name automatically, just use `heroku create` without specifying a name.

4. **Add the Heroku remote** to your Git repository:

    ```shell
    heroku git:remote -a your-new-app-name
    ```

5. **Set environment variables**. You can do this in two ways:

    - **Option A**: Use the `.env` file with your environment variables, you can use the `heroku config:push` command (you’ll need the [Heroku Config plugin](https://devcenter.heroku.com/articles/heroku-local#set-up-your-local-environment-variables) for this):
        
        .env file example:
        DATABASE_URL=URL FOUND FROM HEROKU POSTGRES ACCOUNT
        TWILIO_ACCOUNT_SID=SID FOUND FROM TWILIO
        TWILIO_AUTH_TOKEN=AUTH TOKEN FOUND FROM TWILIO
        GOOGLE_SHEETS_CREDENTIALS={GOOGLE SHEET CREDENTIALS GO HERE (FOUND FROM GOOGLE CLOUD CONSOLE)}

        ```shell
        heroku plugins:install heroku-config
        heroku config:push -a your-new-app-name
        ```

    - **Option B**: Set environment variables directly via the terminal, line by line:

        ```shell
        heroku config:set VAR_NAME=value -a your-new-app-name
        ```

        Replace `VAR_NAME` with the name of the environment variable and `value` with its value.

6. **Deploy your code** to Heroku:

    ```shell
    git push heroku master
    ```

    If you are working on a different branch (not master), replace `master` with your branch name.

7. **Run database migrations** if applicable:

    ```shell
    heroku run python manage.py db upgrade
    ```

8. **Open your app** in the web browser:

    ```shell
    heroku open
    ```