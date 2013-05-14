from facebook import (GraphAPI, get_app_access_token, GraphAPIError)
import urllib
import logging
import httplib
import json

FB_APP_ID = ""
FB_APP_SECRET = ""


class TestUserManager(object):

    def __init__(self, app_id, app_secret):
        self.app_id = app_id
        self.app_secret = app_secret
        self.app_access_token = get_app_access_token(app_id, app_secret)
        self.graph = GraphAPI()
        self.users = []

    def create_test_users(self, num_users=10):
        """
        create a number of test_users for this app.
        The maximum number of test users allowed is 2000.
        """
        for i in range(1, num_users + 1):
            user_data = self.graph.request(
                '%s/accounts/test-users' % self.app_id,
                args={
                    'access_token': self.app_access_token,
                    'method': 'post'
                }
            )
            self.users.append(user_data)

    def add_friend_connection(self, user_id_1, user_id_2, token_user_1, token_user_2):
        """
        We need two requests:
        1 - from user_id_1 to invite to connect
        2 - from user_id_2 to accept the invitation
        """
        friend_request_url = "%s/friends/%s" % (user_id_1, user_id_2)
        request_sent = self.graph.request(
            friend_request_url,
            post_args={'access_token': token_user_1})

        if request_sent:
            # and accept it
            friend_request_url = "%s/friends/%s" % (user_id_2, user_id_1)
            request_accepted = self.graph.request(
                friend_request_url,
                post_args={'access_token': token_user_2})

        if not (request_sent and request_accepted):
            raise Exception("Error while connecting users %s and %s" % (user_id_1, user_id_2))

    def revoke_login(self, user_id):
        """Disable all the authorizations the user gave to this app"""
        conn = httplib.HTTPSConnection('graph.facebook.com')

        url = '/%s/permissions?%s' % (
            user_id,
            urllib.urlencode({'access_token': self.app_access_token})
        )
        conn.request('DELETE', url)
        response = conn.getresponse()
        data = response.read()

        response = json.loads(data)
        # Raise an error if we got one, but don't not if Facebook just
        # gave us a Bool value
        if (response and isinstance(response, dict) and response.get("error")):
            raise GraphAPIError(response)
        conn.close()
        print "user %s revoked authorizations" % user_id

    def delete_all_users(self):
        for user in self.users:
            self.graph.request(user['id'], post_args={"method": "delete",
                                                      'access_token': self.app_access_token})
        self.users = []


if __name__ == '__main__':
    test_user_manager = TestUserManager(FB_APP_ID, FB_APP_SECRET)
    test_user_manager.create_test_users()

    try:
        # create a connection between the first user and the other ones
        main_user = None
        for user in test_user_manager.users:
            if not main_user:
                main_user = user
            else:
                test_user_manager.add_friend_connection(
                    main_user['id'],
                    user['id'],
                    main_user['access_token'],
                    user['access_token']
                )
                test_user_manager.revoke_login(user['id'])
                print "%s and %s are now friends" % (main_user['id'], user['id'])
        test_user_manager.revoke_login(main_user['id'])

        # at this point we should have a clean situation (i.e. ready for testing)

    except Exception, e:
        print e
    finally:
        test_user_manager.delete_all_users()
