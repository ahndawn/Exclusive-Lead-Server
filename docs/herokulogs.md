# Heroku Logs and Papertrail Integration

## Heroku Logs in the CLI

Heroku provides a command-line interface (CLI) for managing and accessing logs of your applications. Here's an overview of how to work with Heroku logs in the CLI:

- To view real-time logs, use the command `heroku logs --tail`. This displays logs streaming in your terminal.
- By default, logs from all dynos and process types are shown. You can filter logs by specifying a specific dyno or process type using the `--dyno` or `--ps` flags.
- The `--source` flag allows you to filter logs by source. For example, `--source app` filters logs from the application source.
- To limit the number of logs shown, you can use the `--num` flag followed by the desired number of logs.
- The `heroku logs` command provides various options and flags to customize log output. You can explore them further in the Heroku CLI documentation.

## Integrating Papertrail with Your App

Papertrail is a log management tool that integrates well with Heroku. Here's how to integrate Papertrail with your app:

1. Sign up for a Papertrail account at [papertrail.com](https://www.papertrail.com/).
2. Create a Papertrail log destination within your Papertrail account. Note down the host and port information provided by Papertrail.
3. In your Heroku app directory, run the command `heroku drains:add syslog://<host>:<port>`. Replace `<host>` and `<port>` with the actual host and port information from your Papertrail log destination.

## Accessing Logs with Specific Dates on Papertrail

To access logs with specific dates on Papertrail, follow these steps:

1. Log in to your Papertrail account.
2. Navigate to the Papertrail log search interface.
3. In the search bar, enter the desired date or date range in the format `date:YYYY-MM-DD` or `date:YYYY-MM-DD..YYYY-MM-DD`.
4. Press Enter or click the search button to retrieve logs from the specified date or date range.

Papertrail offers additional search and filtering options, such as searching for specific log levels, sources, or keywords. You can explore these options in the Papertrail documentation.

## Watching Logs on Heroku.com

Heroku provides a web-based log viewer that allows you to watch logs directly on Heroku.com. Here's how to access logs through the Heroku web interface:

1. Log in to your Heroku account at [dashboard.heroku.com](https://dashboard.heroku.com/).
2. Select your app from the app list to access the app dashboard.
3. In the app dashboard, navigate to the "Metrics" tab.
4. Click on the "View Logs" button to open the log viewer.
5. The log viewer displays logs in real-time. You can filter logs by process type, log level, or search for specific keywords.

Using the log viewer on Heroku.com provides a convenient way to monitor and analyze logs directly from your browser.

Remember to refer to the Heroku and Papertrail documentation for more detailed information and advanced usage of logs and log management.