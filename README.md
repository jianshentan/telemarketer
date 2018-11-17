# Telemarketers Save Thanksgiving

## Getting Started

This application depends on Twilio to automate voice calls. To begin, make sure you have proper authentication methods for Twilio. This includes having an twilio SID and auth token.

This application is also deployed using Docker, so make sure that you have Docker installed.

I would also recommend using some kind of virtual env (conda or pyenv).

### Testing the application locally
1. Copy __template.env__ from the root directory to __.env__ and fill out the environment variables
2. Run `source .env` to load the environment variables into your session
3. `cd` into the __app__ directory and run `python3 app.py` to run your session. This should load the website on localhost:9001

### (re)deployment
0. Backup any changes you've made to github.
1. Build your docker container: `docker build -t telemarketer`
2. `docker tag brandnewroman <username>/telemarketer`
3. `docker push <username>/telemarketer`
4. Go to Azure portal and restart
