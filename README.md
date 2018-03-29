
# AWS CodePipeline Flowdock Integration

This repository provides AWS Lambda function which reacts to (AWS CodePipeline execution
state changes) and report these to team inbox in a Flowdock flow. 

The Lambda function is managed by [Serverless framework](https://serverless.com/).    

## Flowdock Setup

Follow the instructions described [here](https://www.flowdock.com/api/integration-getting-started).
After application has been created, open team inbox in Flowdock flow and add the application as a source.
This process provides you the Flowdock token which you should store for later use.   

## Setup AWS Infrastructure

Prerequisites:
- Python 3
- Serverless framework
- AWS security credentials. This guide uses [AWS CLI named profiles](https://docs.aws.amazon.com/cli/latest/userguide/cli-multiple-profiles.html)  
- Flowdock token

```
export FLOWDOCK_TOKEN=<add-your-flowdock-token-here>

python3 -m venv env

sls plugin install -n serverless-python-requirements
sls deploy --aws-profile <profile-name-here>

```


## Running Tests

```
source env/bin/activate
pip install -r requirements.txt
python test_handler.py
```