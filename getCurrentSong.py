import dbus
from dbus.mainloop.glib import DBusGMainLoop
import glib
import copy
import xmpp
import json
from googleChatStatus import GoogleChatHelper

class MusicPlayerStatus:
    def __init__(self):
        self.DEBUG = 1       # debug flag
        self.supportedMediaPlayers = ["guayadeque", "banshee", "rhythmbox", "clementine"] # Supported Media Players
        self.identity = None # player identity
        self.playerProxy = None
        self.playerProps = None
        self.player = None
        self.currTrackStr = None
        self.credentials = self.loadCredentials()
        self.userName = self.credentials[0]
        self.pwd = self.credentials[1]
        self.gChatHelper = GoogleChatHelper(self.userName, self.pwd)
    
    # load credentials
    def loadCredentials(self):
        credentialsFile = 'credentials_file'
        cred = [line.strip() for line in open(credentialsFile)] 
        return cred

    #Change Google Chat Status
    def changeGoogleChatStatus(self, newStatus):
        newStatus = u'\u266a' + ' ' + newStatus + ' ' + u'\u266a'
        self.debugLog('Setting new GMail Status to %s' % (newStatus))
        self.gChatHelper.set_status(newStatus)

    # debug function 
    def debugLog(self, str):
        if(self.DEBUG):
            print str

    # debug dump function
    def debugDump(self, data):
        if(self.DEBUG):
            print json.dumps(data)

    def main(self):
        self.ConnectToBus()
        self.mainloop = glib.MainLoop()
        self.mainloop.run()

    # Connects to the Media Player we detected
    def Connect(self, name):
        self.debugLog("Connect to %s" % (name))
        #Cmd = dbus-monitor "type='signal',interface='org.freedesktop.DBus.Properties',path='/org/mpris/MediaPlayer2',member='PropertiesChanged'"
        self.playerProxy = self.bus.get_object(name, '/org/mpris/MediaPlayer2')
        self.playerProps = dbus.Interface(self.playerProxy, 'org.freedesktop.DBus.Properties')
        self.playerProps.connect_to_signal("PropertiesChanged", self.TrackChanged, dbus_interface="org.freedesktop.DBus.Properties")
        self.identity = name

        #Check if any song is being played
        playbackStatus = self.playerProps.Get('org.mpris.MediaPlayer2.Player', 'PlaybackStatus')
        if(playbackStatus == "Playing"):
            #Get current song metadata and call TrackChanged
            initMetadata = self.playerProps.Get('org.mpris.MediaPlayer2.Player', 'Metadata')
            initInterface = 'org.mpris.MediaPlayer2.Player'
            initData = {}
            initData['Metadata'] = initMetadata
            self.TrackChanged(initInterface, initData, [])

    # TrackChanged callback
    def TrackChanged(self, interface, data, sigArray):
        if 'Metadata' not in data:
            return

        #Debug metadata
        #self.debugDump(data) 

        metaData = data['Metadata']
        #Check that artist and title exist, else not return
        if 'xesam:artist' not in metaData or 'xesam:title' not in metaData:
            return

        #Compute newTrackStr
        newTrackStr = ""
        artist = ', '.join(metaData['xesam:artist'])
        title = metaData['xesam:title'] 
        if 'xesam:album' in metaData:
            album = metaData['xesam:album']
            newTrackStr = "%s - %s (%s)" % (title, artist, album)
        else:
            newTrackStr = "%s - %s" % (title, artist)

        #Check if newTrackStr is same as currTrackStr, if 'yes', ignore this signal
        if(newTrackStr != self.currTrackStr):
            self.currTrackStr = copy.deepcopy(newTrackStr)
            self.debugLog("Track Changed -> %s" % (self.currTrackStr))
            self.changeGoogleChatStatus(self.currTrackStr)
        else:
            self.debugLog("Track didn't change, duplicate signal")

    #NameOwnerChanged
    def NameOwnerChanged(self, name, new, old):
        if old != "" and "org.mpris." in name:
            self.Connect(name)

    # check if player is supported
    def isSupportedPlayer(self, playerName):
        for p in self.supportedMediaPlayers:
            if p in playerName:
                return True
        return False

    # connect to the bus
    def ConnectToBus(self):
        print "ConnectToBus"
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
                    self.Connect(playerName)
                    break
                else:
                    self.debugLog("%s is not supported" % playerName)


if(__name__ == "__main__"):
    mPlayerStatus = MusicPlayerStatus()
    mPlayerStatus.main()
