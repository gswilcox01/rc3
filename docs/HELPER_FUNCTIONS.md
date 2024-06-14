# Helper Functions
* Helper functions are similar to env var substitution, in that they use handlebar expressions that get replaced in your template
* A simple example is the #uuid helper function, which replaces the expression with a UUID
  * {{ #uuid }}
* Any handlebar expression in your template that begins with a "#" must match a pre-defined helper function, otherwise rc will abend with an error message
* See each section below for additional documentation & examples for each helper function

## #uuid helper function
* This helper function will be replaced with a newly generated UUID
* An optional parameter can trigger ALSO saving this UUID into an environment var
  * By default the env var will be saved into the global env
  * You may also prefix the env var with "global." or "current." to save in a different env
* An example using this in an Oauth2 flow for state & nonce query parameters:
  ```
  "params": {
    "nonce": "{{ #uuid global.nonce }}",
    "state": "{{ #uuid global.state }}",
  },
  ```

## #pkce_cvcc helper function
* This helper function generates an oauth2 PKCE code_verifier & code_challenge using the SHA256 method
  * The code_verifier is saved into an env var
  * The code_challenge replaces the handlebar expression in your template
* An optional parameter can be passed to save the code_verifier in a specific env var
  * If no parameter is passed the code_verifier will be stored in the global env in an env var named code_verifier 
  * By default the env var will be saved into the global env
  * You may also prefix the env var with "global." or "current." to save in a different env
* An example using this in an Oauth2 PKCE flow query parameters:
  ```
  "params": {
    "code_challenge": "{{ #pkce_cvcc global.cv }}",
    "code_challenge_method": "S256"
    "response_type": "code"
  },
  ```

## #prompt helper function
* This helper function will be replaced with a response entered by the user
* A required parameter is the prompt to display to the user
* The prompt may optionally be suffixed with a default value to suggest to the user
  * To use this feature suffix your prompt with a ":" and the default value
  * See the example below which uses this default value option
* An example of using this to collect 2 inputs from a user before sending a request
  ```
  "params": {
    "page_num": "{{ #prompt Which page of audit records:0 }}",
    "page_size": "{{ #prompt How many audit records per page:10 }}"
  },
  ```

## #file helper function
* This helper function will be replaced with the contents of a file passed to rc with the --file option
* Normally the "--file" option replaces/overrides the entire BODY sent with your request
* With this helper function you can:
  * Still replace the entire body, but REQUIRE that the --file option is always used with the .request
  * Or, just replace a portion of the JSON body defined in your .request file
* An example replacing the entire BODY still, but requiring the --file option be used with "rc send":
  ```
  "body": {
    "json": "{{ #file }}"
  }
  ```
* An example replacing just a portion of the JSON body defined in your .request:
  ```
  "body": {
    "json":  {
      "main": "{{ #file }}",
      "additional" : {
        "property1": "abc",
        "property2": "def"
      }
    }
  }
  ```
