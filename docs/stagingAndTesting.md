# Testing the App with Flask Run and Using leads-staging

## Testing with Flask Run on Local Servers

When developing a Flask app, you can use `flask run` command to start a local server and test your application. Here are some notes on testing with Flask run:

- Make sure you have the necessary dependencies and environment set up locally.
- Run `flask run` command in your project directory to start the local server.
- Access the app in your web browser using the provided local server address (e.g., http://localhost:5000).
- Test the app's functionality, including form submissions, data processing, and navigation.
- Keep in mind that some features may not work in the local environment due to dependencies, environment variables, or external services.

## Limitations of Local Environment

While testing with Flask run on local servers is useful, there are some limitations to consider:

- Certain functionalities may rely on external services that are not available in the local environment. For example, sending password reset emails may require access to an email server.
- Integration with third-party services, such as payment gateways or external APIs, may not function fully in the local environment.
- Environment-specific configurations, such as database connections or environment variables, may differ between the local environment and production environment.

It's important to be aware of these limitations and test the affected functionalities in an environment that closely matches the production environment.

## Testing with leads-staging App

To test the live version of the app before pushing the repository to the main app (`lead-nav`), you can use the `leads-staging` app associated with the app's Git repository. Here's how you can test with leads-staging:

1. Ensure that you have the necessary access and permissions for the `leads-staging` app on Heroku.
2. Push your changes to the `leads-staging` branch in the app's Git repository.
3. Visit the `leads-staging` app's URL to test the live version and verify the functionality.
4. Test all the features, including those that rely on external services, to ensure everything works as expected.
5. Once you're satisfied with the testing on leads-staging, you can proceed to push the changes to the main app (`lead-nav`).

Using the `leads-staging` app allows you to test the live version of your app in an environment that closely resembles the production environment without impacting the main app.

Remember to handle sensitive information appropriately and use test data when testing in live environments.