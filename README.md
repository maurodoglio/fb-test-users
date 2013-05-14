fb-test-users
=============

A (very) simple script to demo the FB API for test user creation 

Setup
-------------

To run this script you need to go to https://developers.facebook.com/apps
and create a new facebook application.

The info needed to create an app are the following::
* Application name
* App namespace (slug)

If you're asked to specify the type of your application choose 'Web mobile' (website with facebook login should be fine too).

Once the app profile is created you should see the App ID/API Key and the app secret key. Fill FB_APP_ID and FB_APP_SECRET inside the python script with those values. 

For more info see See https://developers.facebook.com/docs/test_users/