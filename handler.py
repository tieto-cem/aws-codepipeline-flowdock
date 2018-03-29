import json
import requests
import boto3
import os

PIPELINE_STATE_CHANGE = 'CodePipeline Pipeline Execution State Change'
ACTION_STATE_CHANGE = 'CodePipeline Action Execution State Change'

client = boto3.client('codepipeline', region_name='eu-west-1')


def pipeline_details(event):
    region = event['region']
    detail = event['detail']
    pipeline_name = detail["pipeline"]
    pipeline_execution_id = detail["execution-id"]

    return {
        'region': region,
        'pipeline_name': pipeline_name,
        'stage_name': detail['stage'] if 'stage' in detail else '',
        'action_name': detail['action'] if 'action' in detail else '',
        'pipeline_exec_id': pipeline_execution_id,
        'pipeline_url': f'https://{region}.console.aws.amazon.com/codepipeline/home?region={region}#/view/{pipeline_name}',
    }


def build_details(pipeline):

    pipeline_execution = client.get_pipeline_execution(
        pipelineName=pipeline['pipeline_name'],
        pipelineExecutionId=pipeline['pipeline_exec_id'])

    artifact_revision = pipeline_execution["pipelineExecution"]["artifactRevisions"][0]

    return {
        'revision_id': artifact_revision["revisionId"][:7],
        'revision_url': artifact_revision["revisionUrl"],
        'revision_summary': artifact_revision["revisionSummary"]
    }


def pipeline_approval_token(pipeline_name):
    state = client.get_pipeline_state(name=pipeline_name)

    approve_action = [action
                      for stage in state['stageStates'] if stage['stageName'] == 'Production'
                      for action in stage['actionStates'] if action['actionName'] == 'Approve']
    if approve_action:
        return approve_action[0]['latestExecution']['token']


def base_msg(pipeline):
    return {
        'flow_token': os.environ['FLOWDOCK_TOKEN'],
        'event': 'activity',
        'author': {
            'name': 'AWS CodePipeline'},
        'body': '',
        'external_thread_id': pipeline['pipeline_exec_id'],
        'thread': {
            'title': f'''Pipeline <a href="{pipeline['pipeline_url']}">{pipeline['pipeline_name']}</a> build #{pipeline['pipeline_exec_id']}'''}}


def pipeline_started_msg(base_msg, pipeline):
    base_msg['title'] = 'Pipeline started'
    base_msg['thread']['status'] = {
        "color": "blue",
        "value": "RUNNING"
    }
    return base_msg


def pipeline_build_started_msg(base_msg, pipeline):
    build = build_details(pipeline)
    base_msg['title'] = f'''Building commit <a href="{build['revision_url']}">{build['revision_id']}</a>: {build['revision_summary']}'''
    base_msg['thread']['status'] = {
        "color": "blue",
        "value": "RUNNING"
    }
    return base_msg


def pipeline_approval_pending_msg(base_msg, pipeline):
    pipeline_name = pipeline['pipeline_name']
    token = pipeline_approval_token(pipeline_name)
    approve_url = f'''https://{pipeline['region']}.console.aws.amazon.com/codepipeline/home?region={pipeline['region']}#/view/{pipeline_name}/Production/Approve/approve/{token}'''

    base_msg['title'] = f'''Approve {pipeline['stage_name'].lower()}? <a href="{approve_url}"> Approve or reject</a>'''
    base_msg['thread']['status'] = {
        "color": "yellow",
        "value": f'''APPROVE - {pipeline['stage_name'].upper()}?'''
    }
    return base_msg


def pipeline_failed_msg(base_msg, pipeline):
    base_msg['title'] = f'''Pipeline action "{pipeline['action_name']}" failed'''
    base_msg['thread']['status'] = {
        "color": "red",
        "value": "FAILED"
    }
    return base_msg


def pipeline_succeeded_msg(base_msg, pipeline):
    base_msg['title'] = "Build succeeded"
    base_msg['thread']['status'] = {
        "color": "green",
        "value": "SUCCEEDED"
    }
    return base_msg


def pipeline_approved_msg(base_msg, pipeline):
    base_msg['title'] = f'''{pipeline['stage_name']} approved'''
    base_msg['thread']['status'] = {
        "color": "blue",
        "value": "RUNNING"
    }
    return base_msg


def pipeline_prod_deploy_rejected_msg(base_msg, pipeline):
    base_msg['title'] = f'''{pipeline['action']} not approved'''
    base_msg['thread']['status'] = {
        "color": "purple",
        "value": "REJECTED"
    }
    return base_msg


def flowdock_msg(event):
    """
        Returns Flowdock message based on the received event. Returns None if the event doesn't
        represent a change that should be notified to Flowdock.

        Args:
            event (dict): AWS CodePipeline state change event send by CloudWatch Events
    """

    event_type = event['detail-type']
    event_state = event['detail']['state']

    msg = None

    if event_type == PIPELINE_STATE_CHANGE:
        if event_state == 'STARTED':
            msg = pipeline_started_msg
        elif event_state == 'SUCCEEDED':
            msg = pipeline_succeeded_msg
    elif event_type == ACTION_STATE_CHANGE:
        action = event['detail']['action']
        if event_state == 'FAILED':
            if action == 'Approve':
                msg = pipeline_prod_deploy_rejected_msg
            else:
                msg = pipeline_failed_msg
        elif event_state == 'STARTED':
            if action == 'Approve':
                msg = pipeline_approval_pending_msg
            elif action == 'Source':
                msg = pipeline_build_started_msg
        elif event_state == 'SUCCEEDED' and action == 'Approve':
            msg = pipeline_approved_msg

    if not msg:
        return None
    else:
        pipeline = pipeline_details(event)
        basemsg = base_msg(pipeline)
        return msg(basemsg, pipeline)


def send_flowdock_msg(msg):
    """Sends specified message to Flowdock"""
    headers = {'Content-Type': 'application/json', 'Accept': 'text/plain'}
    requests.post('https://api.flowdock.com/messages', data=json.dumps(msg), headers=headers)


def main(event, context):
    print('event received:', event)
    msg = flowdock_msg(event)

    if msg:
        send_flowdock_msg(msg)
        return msg
    else:
        print('event ignored')
        return ''


if __name__ == "__main__":
    main('', '')
