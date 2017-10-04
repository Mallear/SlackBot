# SlackBot

Code source base for a SlackBot, taken from [slack-starterbot project by MattMakai](https://www.fullstackpython.com/blog/build-first-slack-bot-python.html).

## Getting Started

* Create a slack bot via Slack web interface
* Add the API token in the script
* Install dependencies
* Launch
OR
* Build and deploy the container

## Technical Details

Technical stack :
* Python3
* SlackClient for Python (explained in MattMakai tuto, see above)

Docker containers build inside of the compose file, juste launch `docker-compose up -d` to build and deploy

# Reading

More about slack bot & slack apps on [Kim Mok blog article](https://tutorials.botsfloor.com/slack-app-or-bot-user-integration-842c3843eea8).

Tutorial on Slack botting in containers with NodeJS and BotKit on [Los Techies](https://lostechies.com/andrewsiemer/2016/04/14/building-a-slack-bot-with-botkit-node-and-docker/).

