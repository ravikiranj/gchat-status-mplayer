import dbus
from dbus.mainloop.glib import DBusGMainLoop
import glib
import copy
import xmpp

class MusicPlayerStatus:
    def __init__(self):
        self.DEBUG = 1       # debug flag

        self.root = None         # / org.freedesktop.MediaPlayer
        self.player = None      # /Player org.freedesktop.MediaPlayer
        self.tracklist = None    # /Tracklist org.freedesktop.MediaPlayer

        self.playing = False      # Playing status

        self.bus = None          # Connection to the session bus
        self.identity = None     # MediaPlayer Identity

        self.mainloop = None     # Main loop

        self.supportedMediaPlayers = ["guayadeque"] # Supported Media Players

        self.trackChangeStr = "" # Changed Track Status
        self.currentTrackStr = "" # Current Track Status

        USERNAME = "ravikirn@cs.unc.edu"       # don't include @gmail.com
        PASSWORD = ""
        self.gChatStatus = GChatStatus(USERNAME, PASSWORD)

    def getCurrentPlayingTrack(self):
        return self.currentTrackStr

    def main(self):
        self.ConnectToBus()
        self.mainloop = glib.MainLoop()
        self.mainloop.run()

    # connect to the bus
    def ConnectToBus(self):
        DBusGMainLoop(set_as_default=True)

        self.bus = dbus.SessionBus()
        dbus_names = self.bus.get_object( "org.freedesktop.DBus", "/org/freedesktop/DBus" )
        dbus_names.connect_to_signal("NameOwnerChanged", self.NameOwnerChanged, dbus_interface="org.freedesktop.DBus") # to detect new Media Players

        dbus_o = self.bus.get_object("org.freedesktop.DBus", "/")
        dbus_intf = dbus.Interface(dbus_o, "org.freedesktop.DBus")
        name_list = dbus_intf.ListNames()

        # connect to the first Media Player found
        for playerName in name_list:
            if "org.mpris." in playerName:
                if self.isSupportedPlayer(playerName):
                    self.debugLog("Connected to %s" % playerName)
                    self.Connect(playerName)
                    break
                else:
                    self.debugLog("%s is not supported" % playerName)

    # check if player is supported
    def isSupportedPlayer(self, playerName):
        for p in self.supportedMediaPlayers:
            if p in playerName:
                return True
        return False

    # Connects to the Media Player we detected
    def Connect(self, name):
        # first we connect to the objects
        root_o = self.bus.get_object(name, "/")
        player_o = self.bus.get_object(name, "/Player")
        tracklist_o = self.bus.get_object(name, "/TrackList")

        # there is only 1 interface per object
        self.root = dbus.Interface(root_o, "org.freedesktop.MediaPlayer")
        self.tracklist  = dbus.Interface(tracklist_o, "org.freedesktop.MediaPlayer")
        self.player = dbus.Interface(player_o, "org.freedesktop.MediaPlayer")

        # connect to the TrackChange signal
        player_o.connect_to_signal("TrackChange", self.TrackChange, dbus_interface="org.freedesktop.MediaPlayer")

        # determine if the Media Player is playing something
        if self.methodExists(self.player, "GetMetadata"):
            track = self.player.GetMetadata()
            if track:
                self.TrackChange(track)

        self.identity = name

    # debug function 
    def debugLog(self, str):
        if(self.DEBUG):
            print str

    # TrackChange callback
    def TrackChange(self, Track):
        artist = self.getTrackProperty(Track, 'artist')
        title = self.getTrackProperty(Track, 'title')
        year = self.getTrackProperty(Track, 'year')
        self.trackChangeStr = ""
        if(artist != "" and title != ""):
            if(year != ""):
                self.trackChangeStr = "%s - %s (%s)" % (title, artist, year)
            else:
                self.trackChangeStr = "%s - %s" % (title, artist)

        if(self.trackChangeStr != ""):
            self.currentTrackStr = copy.deepcopy(self.trackChangeStr)
            self.changeGChatStatus(self.currentTrackStr)
            self.debugLog("Track Changed - %s" % (self.currentTrackStr))
        else:
            self.debugLog("Track Changed but either artist or title were empty")

    def changeGChatStatus(self, newStatus):
        print "Changing GMail Status"
        self.gChatStatus.set_status(newStatus)

    #Get Track Property
    def getTrackProperty(self, d, key):
        if key in d:
            return d[key]
        else:
            return ""

    #Dump Object
    def dump(self, obj):
      for attr in dir(obj):
          print "obj.%s = %s" % (attr, getattr(obj, attr))

    def NameOwnerChanged(self, name, new, old):
        if old != "" and "org.mpris." in name:
            self.Connect(name)

    #Check if method exists
    def methodExists(self, obj, methodName):
        if(hasattr(obj, methodName) and callable(getattr(obj, methodName))):
            return True
        return False
#end class

class GChatStatus():
    def __init__(self, username='', password=''):
        self.username = username
        self.password = password
        self.jid = xmpp.protocol.JID(self.username)
        if not self.jid.getNode():
            print 'You must supply a username in the form of username@server.com'
            exit(1)
        self.connect()
 
    def connect(self, debug=''):
        self.client = xmpp.Client(self.jid.getDomain(), debug=debug)
        if not self.client.connect(('gmail.com', 5223)):
            raise IOError('Could not connect to server.')
        if not self.client.auth(self.jid.getNode(), self.password):
            raise IOError('Could not authenticate to server.')
 
    def set_status(self, new_status):
        # Thanks to http://blog.thecybershadow.net/2010/05/08/setting-shared-google-talk-gmail-status-programmatically/
        resp = self.client.SendAndWaitForResponse(xmpp.Iq('get','google:shared-status', payload=[]))
        current_show = resp.getTag('query').getTagData('show')
        if new_status:
            print 'setting status:', new_status, '[%s]'%current_show
        else:
            print 'resetting status:', '[%s]'%current_show
            new_status = ''
        self.client.SendAndWaitForResponse(xmpp.Iq('set','google:shared-status', payload=[
            xmpp.Node('show',payload=[current_show]),
            xmpp.Node('status',payload=[new_status])
        ]))
#end class

if(__name__ == "__main__"):
    mPlayerStatus = MusicPlayerStatus()
    mPlayerStatus.main()
