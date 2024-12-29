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
rc is installed as a Python script.  The instructions below should work fine for most users.  Please reach out if they don't.
The MacOS instructions leverage "pipx" to install in a Python virtualenv instead of with your system Python modules. 

If you'd like to install with "pipx" in Windows that works fine as well, but is not documented here.  See: https://github.com/pypa/pipx
* Pre-reqs
    * Python 3.12+ (required)
    * VSCode (optional, but highly recommended)
* Windows:
    * Install  
      * pip install rc3
    * Upgrade
      * pip install --upgrade rc3
    * Windows Troubleshooting
      * See:  [Windows Setup Issues](docs/WINDOWS_SETUP.md)
* MacOS
    * Pre-reqs 
      * brew install python
      * brew install pipx
      * pipx ensurepath
    * Install
      * pipx install rc3
    * Upgrade
      * pipx upgrade rc3

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

## Working with files
* A common pattern might be to:
  * save a GET response
  * edit the JSON/response locally
  * then PUT/POST back to save or create a new record
* The "--file" option on the "rc send" command supports this flow
  * When the "--file" option is used you must pass a filename with the option
  * The contents of that filename will be used as the BODY of the request (overriding what's in the .request template)
* An example below using the example collection; uses a GET response as a template for a new POST request.
  ```
  $ rc send greeting > my.json
  $ vi my.json
  $ rc send new-greeting --file my.json 
  {
  "id": 6,
  "text": "Koar",
  "language": "Martian"
  }
  ```
* The "--file" option follows the convention of a "-" character for the filename represents STDIN
* Using this feature you can pipe the output of 1 request into another, example below
  ```
  $ rc send greeting | rc send new-greeting --file -
  {
      "id": 7,
      "text": "Hello",
      "language": "English"
  }
  ```
* If you wish to have file contents just override a portion of your .request template & not replace the entire BODY
  * see the #file helper function in the additional help document [Helper Functions](docs/HELPER_FUNCTIONS.md)

## Additional Commands
* For documentation on some more niche CLI commands See: [Additional Commands](docs/ADDITIONAL.md)
  * rc upgrade --- upgrades schemas & files in your collection
  * rc decode --- decodes/displays JWTs in your environment
  * rc keyring --- get/set/delete values in your OS keyring (Keychain, or Win Cred Locker)

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
  4. Keyring values (MacOS Keychain, Windows Cred Locker)
     * For more info see "keyring" command here: [Additional Commands](docs/ADDITIONAL.md)
* For examples of variable placeholders, see the following files in the example collection:
    * /greetings-basic/rc-folder.json
    * /greetings-oauth2/mint-admin-token.request

## Helper Functions
* Helper functions are similar to env var substitution, in that they use handlebar expressions that get replaced in your template
* A simple example is the #uuid helper function, which replaces the expression with a UUID
    * {{ #uuid }} 
* For more complete documentation on helper functions see: [Helper Functions](docs/HELPER_FUNCTIONS.md)
  * #uuid --- generates a new Type4 UUID
  * #pkce_cvcc --- generates a PKCE code_verifier & code_challenge
  * #prompt --- will prompt the user for input
  * #secure_prompt --- will prompt the user for input (that is masked on screen)
  * #keyring_prompt --- will read a value from your OS keyring, or secure prompt for a value 
  * #keyring --- will read a value from your OS keyring (Keychain or Win Cred Locker)
  * #file --- will inject '--file' option file contents into just a portion of your template

## Extracting values from a response:
* You can extract a value from any response and save it into the current or global Environment
* You can extract with either of:
  1. JsonPath (preferred)
  2. Python Regex
* For an example of each see the following files in the example collection:
  * /examples/example_Extract_JsonPath.request
  * /examples/example_Extract_Regex.request
* For an example of using multiple extracts on 1 request, and various "to" and "from" options see:
  * /examples/example_KitchenSink.request 
* Extract "from" options:
  * "body" --- will extract from the BODY of the response (this is the default)
  * "response" --- will extract from the verbose output saved to .response file
* Extract "to" options:
  * "current" --- will extract to the currently selected env
  * "global" --- will extract to the global env (this is the default)
  * "stdout" --- will replace the normal stdout, to just the extracted value(s)
  * "response" --- will extract to the verbose .response file that is generated
  * "keyring" --- will extract to your OS Keyring (KeyChain or Windows Cred Locker)
* Read more about Json Path here:
  * https://www.digitalocean.com/community/tutorials/python-jsonpath-examples
  * https://www.baeldung.com/guide-to-jayway-jsonpath
  * https://jsonpath.com/
* Read more about Python Regex here:
  * https://docs.python.org/3/howto/regex.html

## Settings:
* Settings are mostly only documented in the default settings.json file & the settings schema
* See: https://json.schemastore.org/rc3-settings-0.0.3.json
* Or after running "rc" for the first time see:
  * RC_HOME/rc-settings.json

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
				
