# rc
rc = REST CLI  

rc is a tool to help execute REST API requests.  
rc is based on Collections, Environments and Requests.  Similar to the tool we all love/hate --- Postman.  

## Overview
* A Collection is a local directory (optionally checked in as a git repository somewhere).
* A Collection contains *.request files that each represent a single REST API Request that can be executed
* The output from executing a *.request file is normally:
    * The HTTP response body to standard out
    * A detailed *.response file saved in the same directory as the *.request file sent

## Installation
* Pre-reqs
    * Python 3.12+ (required)
    * VSCode (optional, but highly recommended)
* Install
    * pip install rc3

## RC Setup & Sending your first request
* mkdir example-collection
* cd example-collection
* rc init
    * Will do 0-4 things
      1. Will create the RC_HOME directory if it doesn't exist.
      2. Will create RC_HOME/settings, global env, and schemas dir if they don't exist.
      3. Will initialize a new example Collection if ran from an empty directory.
      4. Will import the current directory if it contains a valid collection.json file.
* rc send greeting
    * Will send the first request named "greeting" in your collection
    * Wait for it…  
      * A greetings-demo project is running on Google Cloud Run
      * And it scales down to 0 instances when there is no demand (i.e. your first request will be SLOW…)
* cat greetings-basic/greeting.response
    * Will show more verbose output from the "rc send greeting" cmd you just sent

## More examples
* View all Collections, Environments, and Requests you have setup on this machine
    * rc list
* View all Requests for the current Collection (the following commands are equivalent):
    * rc list requests
    * rc list r
    * rc r
* Pick a new active request in the current collection (the following commands are equivalent):
    * rc request --pick new-greeting
    * rc request --pick 3
    * rc request 3
    * rc r 3
* View the definition of the active request:
    * rc request --info
    * rc r --info
    * rc r -i
* Send the current request (what you just picked)
    * rc send
* Edit the current request & send it UPON file close
    * rc send --edit
* Pick a new current request from a list & send it immediately
    * rc send --pick
* Pick a new current request (WITHOUT a list/prompt) & send it immediately
    * rc send --pick 7

## Viewing help
* View overall help and a list of all available sub-commands
    * rc
* View help for specific sub-commands
    * rc request --help
    * rc collection --help
    * rc environment --help

## Additional Concepts
## Authentication
* Authentication can be defined in a Request, Folder, our in the collection.json file in the root of your collection
* Inheritance is walked until auth is defined, or the root of the collection is found
    * request > folder > parent folder > collection.json
* For examples of authentication see the following files in the example collection:
    * /greetings-basic/folder.json
    * /greetings-basic/greeting.request
    * /greetings-oauth2/mint-admin-token.request
    * /examples/example_Auth_Basic.request
    * /examples/example_Auth_Bearer.request
    * /examples/example_Auth_Token.request 

## Environment Variable substitution
* Similar to postman, env vars in handlebars will be replaced in request files before being sent.
* Example handlebar format:
    * {{ var_name }}
* Environments are searched in the following order for values:
  1. Current environment in collection
  2. Global environment in RC_HOME
  3. SHELL/OS ENVIRONMENT
* For examples of variable placeholders, see the following files in the example collection:
    * /greetings-basic/greeting.request
    * /greetings-oauth2/mint-admin-token.request