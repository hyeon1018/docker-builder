# docker-builder

## API
| URI | METHOD | Description |
| --- | ------ | ----------- |
| /repo | POST | add docker build work |
| /repo/<repo_title> | GET | get docker build work information | 
| /hook/<repo_title> | POST | event hook for docker build work |


## /repo
json format body with this key
* title : build work identifier
* url : github repository url
* token : access token for github repository
* branch : branch name for target

## /hook/<repo_title>
github webhook url for event monitoring.