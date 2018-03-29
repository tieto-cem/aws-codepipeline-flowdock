import handler
import os
import unittest
from botocore.stub import Stubber

pipeline_started_event = {
    "version": "0",
    "id": "b8d89c55-f3a6-7e3c-9b72-4e3a38d0c03b",
    "detail-type": "CodePipeline Pipeline Execution State Change",
    "source": "aws.codepipeline",
    "account": "123456789012",
    "time": "2018-03-09T08:12:43Z",
    "region": "eu-west-1",
    "resources": ["arn:aws:codepipeline:eu-west-1:123456789012:my-pipeline"],
    "detail": {
        "pipeline": "my-pipeline",
        "execution-id": "3776ce0b-26ba-40a5-a1ef-2f1f2591934e",
        "state": "STARTED",
        "version": 3.0}}

pipeline_source_event = {
    "version": "0",
    "id": "80d310ed-5253-9eb6-f28b-404bf25b47b0",
    "detail-type": "CodePipeline Action Execution State Change",
    "source": "aws.codepipeline",
    "account": "123456789012",
    "time": "2018-03-09T08:12:47Z",
    "region": "eu-west-1",
    "resources": ["arn:aws:codepipeline:eu-west-1:749354820659:my-pipeline"],
    "detail": {
        "pipeline": "my-pipeline",
        "execution-id": "3776ce0b-26ba-40a5-a1ef-2f1f2591934e",
        "stage": "Source",
        "action": "Source",
        "state": "STARTED",
        "type": {"owner": "ThirdParty", "provider": "GitHub", "category": "Source", "version": "1"},
        "version": 3.0}}

pipeline_failed_event = {
    "version": "0",
    "id": "0810c50b-e4ae-3d92-a760-41ee2291d217",
    "detail-type": "CodePipeline Action Execution State Change",
    "source": "aws.codepipeline",
    "account": "123456789012",
    "time": "2018-03-09T08:13:24Z",
    "region": "eu-west-1",
    "resources": ["arn:aws:codepipeline:eu-west-1:749354820659:my-pipeline"],
    "detail": {
        "pipeline": "my-pipeline",
        "execution-id": "3776ce0b-26ba-40a5-a1ef-2f1f2591934e",
        "stage": "Build",
        "action": "Build",
        "state": "FAILED",
        "type": {"owner": "AWS", "provider": "CodeBuild", "category": "Build", "version": "1"},
        "version": 3.0}}

pipeline_pending_approval_event = {
    "version": "0",
    "id": "16aa4d0d-08d0-c3ce-f41a-1e9f08f7dc1c",
    "detail-type": "CodePipeline Action Execution State Change",
    "source": "aws.codepipeline",
    "account": "123456789012",
    "time": "2018-03-09T08:19:49Z",
    "region": "eu-west-1",
    "resources": ["arn:aws:codepipeline:eu-west-1:123456789012:my-pipeline"],
    "detail": {
        "pipeline": "my-pipeline",
        "execution-id": "3776ce0b-26ba-40a5-a1ef-2f1f2591934e",
        "stage": "Production",
        "action": "Approve",
        "state": "STARTED",
        "type": {"owner": "AWS", "provider": "Manual", "category": "Approval", "version": "1"}, "version": 3.0}}

pipeline_succeeded_event = {
    "version": "0",
    "id": "f338242d-02f5-0053-79cd-bccd42f9cf24",
    "detail-type": "CodePipeline Pipeline Execution State Change",
    "source": "aws.codepipeline",
    "account": "123456789012",
    "time": "2018-03-09T08:25:01Z",
    "region": "eu-west-1",
    "resources": ["arn:aws:codepipeline:eu-west-1:123456789012:my-pipeline"],
    "detail": {
        "pipeline": "my-pipeline",
        "execution-id": "3776ce0b-26ba-40a5-a1ef-2f1f2591934e",
        "state": "SUCCEEDED",
        "version": 3.0}}

get_pipeline_execution_response = {
    'pipelineExecution': {
        'pipelineName': 'my-pipeline',
        'pipelineVersion': 3,
        'pipelineExecutionId': '3776ce0b-26ba-40a5-a1ef-2f1f2591934e',
        'status': 'Succeeded', 'artifactRevisions': [{
            'name': 'app-sources',
            'revisionId': '5963024454c0c2818d5fa7b9cad3d3cd3120e78d',
            'revisionChangeIdentifier': '2018-02-15T14:32:36Z',
            'revisionSummary': 'initial commit',
            'created': '2018-02-15T14:32:36Z',
            'revisionUrl': 'https://github.com/cxcloud/mc-accelerator/commit/5963024454c0c2818d5fa7b9cad3d3cd3120e78d'}]}}

get_pipeline_state_response = {
    'pipelineName': 'test-pipeline',
    'pipelineVersion': 1,
    'stageStates': [
        {
            'stageName': 'state1',
            'inboundTransitionState': {
                'enabled': True
            },
            'actionStates': [
                {
                    'actionName': 'Deploy',
                    'latestExecution': {
                        'status': 'Succeeded',
                        'summary': '',
                        'lastStatusChange': '2018-03-08T14:04:55Z',
                        'externalExecutionId': '1234',
                        'externalExecutionUrl': 'url'
                    },
                    'entityUrl': 'url'
                }
            ],
            'latestExecution': {
                'pipelineExecutionId': '1234',
                'status': 'Succeeded'
            }},
        {
            'stageName': 'Production',
            'inboundTransitionState': {
                'enabled': True
            },
            'actionStates': [
                {
                    'actionName': 'Approve',
                    'latestExecution': {
                        'status': 'InProgress',
                        'lastStatusChange': '2018-03-08T14:04:55Z',
                        'token': '69628e7e-d309-4a6a-b01d-9f1aeca2060d'
                    }
                },
                {
                    'actionName': 'Deploy',
                    'latestExecution': {
                        'status': 'Succeeded',
                        'summary': '',
                        'lastStatusChange': '2018-03-08T14:04:55Z',
                        'externalExecutionId': '1234',
                        'externalExecutionUrl': 'url'
                    },
                    'entityUrl': 'url'
                }
            ],
            'latestExecution': {
                'pipelineExecutionId': 'a8b63ff6-49c7-4da4-ac71-1308e85027a5',
                'status': 'InProgress'
            }
        }
    ]
}


class TestHandler(unittest.TestCase):

    def test_pipeline_details(self):
        pipeline = handler.pipeline_details(pipeline_started_event)

        self.assertEqual(pipeline, {
            'region': 'eu-west-1',
            'action_name': '',
            'stage_name': '',
            'pipeline_name': 'my-pipeline',
            'pipeline_url': 'https://eu-west-1.console.aws.amazon.com/codepipeline/home?region=eu-west-1#/view/my-pipeline',
            'pipeline_exec_id': '3776ce0b-26ba-40a5-a1ef-2f1f2591934e',
        })

    def test_build_details(self):
        expected_request = {
            'pipelineExecutionId': '3776ce0b-26ba-40a5-a1ef-2f1f2591934e',
            'pipelineName': 'my-pipeline'}

        with Stubber(handler.client) as stubber:
            stubber.add_response('get_pipeline_execution', get_pipeline_execution_response, expected_request)
            build = handler.build_details({
                'region': 'eu-west-1',
                'pipeline_name': 'my-pipeline',
                'pipeline_exec_id': '3776ce0b-26ba-40a5-a1ef-2f1f2591934e'})

            self.assertEqual(build, {
                'revision_id': '5963024',
                'revision_url': 'https://github.com/cxcloud/mc-accelerator/commit/5963024454c0c2818d5fa7b9cad3d3cd3120e78d',
                'revision_summary': 'initial commit'})

    def test_base_msg(self):
        pipeline = {'pipeline_name': 'pipeline_name',
                    'pipeline_url': 'pipeline_url',
                    'pipeline_exec_id': 'pipeline_id'}

        os.environ['FLOWDOCK_TOKEN'] = 'FT1234'

        base_msg = handler.base_msg(pipeline)

        self.assertEqual(base_msg, {
            'flow_token': 'FT1234',
            'event': 'activity',
            'author': {
                'name': 'AWS CodePipeline'},
            'body': '',
            'external_thread_id': 'pipeline_id',
            'thread': {
                'title': f'''Pipeline <a href="pipeline_url">pipeline_name</a> build #pipeline_id'''}})

    def test_pipeline_started_msg(self):
        base_msg = {
            'flow_token': 'FT1234',
            'event': 'activity',
            'author': {
                'name': 'AWS CodePipeline'},
            'body': '',
            'external_thread_id': 'pipeline_id',
            'thread': {
                'title': f'''Pipeline <a href="pipeline_url">pipeline_name</a> build #pipeline_id'''}}

        self.assertEqual(handler.pipeline_started_msg(base_msg, {}),
                         {'flow_token': 'FT1234',
                          'event': 'activity',
                          'author': {
                              'name': 'AWS CodePipeline'},
                          'body': '',
                          'title': 'Pipeline started',
                          'external_thread_id': 'pipeline_id',
                          'thread': {
                              'title': f'''Pipeline <a href="pipeline_url">pipeline_name</a> build #pipeline_id''',
                              'status': {
                                  'color': 'blue',
                                  'value': 'RUNNING'}}})

    def test_pipeline_started_msg2(self):
        msg = handler.flowdock_msg(pipeline_started_event)
        self.assertIsNotNone(msg)
        self.assertEqual('RUNNING', msg['thread']['status']['value'])

    def test_pipeline_build_started_msg(self):
        with Stubber(handler.client) as stubber:
            stubber.add_response('get_pipeline_execution', get_pipeline_execution_response)

            msg = handler.flowdock_msg(pipeline_source_event)
            self.assertIsNotNone(msg)
            self.assertEqual('RUNNING', msg['thread']['status']['value'])

    def test_pipeline_approval_pending_msg(self):
        with Stubber(handler.client) as stubber:
            stubber.add_response('get_pipeline_state', get_pipeline_state_response)

            msg = handler.flowdock_msg(pipeline_pending_approval_event)
            self.assertIsNotNone(msg)
            self.assertEqual('APPROVE - PRODUCTION?', msg['thread']['status']['value'])
            expected_url = 'https://eu-west-1.console.aws.amazon.com/codepipeline/home?region=eu-west-1#/view/my-pipeline/Production/Approve/approve/69628e7e-d309-4a6a-b01d-9f1aeca2060d'
            expected_title = f'Approve production? <a href="{expected_url}"> Approve or reject</a>'
            self.assertEqual(expected_title, msg['title'])

    def test_pipeline_succeeded_msg(self):
        msg = handler.flowdock_msg(pipeline_succeeded_event)
        self.assertIsNotNone(msg)
        self.assertEqual('SUCCEEDED', msg['thread']['status']['value'])
        self.assertEqual('Build succeeded', msg['title'])

    def test_pipeline_approval_token(self):
        with Stubber(handler.client) as stubber:
            stubber.add_response('get_pipeline_state', get_pipeline_state_response, {'name': 'test-pipeline'})

            token = handler.pipeline_approval_token('test-pipeline')
            self.assertEqual(token, '69628e7e-d309-4a6a-b01d-9f1aeca2060d')

    def test_pipeline_failed_msg(self):
        msg = handler.main(pipeline_failed_event, {})
        self.assertEqual(msg['title'], 'Pipeline action "Build" failed')


if __name__ == '__main__':
    unittest.main()
