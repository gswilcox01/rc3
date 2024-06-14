# Additional Commands
This page documents some additional commands that didn't make sense to add to the main README/getting started document.

## rc upgrade
* This command is meant to upgrade your rc collection files created with a prior release of rc to the latest format/schemas.
* It is a work in progress, and currently does the following 3 things:
  * Updates $schema in RC_HOME, settings & global-env
  * Updates examples in the current collection if there are any changes in the reference/example collection
  * Updates $schema in your current collection if there are new schemas (applies to requests, folders, collection, environments)
* You will be prompted/must confirm YES before each upgrade step is done
* Example output from a collection that has no upgrades possible:
  ```
  $ rc upgrade
  Checking for possible upgrades...
  Checking RC_HOME schemas... OK
  Checking current COLLECTION examples... OK
  Checking current COLLECTION schemas... OK
  Checking current COLLECTION REQUEST extract JSON... NOT IMPLEMENTED YET
  Checking current COLLECTION validating JSON against current schemas... NOT IMPLEMENTED YET
  ```

## rc decode
* This is a simple command that will decode a JWT in an environment & display the results
* By default it will attempt to decode an env var named "token"
* An optional JWT_ENV_VAR argument may be passed if you have a different env var to decode
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
