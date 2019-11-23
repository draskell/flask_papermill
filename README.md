# flask_papermill

Flask server to do papermill jobs.  This app will act like a blog to allow users to add jupyter notebooks and provide functionality to run them with papermill.

### Some feature ideas:

1. Be able to download the papermill result pdf file. 
2. Be able to add Jupyter Notebooks
3. S3 support to save notebook results to S3 and generate presigned urls to let AWS render the result to the user.
4. Host or publish result notebookss with binder or commuter.

Inspired by [this post](https://medium.com/netflix-techblog/scheduling-notebooks-348e6c14cfd6) and associated talks at PyCon 2019.