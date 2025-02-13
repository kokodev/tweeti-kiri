#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
README / MANUAL

Please look at the bottom of this script to find verbose description
of how to setup and operate this script in a meanigful and safe manner.

Thank you, have fun!
"""

# needed for basic file I/O
import sys, os, traceback, math, re

import anyjson
import zipfile
import twitter
from datetime import datetime

# configuration storage & retrieval
from configparser import ConfigParser
from datetime import date

# APP CONSTANTS
APP_PATH                    = os.path.dirname(os.path.abspath(__file__))
APP_CONFIG_FILE             = 'configuration.cfg'
APP_ESTIMATED_RATE_LIMIT    = 10 # docu says 180 Requests per 15 min (900 seconds) window makes 5 seconds per operation (lets stay with 10 secs per op)
APP_VERSION                 = 'v1.2 (for Python 3)'

# APP CONFIGURATION GLOBAL
APP_CFG_CONSUMER_KEY        = None
APP_CFG_CONSUMER_SECRET     = None
APP_CFG_ACCESS_TOKEN_KEY    = None
APP_CFG_ACCESS_TOKEN_SECRET = None
APP_CFG_TWITTER_NICK        = None
APP_CFG_TWITTER_ARCHIVE     = None

# DEFAULT CONFIG VALUES
APP_DFT_CONSUMER_KEY        = None # e.g. 'UEGC5s9Jk7A3pg1ZvYg4h35Dj'
APP_DFT_CONSUMER_SECRET     = None # e.g. 'OkunqjD6MkQxoxvTjcHayZm3yfq1CgfQM5JRjQYSqKoglMRKzh'
APP_DFT_ACCESS_TOKEN_KEY    = None # e.g. '3401492-cMrxN5eunq9kbeOfY0VtSYGHFwXpkp367gLeCnM26X'
APP_DFT_ACCESS_TOKEN_SECRET = None # e.g. 'Wmqy5GFsaVBlny51ZkZwDwNDRrnDf4hRswk9CIeJR0HhU'
APP_DFT_TWITTER_NICK        = None # e.g. 'tagesschau'
APP_DFT_TWITTER_ARCHIVE     = None # e.g. 'twitter_archiv_tagesschau_2016.zip'

APP_LOGO = """
_____                    __________      ______ _____       _____ 
__  /___      _____________  /___(_)     ___  /____(_)_________(_)
_  __/_ | /| / /  _ \  _ \  __/_  /________  //_/_  /__  ___/_  / 
/ /_ __ |/ |/ //  __/  __/ /_ _  /_/_____/  ,<  _  / _  /   _  /  
\__/ ____/|__/ \___/\___/\__/ /_/        /_/|_| /_/  /_/    /_/   """

# see http://www.kammerl.de/ascii/AsciiSignature.php
# http://patorjk.com/software/taag/#p=display&f=Doom&t=tweeti-kiri%20

global APP_API
APP_API = None

# If you had to interrupt the script, just put the last
# status ID here and it will resume from that point on.
last = 0

def query_yes_no( question, default="yes" ):
    """Ask a yes/no question via input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".
    """
    valid = {"yes": True, "y": True, "ye": True, "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write( question + prompt )
        choice = input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write( "Please respond with 'yes' or 'no' (or 'y' or 'n').\n" )

def read_fake_json( zip, filename ):
    data = zip.open( filename, 'r' ).read()
    # print( "DATA 1: {}".format( data ) )
    data = data.decode("utf-8")
    first_line, data = data.split( '\n', 1 )
    first_line = first_line.split( '=', 1 )[1]
    data = first_line + '\n' + data
    # print( "DATA 2: {}".format( data ) )
    return anyjson.deserialize( data )

def collect_all_tweets(filename):
    zip = zipfile.ZipFile(filename, 'r')
    files = zip.namelist()
    tweets_files = list(filter(lambda x: re.search("\/tweets.*\.js", x), files))

    tweets = []
    for tweets_file in tweets_files:
        print("Collecting tweets from {}".format( tweets_file ))
        tweets += read_fake_json( zip, tweets_file )
    zip.close()
    return tweets
    
def tweets_extract_ids_from_zipfile( filename, tweets_year, tweets_month ):
    print( "ZIPFILE, parsing now: {}".format( filename ) )
    tweet_ids = {}
    tweet_counter = 0
    tweets = collect_all_tweets(filename)
    for object in tweets:
        tweet = object['tweet']
        tweet_date = datetime.strptime(tweet['created_at'], '%a %b %d %H:%M:%S %z %Y').date() # Thu Nov 03 13:21:02 +0000 2022
        key = "%d/%02d" % ( tweet_date.year, tweet_date.month )
        if tweet_date.year < int( tweets_year ):
            if key not in tweet_ids:
                tweet_ids[key] = []
            tweet_ids[key].append(tweet["id"]) 
            tweet_counter += 1
        elif tweet_date.year == int( tweets_year ):
            if tweet_date.month <= int( tweets_month ):
                if key not in tweet_ids:
                    tweet_ids[key] = []
                tweet_ids[ key ].append(tweet["id"])
                tweet_counter += 1
    return [tweet_ids, tweet_counter]

def is_api_configured():
    if not configuration_is_valid():
        print( "API: No api-authorization configured, yet." )
        print( "API: Please configure account/authorization first before trying to use this script." )
        print( "" )
        return False
    return True

def configure_print_status():
    global APP_CFG_TWITTER_NICK
    global APP_CFG_TWITTER_ARCHIVE
    global APP_CFG_CONSUMER_KEY
    global APP_CFG_CONSUMER_SECRET
    global APP_CFG_ACCESS_TOKEN_KEY
    global APP_CFG_ACCESS_TOKEN_SECRET

    print( "CURRENT CONFIGURATION:" )
    print( "----------------------" )
    print( "            TWITTER NICK: {}".format( APP_CFG_TWITTER_NICK ) )
    print( "         TWITTER ARCHIVE: {}".format( APP_CFG_TWITTER_ARCHIVE ) )
    print( "       AUTH CONSUMER KEY: {}".format( APP_CFG_CONSUMER_KEY ) )
    print( "    AUTH CONSUMER SECRET: {}".format( APP_CFG_CONSUMER_SECRET ) )
    print( "   AUTH ACCESS TOKEN KEY: {}".format( APP_CFG_ACCESS_TOKEN_KEY ) )
    print( "AUTH ACCESS TOKEN SECRET: {}".format( APP_CFG_ACCESS_TOKEN_SECRET ) )
    print( "----------------------" )

def configuration_is_valid():
    global APP_CFG_TWITTER_NICK
    global APP_CFG_TWITTER_ARCHIVE
    global APP_CFG_CONSUMER_KEY
    global APP_CFG_CONSUMER_SECRET
    global APP_CFG_ACCESS_TOKEN_KEY
    global APP_CFG_ACCESS_TOKEN_SECRET

    constants_to_check = [APP_CFG_TWITTER_NICK,
    APP_CFG_TWITTER_ARCHIVE,
    APP_CFG_CONSUMER_KEY,
    APP_CFG_CONSUMER_SECRET,
    APP_CFG_ACCESS_TOKEN_KEY,
    APP_CFG_ACCESS_TOKEN_SECRET]
    for current_constant in constants_to_check:
        if not current_constant or not len( current_constant ) > 0:
            return False
    return True

def configuration_clear():
    CONFIG_FILE_PATH = APP_PATH+'/'+APP_CONFIG_FILE
    if os.path.exists( CONFIG_FILE_PATH ):
        continue_deleting = query_yes_no( "CONFIG DELETE: REALLY CLEAR CONFIG FOR ACCOUNT/AUTHORIZATION?", default="no" )
        if continue_deleting:
            print( "CONFIG DELETE: Deleting config {} ...".format( CONFIG_FILE_PATH ) )
            os.remove( CONFIG_FILE_PATH )
            print( "CONFIG DELETE: Deletion completed." )

def configuration_autobackup():
    CONFIG_FILE_PATH = APP_PATH+'/'+APP_CONFIG_FILE
    if APP_CFG_TWITTER_NICK and len( APP_CFG_TWITTER_NICK ) > 0:
        CONFIG_FILE_PATH_BACKUP = APP_PATH+'/'+'backup'+'_'+APP_CFG_TWITTER_NICK+'_'+APP_CONFIG_FILE
    else:
        CONFIG_FILE_PATH_BACKUP = APP_PATH+'/'+'backup'+'_'+APP_CONFIG_FILE
    if os.path.exists( CONFIG_FILE_PATH ):
        print( "CONFIG AUTOBACKUP: Autorenaming old config {} to {} ..." .format( CONFIG_FILE_PATH, CONFIG_FILE_PATH_BACKUP ) )
        os.rename( CONFIG_FILE_PATH, CONFIG_FILE_PATH_BACKUP )
        print( "CONFIG AUTOBACKUP: Autorenaming completed." )

def configuration_read():
    global APP_API

    global APP_CFG_TWITTER_NICK
    global APP_CFG_TWITTER_ARCHIVE
    global APP_CFG_CONSUMER_KEY
    global APP_CFG_CONSUMER_SECRET
    global APP_CFG_ACCESS_TOKEN_KEY
    global APP_CFG_ACCESS_TOKEN_SECRET

    global APP_DFT_TWITTER_NICK
    global APP_DFT_TWITTER_ARCHIVE
    global APP_DFT_CONSUMER_KEY
    global APP_DFT_CONSUMER_SECRET
    global APP_DFT_ACCESS_TOKEN_KEY
    global APP_DFT_ACCESS_TOKEN_SECRET

    # CHECK EXISTENCE
    CONFIG_FILE_PATH = APP_PATH+'/'+APP_CONFIG_FILE
    if not os.path.exists( CONFIG_FILE_PATH ):
        print( "CONFIG READ: No config {} found. Configuring default values." .format( CONFIG_FILE_PATH ) )
        # APPLY DEFAULT VALUES FROM GLOBAL CONSTANTS
        APP_CFG_TWITTER_NICK        = APP_DFT_TWITTER_NICK
        APP_CFG_TWITTER_ARCHIVE     = APP_DFT_TWITTER_ARCHIVE
        APP_CFG_CONSUMER_KEY        = APP_DFT_CONSUMER_KEY
        APP_CFG_CONSUMER_SECRET     = APP_DFT_CONSUMER_SECRET
        APP_CFG_ACCESS_TOKEN_KEY    = APP_DFT_ACCESS_TOKEN_KEY
        APP_CFG_ACCESS_TOKEN_SECRET = APP_DFT_ACCESS_TOKEN_SECRET
        # SAVE DEFAULTS TO A NEW CONFIG INSTEAD NOW...
        if configuration_is_valid():
            configuration_write()
        return
    else:
        print( "CONFIG READ: {}" .format( CONFIG_FILE_PATH ) )

    # READ FILE
    config_file = ConfigParser()
    try:
        config_file.read( CONFIG_FILE_PATH )
    except:
        print( "CONFIG READ: Reading config {} failed. (WARNING: API unconfigured!)" .format( CONFIG_FILE_PATH ) )
        return

    APP_CFG_TWITTER_NICK        = config_file.get( 'account', 'nick' )
    APP_CFG_TWITTER_ARCHIVE     = config_file.get( 'account', 'archive_file' )
    APP_CFG_CONSUMER_KEY        = config_file.get( 'authorization', 'consumer_key' )
    APP_CFG_CONSUMER_SECRET     = config_file.get( 'authorization', 'consumer_secret' )
    APP_CFG_ACCESS_TOKEN_KEY    = config_file.get( 'authorization', 'access_token_key' )
    APP_CFG_ACCESS_TOKEN_SECRET = config_file.get( 'authorization', 'access_token_secret' )

    # getfloat() raises an exception if the value is not a float
    # a_float = config.getfloat('main', 'a_float')
    # getint() and getboolean() also do this for their respective types
    # an_int = config.getint('main', 'an_int')

def configuration_write():
    global APP_API

    global APP_CFG_TWITTER_NICK
    global APP_CFG_TWITTER_ARCHIVE
    global APP_CFG_CONSUMER_KEY
    global APP_CFG_CONSUMER_SECRET
    global APP_CFG_ACCESS_TOKEN_KEY
    global APP_CFG_ACCESS_TOKEN_SECRET

    global APP_DFT_TWITTER_NICK
    global APP_DFT_TWITTER_ARCHIVE
    global APP_DFT_CONSUMER_KEY
    global APP_DFT_CONSUMER_SECRET
    global APP_DFT_ACCESS_TOKEN_KEY
    global APP_DFT_ACCESS_TOKEN_SECRET

    # WRITE FILE
    CONFIG_FILE_PATH = APP_PATH+'/'+APP_CONFIG_FILE

    # BACKUP PREXISTING CONFIG
    if os.path.exists( CONFIG_FILE_PATH ):
        configuration_autobackup();

    config_file = ConfigParser()
    config_file.read( CONFIG_FILE_PATH )
    # STORE account
    config_file.add_section( 'account' )
    config_file.set( 'account', 'nick', APP_CFG_TWITTER_NICK )
    config_file.set( 'account', 'archive_file', APP_CFG_TWITTER_ARCHIVE )
    # AUTH account
    config_file.add_section( 'authorization' )
    config_file.set( 'authorization', 'consumer_key', APP_CFG_CONSUMER_KEY )
    config_file.set( 'authorization', 'consumer_secret', APP_CFG_CONSUMER_SECRET )
    config_file.set( 'authorization', 'access_token_key', APP_CFG_ACCESS_TOKEN_KEY )
    config_file.set( 'authorization', 'access_token_secret', APP_CFG_ACCESS_TOKEN_SECRET )

    print( "CONFIG WRITE: Writing config {} ..." .format( CONFIG_FILE_PATH ) )
    with open( CONFIG_FILE_PATH, 'w' ) as file_to_write:
        config_file.write( file_to_write )
    print( "CONFIG WRITE: Writing succeeded." )

def configure_account():
    configure_print_status()
    print( "" )
    continue_configuring = True
    if configuration_is_valid():
        continue_configuring = query_yes_no( "CONFIG: REALLY RECONFIGURE ACCOUNT/AUTHORIZATION?", default="no" )

    if not continue_configuring:
        print( "CONFIG: Aborted configuration." )
        return
    # NOW ASK DETAILS FROM USER
    global APP_CFG_TWITTER_NICK
    global APP_CFG_TWITTER_ARCHIVE
    global APP_CFG_CONSUMER_KEY
    global APP_CFG_CONSUMER_SECRET
    global APP_CFG_ACCESS_TOKEN_KEY
    global APP_CFG_ACCESS_TOKEN_SECRET

    APP_CFG_TWITTER_NICK        = input( "        ENTER TWITTER NICK NAME: " ).rstrip()
    APP_CFG_TWITTER_ARCHIVE     = input( "ENTER PATH TO TWEET-ZIP-ARCHIVE: " ).rstrip()
    APP_CFG_CONSUMER_KEY        = input( "             ENTER CONSUMER KEY: " ).rstrip()
    APP_CFG_CONSUMER_SECRET     = input( "          ENTER CONSUMER SECRET: " ).rstrip()
    APP_CFG_ACCESS_TOKEN_KEY    = input( "         ENTER ACCESS TOKEN KEY: " ).rstrip()
    APP_CFG_ACCESS_TOKEN_SECRET = input( "      ENTER ACCESS TOKEN SECRET: " ).rstrip()

    print( "" )
    if configuration_is_valid():
        configuration_write()
        print( "CONFIG: Succeeded. Restart script now!" )
    else:
        print( "CONFIG: Entered data is invalid. Something is missing... have a close look..." )
        print( "" )
        configure_print_status()
    print( "" )


def analyze_account():
    global APP_API
    print( "" )
    screen_name = None
    if configuration_is_valid():
        choice_string = "ACCOUNT: ANALYZE CONFIGURED ACCOUNT (Current: %s)?" % APP_CFG_TWITTER_NICK
        continue_using_default_account = query_yes_no( choice_string, default="yes" )
        if continue_using_default_account:
            screen_name = APP_CFG_TWITTER_NICK
        else:
            screen_name = input( "ENTER TWITTER NICK NAME TO ANALYZE: " )
            screen_name = screen_name.rstrip()
    else:
        screen_name = input( "ENTER TWITTER NICK NAME TO ANALYZE: " )
        screen_name = screen_name.rstrip()

    print( "" )
    if not screen_name or len( screen_name ) < 2:
        print( "ACCOUNT: No valid account twitter nick entered. Aborting." )
        return

    MAX_ALLOWED_MESSAGES = 200
    MAX_ALLOWED_FAVS = 200
    MAX_ALLOWED_FOLLOWERS = 2000
    try:
        print( "ACCOUNT: ACQUIRING DATA... PLEASE WAIT..." )
        print( "" )
        if not is_api_configured():
            return
        account_owner = APP_API.GetUser( user_id=None, screen_name=screen_name, include_entities=True )
        #account_blocked_users = api.GetBlocks( user_id=None, screen_name=None, cursor=-1, skip_status=True, include_user_entities=True)
        #account_direct_messages = api.GetDirectMessages( since_id=None, max_id=None, count=MAX_ALLOWED_MESSAGES, include_entities=True, skip_status=False )
        #account_favourites = api.GetFavorites( user_id=None, screen_name=None, count=MAX_ALLOWED_FAVS, since_id=None, max_id=None, include_entities=True )
        #account_followers = api.GetFollowerIDs( user_id=None, screen_name=None, cursor=-1, stringify_ids=False, count=None, total_count=None )
        #account_following = api.GetFriendIDs( user_id=None, screen_name=None, cursor=-1, stringify_ids=False, count=None )
        #account_sent_direct_messages = api.GetSentDirectMessages( since_id=None, max_id=None, count=None, page=None, include_entities=True )
    except twitter.error.TwitterError as e:
        try:
            message = e.message[0]['message']
        except:
            message = repr( e.message )
        print( "ACCOUNT: Error acquiring account data." )
        print( "ACCOUNT: ERROR   {}" .format( message ) )
        return

    # list data
    print( "----------------------" )
    print( "       NAME: {}" .format( account_owner.name ) )
    print( " SCREENNAME: {}" .format( account_owner.screen_name ) )
    print( "  PROTECTED: {}" .format( account_owner.protected ) )
    print( " USER SINCE: {}" .format( account_owner.created_at ) )
    print( "DESCRIPTION: \n\n{}\n" .format( account_owner.description ) )
    print( "----------------------" )
    print( "     TWEETS: {}" .format( str( account_owner.statuses_count ) ) )
    print( "  FOLLOWERS: {}" .format( str( account_owner.followers_count ) ) )
    print( "  FOLLOWING: {}" .format( str( account_owner.friends_count ) ) )
    print( " FAVOURITES: {}" .format( str( account_owner.favourites_count ) ) )
    print( "----------------------" )
    return

def estimated_time_of_arrival( num_of_operations ):
    global APP_ESTIMATED_RATE_LIMIT
    estimated_seconds = num_of_operations * APP_ESTIMATED_RATE_LIMIT
    estimated_minutes = math.floor( estimated_seconds / 60 )
    estimated_seconds = estimated_seconds - ( estimated_minutes * 60 )
    estimated_hours = math.floor( estimated_minutes / 60 )
    estimated_minutes = estimated_minutes - ( estimated_hours * 60 )
    if estimated_hours > 0:
        if estimated_minutes > 0:
            eta_string = "%d hours and %d minutes" % ( estimated_hours, estimated_minutes )
        else:
            eta_string = "%d hours" % ( estimated_hours, )
    else:
        if estimated_seconds > 0:
            eta_string = "%d minutes and %d seconds" % ( estimated_minutes, estimated_seconds )
        else:
            eta_string = "%d minutes" % ( estimated_minutes, )
    return eta_string

def delete_favourites():
    global APP_API
    MAX_ALLOWED_FAVS = 200
    favs_to_delete = None
    screen_name = APP_CFG_TWITTER_NICK
    try:
        if not is_api_configured():
            return
        favs_to_delete = APP_API.GetFavorites( user_id=None, screen_name=None, count=MAX_ALLOWED_FAVS, since_id=None, max_id=None, include_entities=True )
        num_to_delete = len( favs_to_delete )
        num_deleted = 0
        num_deleted_total = 0
        account_owner = APP_API.GetUser( user_id=None, screen_name=screen_name, include_entities=True )
        num_to_delete_total = account_owner.favourites_count
    except:
        print( "FAVOURITES: Error determining amount of favourites." )
        return
    if num_to_delete_total == 0:
        print( "FAVOURITES: No more favs to delete. Everything already cleaned." )
        return

    if num_to_delete == 0 and num_to_delete_total > 0:
        print( "FAVOURITES: There are still {} favourites remaining, but twitter does not allow to delete those remaining favs." .format( num_to_delete_total ) )
        return

    print( "FAVOURITES: There are {} favourites in total to delete." .format( num_to_delete_total ) )

    estimated_time_needed = estimated_time_of_arrival( num_to_delete )
    print( "FAVOURITES: Deletion of first batch of {} favs will take an estimated () to finish." .format( num_to_delete, estimated_time_needed ) )

    continue_deleting = query_yes_no( "FAVOURITES: REALLY DELETE ALL FAVOURITES", default="no" )

    if not continue_deleting:
        print( "FAVOURITES: Aborted deleting." )
        return

    # start destroying favourites one by one
    while num_to_delete > 0:

        print( "FAVOURITES: Deleting {} favourites now..." .format( num_to_delete ) )
        for current_fav in favs_to_delete:
            error_counter = 0
            while True:
                try:
                    APP_API.DestroyFavorite(status=None, status_id=current_fav.id, include_entities=True)
                    num_deleted += 1
                    num_deleted_total += 1
                    print( "FAVOURITES: {} DELETED ({}/{} of {}/{})" .format( current_fav.id, num_deleted, num_deleted_total, num_to_delete, num_to_delete_total ) )
                    break
                except twitter.error.TwitterError as e:
                    try:
                        message = e.message[0]['message']
                        retry = False
                    except:
                        message = repr( e.message )
                        retry = True
                    print( "FAVOURITES: {} ERROR   {}" .format( current_fav.id, message ) )
                    error_counter += 1
                    if error_counter > 5:
                        print( "FAVOURITES: Too many errors, aborting!" )
                        exit(1)
                    if not retry:
                        break # exit endless while loop
        # fetch next batch of 200 favs until we get ZERO
        favs_to_delete = APP_API.GetFavorites( user_id=None, screen_name=None, count=MAX_ALLOWED_FAVS, since_id=None, max_id=None, include_entities=True )
        num_to_delete = len( favs_to_delete )
        num_deleted = 0
        account_owner = APP_API.GetUser( user_id=None, screen_name=screen_name, include_entities=True )
        print( "FAVOURITES: REMAINING FAVOURITES TO DELETE: {}" .format( account_owner.favourites_count ) )
        print( "FAVOURITES: DELETING NEXT BATCH OF FAVOURITES WITH {} REMAINING." .format( num_to_delete ) )

    print( "FAVOURITES: DELETION COMPLETED." )
    return

def delete_retweets():
    global APP_API
    MAX_ALLOWED_RETS = 100
    rets_to_delete = None
    screen_name = APP_CFG_TWITTER_NICK
    try:
        if not is_api_configured():
            return
        rets_to_delete = APP_API.GetUserRetweets( count=None, since_id=None, max_id=None, trim_user=False)
        num_to_delete = len( rets_to_delete )
        num_deleted = 0
        num_deleted_total = 0
    except:
        print( "RETWEETS: Error determining amount of retweets." )
        return
    if num_to_delete == 0:
        print( "RETWEETS: No more retweets to delete. Everything already cleaned." )
        return

    print( "RETWEETS: There are {} retweets in to delete." .format( num_to_delete ) )

    estimated_time_needed = estimated_time_of_arrival( num_to_delete )
    print( "RETWEETS: Deletion of first batch of {} retweets will take an estimated {} to finish." .format( num_to_delete, estimated_time_needed ) )

    continue_deleting = query_yes_no( "RETWEETS: REALLY DELETE ALL RETWEETS", default="no" )

    if not continue_deleting:
        print( "RETWEETS: Aborted deleting." )
        return

    # start destroying favourites one by one APP_API.DestroyStatus(tid)
    while num_to_delete > 0:

        print( "RETWEETS: Deleting {} retweets now..." .format( num_to_delete ) )
        for current_ret in rets_to_delete:
            #print "------------------------"
            #print "RETWEET: id="+ str( current_ret.id ) + ", JSON="+current_ret.AsJsonString()
            #print "------------------------"

            error_counter = 0
            should_delete = True
            while should_delete:
                try:
                    APP_API.DestroyStatus( current_ret.id )
                    num_deleted += 1
                    print( "RETWEETS: {} DELETED ({} of {})" .format( current_ret.id, num_deleted, num_to_delete ) )
                    break
                except twitter.error.TwitterError as e:
                    try:
                        message = e.message[0]['message']
                        retry = False
                    except:
                        message = repr( e.message )
                        retry = True
                    print( "RETWEETS: {} ERROR   {}" .format( current_ret.id, message ) )
                    error_counter += 1
                    if error_counter > 5:
                        print( "RETWEETS: Too many errors, aborting!" )
                        exit(1)
                    if not retry:
                        break # exit endless while loop
        # fetch next batch of next 200 items until we reach ZERO remaining items
        rets_to_delete = rets_to_delete = APP_API.GetUserRetweets( count=None, since_id=None, max_id=None, trim_user=False)
        num_to_delete = len( rets_to_delete )
        print( "RETWEETS: REMAINING RETWEETS TO DELETE: {}" .format( num_to_delete ) )
        print( "RETWEETS: DELETING NEXT BATCH OF RETWEETS WITH {} REMAINING." .format( num_to_delete ) )

    print( "RETWEETS: DELETION COMPLETED." )
    return

def delete_followers():
    global APP_API
    print( "FOLLOWERS: Not yet implemented." )

def delete_friends():
    global APP_API
    print( "FRIENDS: Not yet implemented." )

def delete_directmessages():
    global APP_API
    MAX_ALLOWED_MESSAGES = 200
    messages_to_delete = None
    try:
        if not is_api_configured():
            return
        messages_to_delete = APP_API.GetSentDirectMessages(since_id=None, max_id=None, count=MAX_ALLOWED_MESSAGES, page=None, include_entities=True)
        num_to_delete = len( messages_to_delete )
        num_deleted = 0
    except:
        print( "MESSAGES: Error determining amount of direct messages." )
        return
    if num_to_delete == 0:
        print( "MESSAGES: No more messages to delete. Everything already cleaned." )
        return

    print( "MESSAGES: There are {} sent direct messages to delete." .format( num_to_delete ) )

    estimated_time_needed = estimated_time_of_arrival( num_to_delete )
    print( "MESSAGES: Deletion will take an estimated {} to finish." .format( estimated_time_needed ) )

    continue_deleting = query_yes_no( "MESSAGES: REALLY DELETE ALL DIRECT MESSAGES SENT", default="no" )

    if not continue_deleting:
        print( "MESSAGES: Aborted deleting." )
        return

    # start destroying messages one by one
    print( "MESSAGES: Deleting {} direct messages now..." .format( num_to_delete ) )
    for current_message in messages_to_delete:
        error_counter = 0
        while True:
            try:
                APP_API.DestroyDirectMessage( current_message.id, include_entities=True )
                num_deleted += 1
                print( "MESSAGES: {} DELETED ({} of {}) TO {}" .format( current_message.id, num_deleted, num_to_delete, current_message.recipient_screen_name ) )
                break
            except twitter.error.TwitterError as e:
                try:
                    message = e.message[0]['message']
                    retry = False
                except:
                    message = repr( e.message )
                    retry = True
                print( "MESSAGES: {} ERROR   {}" .format( current_message.id, message ) )
                error_counter += 1
                if error_counter > 5:
                    print( "MESSAGES: Too many errors, aborting!" )
                    exit(1)
                if not retry:
                    break # exit endless while loop
    print( "MESSAGES: DELETION COMPLETED." )
    return

def delete_tweets_choose_time_range( filename_archive ):
    year_today = date.today().year
    year_choice = "PLEASE CHOOSE YEAR UP TO WHICH WE DELETE TWEETS (ENTER for {}): ".format( year_today )
    action_raw = input( year_choice ).rstrip()
    if not action_raw:
        year_chosen = year_today
    else:
        year_chosen = int( action_raw )

    month_today = date.today().month
    month_choice = "PLEASE CHOOSE MONTH (1-12) UP TO WHICH WE DELETE TWEETS (ENTER for {}): ".format( month_today )
    action_raw = input( month_choice ).rstrip()
    if not action_raw:
        month_chosen = month_today
    else:
        month_chosen = int( action_raw )

    continue_deleting = query_yes_no( "TWEETS: SELECT ALL TWEETS UNTIL AND INCLUDING MONTH/YEAR {}/{} ?".format( month_chosen, year_chosen), default="no" )
    if not continue_deleting:
        print( "TWEETS: Aborted deleting." )
        return
    delete_tweets_from_archive_until_year( filename_archive, year_chosen, month_chosen )


def delete_tweets_from_archive_until_year( filename_archive, tweets_year, tweets_month ):
    global APP_API
    if not is_api_configured():
        return

    if filename_archive == None:
        print( "TWEETS: No ZIP archive configured to work with." )
        return
    FILE_PATH = APP_PATH+'/'+filename_archive
    if not os.path.exists( FILE_PATH ):
        print( "TWEETS: The twitter archive in {} was not found." .format( FILE_PATH ) )
        return

    # get list of ids to destroy from zip file
    result_array = tweets_extract_ids_from_zipfile( filename_archive, tweets_year, tweets_month )
    
    tweet_ids = result_array[0]
    num_to_delete = result_array[1]

    # sort in reversed order
    tweet_ids_sorted = sorted( tweet_ids.keys(), reverse=True )

    print( "TWEETS: There are {} tweets to delete." .format( num_to_delete ) )

    estimated_time_needed = estimated_time_of_arrival( num_to_delete )
    print( "TWEETS: Deletion will take an estimated {} to finish." .format( estimated_time_needed ) )

    continue_deleting = query_yes_no( "TWEETS: REALLY DELETE ALL TWEETS NOW?", default="no" )
    if not continue_deleting:
        print( "TWEETS: Aborted deleting." )
        return
    
    begin = False
    num_deleted = 0
    for date in tweet_ids_sorted:
        year, month = date.split("/") # not really used
        num_to_delete_month = len( tweet_ids[date] )
        num_deleted_month = 0
        print( "TWEETS: Deleting {} tweets of: {}" .format( num_to_delete_month, date ) )
        for tid in tweet_ids[date]:
            if begin or last == 0 or tid == last:
                begin = True
                error_counter = 0
                while True:
                    num_deleted += 1
                    num_deleted_month += 1
                    try:
                        APP_API.DestroyStatus(tid)
                        print( "TWEETS: {} DELETED {}/{} of {}/{} (MONTH/TOTAL)" .format( tid, num_deleted_month,num_deleted, num_to_delete_month, num_to_delete ) )
                        break
                    except twitter.error.TwitterError as e:
                        try:
                            message = e.message[0]['message']
                            retry = False
                        except:
                            message = repr( e.message )
                            retry = True
                        print( "TWEETS: {} ERROR   {}   {}/{} of {}/{} (MONTH/TOTAL)" .format( tid, message, num_deleted_month,num_deleted, num_to_delete_month, num_to_delete) )
                        error_counter += 1
                        if error_counter > 5:
                            print( "TWEETS: Too many errors, aborting!" )
                            exit(1)
                        if not retry:
                            break # exit endless while loop
    print( "TWEETS: DELETION COMPLETED." )

def clear_screen():
    print( "" )
    action_raw = input( "ENTER to continue... " ).rstrip()
    os.system('cls' if os.name == 'nt' else 'clear')

# main app call
if __name__ == "__main__":
    os.system('cls' if os.name == 'nt' else 'clear')
    stay_alive = True
    while stay_alive:
        print( "" )
        print( "******************************************" )
        print( "***            TWEETI-KIRI             ***" )
        print( "***  YOUR SOCIAL MEDIA VACUUM CLEANER  ***" )
        print( "***                                    ***" )
        print( "***     by trailblazr, 2016 - 2019     ***" )
        print( "***  (derived from Mario Vilas' code)  ***" )
        print( "******************************************" )
        print( APP_LOGO )
        print( "" )
        configuration_read()
        # configure_print_status()
        if configuration_is_valid():
            # Configure API with keys & secrets of app
            APP_API = twitter.Api( 
                consumer_key=APP_CFG_CONSUMER_KEY, 
                consumer_secret=APP_CFG_CONSUMER_SECRET,
                access_token_key=APP_CFG_ACCESS_TOKEN_KEY, 
                access_token_secret=APP_CFG_ACCESS_TOKEN_SECRET, )
        else:
            APP_CFG_TWITTER_NICK = None

        if APP_CFG_TWITTER_NICK and len( APP_CFG_TWITTER_NICK ) > 0:
            account_string =  " (Current: %s)" % APP_CFG_TWITTER_NICK
        else:
            account_string = ""

        num_menu_items = 8
        print( "" )
        print( "MENU OF AVAILABLE ACTIONS" )
        print( "" )
        print( "(1) Account configure{}" .format( account_string ) )
        print( "(2) Account analyze" )
        print( "(3) Remove tweets" )
        print( "(4) Remove direct messages" )
        print( "(5) Remove favourites" )
        print( "(6) Remove (my) retweets" )
        print( "(7) Remove followers - Not yet implemented -" )
        print( "(8) Remove friends/following - Not yet implemented -" )

        CONFIG_FILE_PATH = APP_PATH+'/'+APP_CONFIG_FILE
        if os.path.exists( CONFIG_FILE_PATH ):
            print( "(9) Remove configuration" )
            num_menu_items += 1

        print( "(0) EXIT/ABORT" )
        print( "" )
        print( "VERSION: {}".format( APP_VERSION ) )
        print( "   INFO: EVERY POTENTIALLY DESTRUCTIVE ACTION WILL ASK FOR CONFIRMATION AGAIN!" )
        print( "" )
        print( "WELCOME." )
        print( "" )

        menu_choice = "PLEASE CHOOSE ITEM FROM MENU [0..{}]: ".format( num_menu_items )
        action_raw = input( menu_choice ).rstrip()
        if not action_raw:
            action_chosen = 0
        else:
            action_chosen = int( action_raw )
        if action_chosen == 1:
            print( "CONFIGURING..." )
            configure_account()
        elif action_chosen == 2:
            print( "ANALYZING..." )
            analyze_account()
        elif action_chosen == 3:
            print( "RETRIEVING TWEETS..." )
            delete_tweets_choose_time_range( APP_CFG_TWITTER_ARCHIVE )
        elif action_chosen == 4:
            print( "RETRIEVING DIRECT MESSAGES..." )
            delete_directmessages()
        elif action_chosen == 5:
            print( "RETRIEVING FAVOURITES..." )
            delete_favourites()
        elif action_chosen == 6:
            print( "RETRIEVING RETWEETS..." )
            delete_retweets()
        elif action_chosen == 7:
            print( "RETRIEVING FOLLOWERS..." )
            delete_followers()
        elif action_chosen == 8:
            print( "RETRIEVING FRIENDS..." )
            delete_friends()
        elif action_chosen == 9 and num_menu_items >= 9:
            print( "Cleaning CONFIG..." )
            configuration_clear()
        elif action_chosen == 0:
            print( "EXIT/ABORT..." )
            stay_alive = False
        else:
            print( "ERROR: INVALID CHOICE/INPUT" )
        if action_chosen != 0:
            clear_screen()


    print( "GOOD BYE!" )
    print( "" )

"""
HINTS FOR INSTALLING AND MODIFYING THIS SCRIPT:
(added by trailblazr from hackerspace bremen, germany)

- to make this script run you need certain installed python modules which are best installed in a virtualenv directory
- so first create a virtualenv directory using 'virtualenv tweeti-kiri'
- then change dir into it and type 'source bin/activate'
- now copy this script into the tweeti-kiri-directory
- continue installing the missing/needed python modules
- you need to install 'anyjson' and 'python-twitter' using 'pip install anyjson' and 'pip install python-twitter'
- also put your downloaded zip.archive of tweets you ordered at twitter in this directory (keep it zipped)
- that's it. you are set. please read the original instructions by Mario Vilas below now...
- to modify the script try e.g. typing 'pydoc'-commands to learn about the twitter api
- type e.g. 'pydoc twitter.DirectMessage' to get more info on classes in the twitter module and how they work
- try to keep stuff simple (use KISS design principle)
- use comments in your code and simplify this code and do make pull-requests

ORIGINAL CODE SOURCE / BLOGPOST / IDEA:
https://breakingcode.wordpress.com/2016/04/04/how-to-clean-up-your-twitter-account/
by Mario Vilas, Security Consultant at NCC Group
see also https://www.linkedin.com/in/mariovilas
on Twitter @Mario_Vilas

EXCERPT FROM THE ORIGINAL BLOG POST (HERE TEXT ONLY):
How to clean up your Twitter account
(Filed under: Privacy, Programming, Tools)
(Tags: LinkedIn, python, tool, Twitter, web, webapp — Mario Vilas at 5:47 am)

Recently I decided to get rid of all of my old tweets, specifically all of them from last year and before.
I had no use for most of them and curating them would have been too much of a burden (over 66.000 tweets! 
so much procrastination!).

Now, there are a number of online applications to do that, but they have at least one of the following problems,
fundamentally the last one:

They pull your Twitter posts from the API, which only allows you to read at most the latest 200 tweets, so removing
the older ones becomes impossible. Some of them get around this by asking you to upload your entire Twitter archive…
which contains a lot more than just your tweets (i.e. your private messages). (EDIT: I’m being told this is no longer
the case, now it just contains your public timeline)

I don’t trust them.

So naturally I rolled my own. The code is crude but it worked for me. It uses the Twitter archive zip file as well,
but since it works locally you don’t need to trust a third party with your personal data. With this I managed to delete
over 60.000 tweets in a day and a half, roughly – it can’t be done much faster because of the API rate limiting, but then
again, what’s the rush? :)

Now, to use it, follow these steps:

(1) Get your Twitter archive.

You can do this by going to Settings -> Account -> Your Twitter archive.
This will send you an email with a download link to a zip file.

(2) Get this script and place it in the same directory as the zip file you just downloaded.

(3) Go to https://apps.twitter.com/ and create a new application.

This will get you the consumer key and the consumer secret, take note of those.
Authorize your app to access your own account (you do it in the same place right after creating your new app).
Check that you change permissions to also allow the app to access your direct messages if you want to delete them too.

(4) Now you have the access token key and secret if not yet generate them, take note of those too. Store that info on your machine.

(5) Edit the script and add all those tokens and secrets at the beginning of the file to the default values.

Add the name of the zip file as well to the default values.
Since you’re at it, review the source code of this script – you shouldn’t be running code you downloaded from
some random place on the interwebz without reading it first!

(6) Run the script. This will take some time. Disable powersave-mode on your machine, lock it and get off the chair. Go out.

Enjoy the real world. It’s the ultimate 3D experience, and it comes in HD!

"""
