# flask_papermill

Flask server to do papermill jobs.  This app will act like a blog to allow users to add jupyter notebooks and provide functionality to run them with papermill.

# Environment Variables:

### Mail

These environment variables allow the system to send alerts to users and administrators.

- __EMAIL_DOMAINS__: comma separated list of domains which are allowed for user emails.
- __MAIL_SERVER__: the server to use to send mail.
- __MAIL_PORT__: the port to use to send mail on the server specified with MAIL_SERVER.
- __MAIL_USE_TLS__: whether or not to use TLS when sending mail.
- __MAIL_USERNAME__: username which the mail should come from.
- __MAIL_PASSWORD__: password of the mail account associated with the mail username specified by MAIL_USERNAME.
- __ADMIN_EMAIL__: admin email to send error messages etc.

### S3

These credentials are used by papermill to gain access to the AWS S3 bucket where notebooks and output can be stored.  You can either specify these environment variables or have a `~/.aws/credentials` file which has the credentials.  Papermill just uses the `boto3` package, so you can consult the [boto3 credentialing documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/configuration.html) for more info.

- __AWS_ACCESS_KEY_ID__: The access key for your AWS account.
- __AWS_SECRET_ACCESS_KEY__: The secret key for your AWS account.
- __AWS_PROFILE__: If you have multiple accounts configured (in `~/.aws/credentials), you can specify which account to use with this variable.


### Some feature ideas:

1. S3 support to save notebook results to S3 and generate presigned urls to let AWS render the result to the user.
2. Host or publish result notebookss with binder or commuter.

Inspired by [this post](https://medium.com/netflix-techblog/scheduling-notebooks-348e6c14cfd6) and associated talks at PyCon 2019.