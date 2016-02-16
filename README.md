[![Build Status](https://api.travis-ci.org/alphagov/notifications-delivery.svg?branch=master)](https://api.travis-ci.org/alphagov/notifications-delivery.svg?branch=master)

# notifications-delivery
Application to handle the interactions with the external message providers.

Job to read notifications from the queue.

Send the notifications.

Handle notification rate limiting.


# To run this application locally

* create an environment.sh file in root of this project. This file is ingored in .gitignore so
that you can add sensitive credentials locally if needed.

This file will be sourced by the run_app.sh script so the application will have all the configuration needed.

Add the following to the environment.sh file:

```
export NOTIFY_DELIVERY_ENVIRONMENT='config.Development'
export SECRET_KEY='dev-notify-secret-key'
export DANGEROUS_SALT='dev-notify-salt'
export NOTIFY_LOG_LEVEL='DEBUG'
export NOTIFY_APP_NAME='delivery'
export DELIVERY_LOG_LEVEL='DEBUG'
export PROCESSOR_MAX_NUMBER_OF_MESSAGES=1
export PROCESSOR_VISIBILITY_TIMEOUT=5
export NOTIFICATION_QUEUE_PREFIX='[unique-to-environment]-development'
export AWS_REGION='eu-west-1'
export NOTIFY_JOB_QUEUE='[unique-to-environment]-notify-job-queue'
export API_HOST_NAME='http://localhost:6011'
export DELIVERY_CLIENT_USER_NAME='dev-notify-delivery'
export DELIVERY_CLIENT_SECRET='dev-notify-secret-key'
export JOB_POLL_INTERVAL_SECONDS=5
export DELIVERY_POLL_INTERVAL_SECONDS=1

```

SECRET_KEY and DANGEROUS_SALT and DELIVERY_CLIENT_USER_NAME and DELIVERY_CLIENT_SECRET must match values in notifications-api config.

If you add a new item to config.py add that to your local environment file and get it added
to the environment on the deployment target. The environment.sh is ingored in version control as there may be
cases during local development where you might want to set credentials for some external system to be connected
to during development.

For tests use environment_test.sh which is in version control and is used from unit tests and travis build so should
never contain any sensitive credentials.

In order to run any management commands you must source your environment file first or create wrapper shell scripts
to include sourcing the environment file before calling a command.

As configuration values must read from environment the application to fail on startup if not any values not present.

There may be good reason to hard code some values in the config.py but those should be the exception.

Then to actually run:

```
scripts/run_app.sh
```
