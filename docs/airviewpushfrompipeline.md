# Populating events from pipeline checks

The purpose is to surfacing security checks and their results that occur during a pipeline run to airview.
E.g. Are there any vulnerable libraries, any policy-as-code failures, etc.

There are currently two POCs demonstrating two different methods of pushing pipeline checks to AirView.
1. Directly, via installing the AirView client and invoking it from the pipeline. Done in ADO.
2. Via a webhook after the event, and intermediary transformation to a Lambda. Done in Github.

Both of these methods are in POC, (read broken) state.

## Direct from ADO to AirView

The repo - https://dev.azure.com/mdrnwrk-ado/airview/_git/demo-pipeline-data
The pipeline -  https://dev.azure.com/mdrnwrk-ado/airview/_git/demo-pipeline-data
The transformation script - https://dev.azure.com/mdrnwrk-ado/airview/_git/demo-pipeline-data?path=/_scripts/airview_push.py

This method uses a "baked" in outdated airview client and utilises a custom script to invoke the airview client directly from the pipeline.

Improvements
- [ ] Install the airview client (via pip/requirements) instead of "packaging" it internally
- [ ] RBAC (?)

## Github Actions webhook to API Gateway/Lambda transformation to AirView

The transformation lambda - https://github.com/AirWalk-Digital/airview-sdlc-notifier/blob/main/airview_sdlc_notifier/main.py
The example repo with the github actions/pipeline - https://github.com/AirWalk-Digital/DevSecOps-terraform-example/tree/main/.github/workflows

Each time a Github Action is triggered, a webhook is triggered that will send the event to an API Gateway. The API Gateway will invoke a lambda that will transform the event (map the fields, enhance, etc.)
and send it to AirView.

Improvements
- [ ] Install the airview client (via pip/requirements) instead of "packaging" it internally
- [ ] RBAC (?)
