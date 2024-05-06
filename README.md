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