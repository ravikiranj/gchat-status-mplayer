#!/usr/bin/env python

#Thanks to http://bluegray.co.za/content/setting-google-talk-status-python-xmpp for the code

import xmpp, sys

class GoogleChatHelper():
    def __init__(self, username):
        self.username = username
        self.connSuccess = False
        self.jid = xmpp.protocol.JID(self.username)
 
    def connect(self, passwd, debug=''):
        self.client = xmpp.Client(self.jid.getDomain(), debug=debug)
        if not self.client.connect(('gmail.com', 5223)):
            print 'Could not connect to server.'
            return

        if not self.client.auth(self.jid.getNode(), passwd):
            print 'Could not authenticate to server.'
            return

        self.connSuccess = True
        

    def isConnected(self):
        return self.connSuccess
 
    def set_status(self, new_status):
        # Thanks to http://blog.thecybershadow.net/2010/05/08/setting-shared-google-talk-gmail-status-programmatically/
        resp = self.client.SendAndWaitForResponse(xmpp.Iq('get','google:shared-status', payload=[]))
        current_show = resp.getTag('query').getTagData('show')
        self.client.SendAndWaitForResponse(
                                           xmpp.Iq('set','google:shared-status', payload=[
                                                                                          xmpp.Node('show',payload=[current_show]),
                                                                                          xmpp.Node('status',payload=[new_status])
                                                                                          ]
                                                  )
                                          )
    #end set_status
#end Class

