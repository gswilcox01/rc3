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
    * Will send the first request named "greeting" in the example Collection
    * Wait for it…  
      * A greetings-demo project is running on Google Cloud Run
      * And it scales down to 0 instances when there is no demand (i.e. your first few requests will be SLOW…)
* cat greetings-basic/greeting.response
    * Will show more verbose output from the "rc send greeting" cmd you just sent

## Sending more requests from the example collection
* All the requests in the example collection can be sent to the greetings-demo app
  ```
  Listing REQUESTS found in current_collection:
  NUM:   FOLDER:             MET:     NAME:              
  1*     /greetings-basic    GET      greeting
  2      /greetings-basic    GET      greetings
  3      /greetings-basic    POST     new-greeting
  4      /greetings-basic    DELETE   remove-greeting
  5      /greetings-basic    PUT      update-greeting
  6      /greetings-oauth2   GET      greeting
  7      /greetings-oauth2   POST     mint-admin-token
  8      /greetings-oauth2   POST     mint-token
  ```
* For example:
    * rc send 1
    * rc send 2
    * rc send 3
* Notes:
  * Make sure there is a greeting #8 before sending request 4, or you'll get a 404
  * Make sure you run request 7, before request 6, so you have an access_token

## More command examples
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
* Authentication can be defined in a Request, Folder, or in the collection.json file in the root of your collection
* Inheritance is walked until auth is defined, or the root of the collection is found in this order:
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

## Extracting values from a response:
* You can extract a value from any response and save it into the current or global Environment
* You can extract with either of:
  1. JsonPath (preferred)
  2. Python Regex
* For an example of each see the following files in the example collection:
  * /examples/example_Extract_JsonPath.request
  * /examples/example_Extract_Regex.request
  * /greetings-oauth2/mint-admin-token.request
* All the examples above:
  * Extract a top level "access_token" node from a JSON response
  * And save the value in a variable named "token" in the "global" environment
* Read more about Json Path here:
  * https://www.digitalocean.com/community/tutorials/python-jsonpath-examples
  * https://www.baeldung.com/guide-to-jayway-jsonpath
  * https://jsonpath.com/
* Read more about Python Regex here:
  * https://docs.python.org/3/howto/regex.html

## Settings:
* Settings are only documented in the default settings.json file & the settings schema
* See: https://json.schemastore.org/rc3-settings-0.0.3.json
* Or after running "rc init" see:
  * RC_HOME/settings.json
  * RC_HOME/schemas/rc3-settings-0.0.3.json

## Proxies:
* rc leverages Python Requests defaults which honors these ENV VARS for proxy settings:
  * HTTP_PROXY
  * HTTPS_PROXY
  * NO_PROXY
  * ALL_PROXY
* NO_PROXY/Proxy Bypass:
  * Note:  IP addresses are not allowed/honored, and hostnames must be used
  * See: https://github.com/psf/requests/issues/4871
* See more info about Python Requests Proxies here:
  * https://requests.readthedocs.io/en/latest/user/advanced/#proxies

## CA certificates:
* By default rc will follow Python Requests default behaviour
  * Using the Python 'certifi' module truststore file
  * And verifying certs
* You can turn off cert verification in RC_HOME/settings.json with:
  * "ca_cert_verification": false,
* You can set a custom cert ca_bundle file with:
  * "ca_bundle": "/path/to/ca/bundlefile",
* You can alternativelly set the path to a ca_bundle file with one of these ENV VARS:
  * REQUESTS_CA_BUNDLE
  * CURL_CA_BUNDLE
* For more details see:
  * https://requests.readthedocs.io/en/latest/user/advanced/#ssl-cert-verification

## VSCode setup:
* Associate *.request & *.response files with the JSON editor
  * Open a file that needs mapping
  * CTRL + SHIFT + P
  * Choose "Change Language Mode"
  * Choose "Configure File Association for '.extension'"
  * Choose "JSON" from the list
				
