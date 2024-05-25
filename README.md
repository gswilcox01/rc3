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

## Installation & Upgrade
* Pre-reqs
    * Python 3.12+ (required)
    * VSCode (optional, but highly recommended)
* Install
    * pip install rc3
* Upgrade
    * pip install --upgrade rc3
* Windows User?
    * See:  [Windows Setup Issues](WINDOWS_SETUP.md)

## Setup & Send your first request
* First create an empty directory somewhere (any name & location is fine)
  ```
  $ mkdir temp-collection
  $ cd temp-collection
  ```
* Next run "rc new" to create a new collection
  * Choose all default values, and you'll get an example collection you can explore
  ```
  $ rc new
  Enter a NAME for this COLLECTION [temp-collection]:
  Include example Requests in your new collection? [Y/n]:
  Importing collection into RC_HOME/rc-settings.json
  Collection 'temp-collection' has been successfully imported, try 'rc list' next...
  ```
* Next run "rc list" to see what's in the example collection you just created
  ```
  $ rc list
  Listing COLLECTIONS found in settings.json:
  NUM:   NAME:             LOCATION:                             
  1      example-rc        C:\git\example-rc
  2*     temp-collection   C:\temp-collection
  Listing ENVIRONMENTS found in current_collection:
  NUM:   NAME:       baseUrl:
  1*     dev         https://greetings-mvrsygo3gq-uc.a.run.app
  2      localhost   http://localhost:8080
  Listing REQUESTS found in current_collection:
  NUM:   FOLDER:             METHOD:   NAME:
  1*     /greetings-basic    GET       greeting
  2      /greetings-basic    GET       greetings
  3      /greetings-basic    POST      new-greeting
  4      /greetings-basic    DELETE    remove-greeting
  5      /greetings-basic    PUT       update-greeting
  6      /greetings-oauth2   GET       greeting
  7      /greetings-oauth2   POST      mint-admin-token
  8      /greetings-oauth2   POST      mint-token
  ```
* Next send the "greeting" request with the rc send command
  * Wait for it…
    * A greetings-demo project is running on Google Cloud Run
    * And it scales down to 0 instances when there is no demand (i.e. your first few requests will be SLOW…)  
  ```
  $ rc send greeting
  {                        
      "id": 1,             
      "text": "Hello",     
      "language": "English"
  }
  ```
* Next "cat" the generated greeting.response file that will have more verbose output from the send command
  ```
  $ cat greetings-basic/greeting.response
  {                                                                                     
    "status_code": 200,                                                               
    "time": "845.772ms",                                                              
    "size": {                                                                         
        "body": 44,                                                                   
        "headers": 442,                                                               
        "total": 486                                                                  
    },                                                                                
    "headers": {                                                                      
        "vary": "Origin,Access-Control-Request-Method,Access-Control-Request-Headers",
        "Date": "Wed, 08 May 2024 15:06:54 GMT",                                      
        "Server": "Google Frontend",
  
    ...
                                                    
  }
  ``` 

## Sending more requests from the example collection
* All the requests in the example collection can be sent to the greetings-demo app running on Google Cloud Run
* To view all requests in the example collection run "rc request --list"
  ```
  $ rc request --list
  Listing REQUESTS found in current_collection:
  NUM:   FOLDER:             METHOD:  NAME:              
  1*     /greetings-basic    GET      greeting
  2      /greetings-basic    GET      greetings
  3      /greetings-basic    POST     new-greeting
  4      /greetings-basic    DELETE   remove-greeting
  5      /greetings-basic    PUT      update-greeting
  6      /greetings-oauth2   GET      greeting
  7      /greetings-oauth2   POST     mint-admin-token
  8      /greetings-oauth2   POST     mint-token
  ```
* Try sending requests by NUMBER instead of by NAME using these commands:
  ```
  $ rc send 1
  $ rc send 2
  $ rc send 3
  ```
* Notes:
  * Make sure there is a greeting #8 before sending request 4, or you'll get a 404
  * Make sure you run request 7, before request 6, so you have a {{ token }} available in your global environment

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
## Import an existing collection from a git repo
* The example collection you created with the "rc new" command is also checked into a git repository here:
* https://github.com/gswilcox01/example-rc
* You can clone & import collections following the example below:
  ```
  $ git clone https://github.com/gswilcox01/example-rc.git
  Cloning into 'example-rc'...
  remote: Enumerating objects: 33, done.
  remote: Counting objects: 100% (33/33), done.
  remote: Compressing objects: 100% (17/17), done.
  remote: Total 33 (delta 14), reused 33 (delta 14), pack-reused 0
  Receiving objects: 100% (33/33), 4.87 KiB | 262.00 KiB/s, done.
  Resolving deltas: 100% (14/14), done.
  
  $ cd example-rc 
  
  $ rc import
  Importing collection into RC_HOME/rc-settings.json
  Collection 'example-rc' has been successfully imported, try 'rc list' next...
  ```

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
* You can set a custom cert ca_bundle file in RC_HOME/settings.json with:
  * "ca_bundle": "/path/to/ca/bundlefile",
* You can alternatively set the path to a ca_bundle file with one of these ENV VARS:
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
				
