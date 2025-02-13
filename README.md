# tweeti-kiri
Your Social Media Vacuum Cleaner. Python application to help with housekeeping on Twitter.

## Screenshot
![image](https://raw.githubusercontent.com/HackerspaceBremen/tweeti-kiri/master/screenshot_tweeti_kiri_v1_2.png)

## Features
The program runs on the command line and provides an **interactive** way of requesting userinput to be setup and configured. Every action can be chosen individually and will only be executed after user confirmation.

Following features are provided by this application:

* Configure and store authorization credentials
* Analyze your own and any other twitter account
* Remove **all** tweets
* Remove **all** direct messages
* Remove **all** favourites
* Remove **all** retweets
* Remove **all** followers (not yet implemented!)
* Remove **all** friends/following (not yet implemented!)
* Clear any configured authorization credentials

## Installation (Python 3)

Ensure you have installed Python 3. (You could use `brew` to install Python 3 just by entering `brew install python3` ) If you have it installed just create a virtual environment using  

### 1. Setup virtual environment

```
$ cd $(WHAT_EVER_YOUR_FORK_PATH_IS)
$ python3 -m venv tweeti-kiri
``` 
this creates a folder with the virtual environment.

This will create the directory `~/tweeti-kiri/` under your home directory.

If you want to create this environment on another place just name it: 
`python3 -m venv ~/Developer/Python/tweeti-kiri`. This will setup your virtual environment on the given path. All missing directories are created automatically. **For this example we will use `~/tweeti-kiri/`**.


### 2. Activate your virtual environment
To activate this new environment just type these two commands:  

```
$ cd ~/tweeti-kiri/
source bin/activate
```
 
### 3. Setup your virtual environment
Now you have to copy the `tweeti_kiri.py` file from this repository into your new virtual environment:  

```
$ cp $(WHAT_EVER_YOUR_FORK_PATH_IS)/tweeti_kiri.py .
$ cp $(WHAT_EVER_YOUR_FORK_PATH_IS)/requirements.txt .
```

For making `tweeti_kiri.py` to run as expected we need to install some additional Python modules which are found in the `requirements.txt` file. These modules will be installed in our activated virtual environment:  

```
# The setup process needs to be adjusted a little for todays Python setup

$ python3 -m pip install --upgrade pip
$ pip3 install "setuptools<58.0.0"
$ pip3 install -r requirements.txt
```

### 4. Prepare for usage
After you installed the necessary Python modules to make the program work you need to create an app-authorization-entry in your twitter profile and afterwards configure the Python program with several credentials.

Please follow the description below in **Configure twitter App & API Keys**.

### 5. Launch
```
$ python3 tweeti-kiri.py
```

You should see something similar to the screenshot above.

## Configure twitter App & API Keys
Just follow this step by step description:

1. To be able to remove **all** tweets from your account you first need to get **Your Twitter archive**. This is necessary since we use the included Tweet-IDs being able to remove **all** tweets! You can do this by going to your [Twitter Account Settings](https://twitter.com/settings/account) (Twitter → Top Right Avatar → Settings → Account (left navigation)). Below on that page you will find a button named **Request your archive**. Click it. Twitter will send you an email if the archive is ready for download.
2. Now navigate to [https://apps.twitter.com/](https://apps.twitter.com/) and create a new application. You can name the application e.g. **tweeti-kiri-$myTwitterNickname** because this name has to be unique worldwide. Be aware that for setting up this application you need to add a mobile phone number to your account before this will succeed. You can remove that number after the app was successfully created.  
If you haven't already done it, please [configure your mobile number here](https://twitter.com/settings/devices).
3. When setting up the User authentication settings for your Twitter app, select "Read and write and Direct message" under _App Permissions_ and Web App, "Automated App or Bot" under _Type of App_. Under _App info_, the settings can be neglegted, but some are reqiured. Just enter any URL you'd like (e.g. https://delete-twitter.io/auth) for the "Callback URI / Redirect URL" and the base URL as "Website URL" (e.g. https://delete-twitter.io). Save the changes and copy the Client ID and Client Secret.
4. In the _Keys and Tokens_ section of your app, under _Authentication Tokens_, select "Generate" in the _Access Token and Secret_ section, and copy the "Access Token" and "Access Token Secret". These are the values needed for the tweeti-kiri config.
5. Note down the **consumer key** and the **consumer secret** the new app provides to you.
6. Authorize your app to access your own account and change permissions to also give it access to direct messages. Then request the creation of the **access token key & access token secret** and note them down, too.
7. Within the developper portal, select _Twitter API v2_ in the menu on the left and go to _Elevated_ on the top. You need to "apply" for elevated API access in order to be able to actually work with it. Just fill out the form and wait a little until access gets approved.
8. By this time Twitter should have mailed a link to you with your Twitter-archive as a **ZIP** file. Give this file a meaningful name like e.g. `tweet_archive_$yourNick_2016.zip` and copy it to your virtual environment `~/tweeti-kiri/` directory.
9. Now, from within your virtual environment, you can launch the program by typing `python tweeti_kiri.py`
from the command line and start with `ACTION 1` to configure your account & credentials.
10. As _Consumer Key_ enter the API key from the Twitter app settings. _Consumer Secret_ should be the _API Key Secret_. _Access Token Key and Secret_ should also be copied from the app settings before.
11. **DONE!** You are now ready to do some housekeeping with your account.
12. If you want to work with different twitter accounts, you need to repeat the procedure of configuration with each of these accounts. You can make a simple backup of the **configuration.cfg** which is created for each successful configuration if you want to keep that somewhere safe for later use.


## Installation (under Python 2.x only)
Before starting the installation, make sure you have `python`, `pip` and `virtualenv` installed.  
On macOS `python` should be installed by default and its setup tool `easy_install`, too. If you are missing `pip` and/or `virtualenv` it's very straight forward to install it. First you should setup `pip`:

```
sudo easy_install pip
```

The next step is to install the virtualenv package:
```
sudo -H pip install virtualenv
```

## Usage

### Last Release (Legacy)
<span style="color:red;">**IMPORTENT:**</span> The most recent release needs to update the `python-twitter` module to the latest version `python-twitter (3.3)`. You can use *pip-review* to upgrade outdated modules. Just install it using `pip install pip-review` then type the following:

```
$ pip install pip-review
```

```
$ pip-review --local --interactive
```


### 1. Create your virtual environment
```
virtualenv tweeti-kiri
```
This will create the directory `~/tweeti-kiri/` under your home directory.

If you want to create this environment on another place just name it: 
`virtualenv ~/Developer/Python/tweeti-kiri`. This will setup your virtual environment on the given path. All missing directories are created automatically. **For this example we will use `~/tweeti-kiri/`**.


### 2. Activate your virtual environment
To activate this new environment just type these two commands:
```
cd ~/tweeti-kiri/
source bin/activate
```

 
### 3. Setup your virtual environment
Now you have to copy the `tweeti_kiri.py` file from this repository into your new virtual environment:
```
cp $(WHAT_EVER_YOUR_FORK_PATH_IS)/tweeti_kiri.py .
```

For making `tweeti_kiri.py` to run as expected we need to install two additional Python modules, `anyjson` and `python-twitter`. These modules will be installed in our activated virtual environment:
```
pip install anyjson
pip install python-twitter
```

### 4. Prepare for usage
After you installed the necessary Python modules to make the program work you need to create an app-authorization-entry in your twitter profile and afterwards configure the Python program with several credentials.

Please follow the description in **Configure twitter App & API Keys**.

## Versions
* Version 0.9 (12. April 2016)
* Version 0.91 (13. September 2016)
* Version 0.92 (13. September 2016)
* Version 1.0 (25. May 2017)
* Version 1.1 (26. May 2017)
* Version 1.2 (8. June 2019)

## Contact
Helpful hints for improving this piece of code can be transmitted to [trailblazr@hackerspace-bremen.de](mailto:trailblazr@hackerspace-bremen.de) or via Twitter to [@hspacehb](http://twitter.com/@hspacehb) the Twitter-Account of [Hackerspace Bremen](https://www.hackerspace-bremen.de/).

## Kudos
Many thanks go to [Mario Vilas](https://github.com/MarioVilas) for providing a really [useful piece of code](https://breakingcode.wordpress.com/2016/04/04/how-to-clean-up-your-twitter-account/) to start wrapping your head around. Thanks go also to the people maintaining the python-twitter module. Awesome piece of work without which this script won't be existing!

I also thank all the beta testers of the code and all the visitors at the presentation at [Hackerspace Bremen](https://www.hackerspace-bremen.de) which posed some good questions during the [presentation (slides as PDF)](https://raw.githubusercontent.com/HackerspaceBremen/tweeti-kiri/master/tweeti_kiri_presentation_april_2016.pdf).

## License
This code is licensed under the GPLv3 License.

## Alternatives
There do exist several other solutions to the problem of housekeeping with twitter accounts. One of the most convenient solutions I have seen recently is the tool [semipheral](https://github.com/micahflee/semiphemeral) which offers a convenient way to manage your tweets in a way that you can do cleanup but also keep the most valuable tweets (defined by a ruleset you configure).

The special way tweeti-kiri operates on the twitter archives only, allows to also delete tweets which are way back in the past. If you have more than 3000 tweets you won't even be able to delete them via twitters' official website. Using the archive gives you a way to delete even 100.000 tweets back into the past.
