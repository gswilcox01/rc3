# Helper Functions
* Helper functions are similar to env var substitution, in that they use handlebar expressions that get replaced in your template
* A simple example is the #uuid helper function, which replaces the expression with a UUID
  * {{ #uuid }}
* Any handlebar expression in your template that begins with a "#" must match a pre-defined helper function, otherwise rc will abend with an error message
* See each section below for additional documentation & examples for each helper function

## #uuid helper function
* This helper function will be replaced with a newly generated UUID
* An optional parameter can trigger ALSO saving this UUID into an environment var or keyring
  * By default the env var will be saved into the global env
* You may optionally prefix the var name with "global.", "current." or "keyring."
  * "global.nonce" will also save the value in the global env, in a var named "nonce"
  * "current.nonce" will also save the value in the current env, in a var named "nonce"
  * "keyring.nonce" will also save the value in your OS Keyring, in a var named "nonce"
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
  * By default the env var will be saved into the global env, in a var named "code_verifier"
* You may optionally pass a parameter to store the code_verifier in a specific env
  * "global.cv" will save the value in the global env, in a var named "cv"
  * "current.cv" will save the value in the current env, in a var named "cv"
  * "keyring.cv" will save the value in your OS Keyring, in a var named "cv"
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

## #secure_prompt helper function
* This helper function will be replaced with a response entered by the user
* This helper function is the same as the #prompt helper function, EXCEPT the user input is hidden on the terminal when entered
* An example of using this to collect a password
  ```
  "auth": {
    "type": "basic",
    "username": "{{ #prompt username }}",
    "password": "{{ #secure_prompt password }}",
  },
  ```

## #keyring helper function
* This helper function will be replaced with a value from your OS keyring (Keychain, or Windows Cred Locker)
* A required parameter is the NAME to read from your OS keyring
* An example where both a lan_username and lan_password have been stored in your OS keyring
  ```
  "auth": {
    "type": "basic",
    "username": "{{ #keyring lan_username }}",
    "password": "{{ #keyring lan_password }}",
  },
  ```

## #keyring_prompt helper function
* This helper function will be replaced with a value from your OS keyring (Keychain, or Windows Cred Locker)
* A required parameter is the NAME to read from your OS keyring
* This helper function is very similar to the "keyring" helper, except:
    * If the NAME does not exist in your keyring, you will be prompted for the value
    * The provided value will be used for this request AND stored in your keyring for future requests
* An example where a lan_password might be stored in your OS keyring
  ```
  "auth": {
    "type": "basic",
    "username": "gary",
    "password": "{{ #keyring_prompt lan_password }}",
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
