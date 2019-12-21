# docker-builder

## ENV
* K8SINFRA_URL : kubernetes infra server address.
* GCLOUD_AUTH_KEY : gcloud account json key.
* GCLOUD_REGISTRY_HOST : gcloud registry host url (default : asia.gcr.io)
* GCLOUD_PROJECT_ID : gcloud project id for registrty

## API
| URI | METHOD | Description |
| --- | ------ | ----------- |
| /repo | POST | add docker build work |
| /repo/<repo_title> | PUT | update docker build work information | 
| /repo/<repo_title> | GET | get docker build work information |
| /hook/<repo_title> | POST | event hook for docker build work |

## /repo
json format body with this key
* title : build work identifier
* url : github repository url
* token(optional) : access token for github repository
* branch : branch name for target

## /hook/<repo_title>
github webhook url for event monitoring.