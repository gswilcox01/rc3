# Additional Commands
This page documents some additional commands that didn't make sense to add to the main README/getting started document.

## rc upgrade
* This command is meant to upgrade your rc collection files created with a prior release of rc to the latest format/schemas.
* It is a work in progress, and currently does the following 3 things:
  * Updates $schema in RC_HOME, settings & global-env
  * Updates examples in the current collection if there are any changes in the reference/example collection
  * Updates $schema in your current collection if there are new schemas (applies to requests, folders, collection, environments)
* You will be prompted/must confirm YES before each upgrade step is done
* Example output from a collection that had 1 example request out of date:
  ```
  $ rc upgrade
  Checking for possible upgrades...
  Checking RC_HOME schemas... OK
  Checking current COLLECTION examples... UPGRADES NEEDED
  Example folder has 1 out-of-date examples, 0 missing examples...
  Would you like to create/update current COLLECTION examples [Y/n]:
  Updating current COLLECTION examples... SUCCESS
  Checking current COLLECTION schemas... OK
  Checking current COLLECTION REQUEST extract JSON... NOT IMPLEMENTED YET
  Checking current COLLECTION validating JSON against current schemas... NOT IMPLEMENTED YET
  ```
## rc decode
* This is a simple command that will decode a JWT in an environment (or keyring) & display the results
* By default it will attempt to decode a var named "token" (which exists in an env or keyring)
* An optional JWT_VAR argument may be passed if you have a different var name to decode
* An example:
  ```
  $ rc decode
  Decoding HEADERS and CLAIMS from 'token' env var
  {
      "kid": "b929b10c-2473-45cb-95f2-511884389459",
      "alg": "RS256"
  }
  {
      "sub": "greetings-admin",
      "aud": "greetings-admin",
      "nbf": 1718321183,
      "scope": [
          "greetings.write"
      ],
      "iss": "http://greetings-mvrsygo3gq-uc.a.run.app",
      "exp": 1718324783,
      "iat": 1718321183,
      "jti": "2f54dc4b-9f48-4965-a90d-074b4928016f"
  }
  Issued at:  Thu Jun 13 18:26:23 2024
  Curr time:  Thu Jun 13 18:26:36 2024
  Expires at: Thu Jun 13 19:26:23 2024
  ```
## rc keyring
* This is a simple command that will GET, SET, or DELETE values in your operating system keyring
* By default this is the macOs Keychain, or Windows Credential Locker
* Other keyrings/backends are available, but YMMV, see: https://github.com/jaraco/keyring
* An example setting a value for the name "password":
  ```
  $ rc keyring --set password
  Please enter a value for NAME(password):
  ```
* An example inspecting a value for the name "password" (Note: you won't normally do this unless you want to double-check what value you have stored in the keyring):
  ```
  $ rc keyring --get password
  pass
  ```
* By default, env var substitution checks the following locations in this order 1. Current env, 2. Global env, 3. Shell env, 4. Keyring.
* So, keyring values will automatically be found/replaced in mustache/handlebar expressions, AS LONG as there is not an env var with the same name.
* An example using a keyring NVP based on this default handling:
  ```
  {
    "password": "{{ password }}"
  }
  ```
* An example using a keyring NVP only (and NOT checking env vars first):
  ```
  {
    "password": "{{ #keyring password }}"
  }
  ```