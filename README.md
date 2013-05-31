<h2>Readme</h2>
* Requires python2.7 and python-dbus. You can install it on Ubuntu with below command.

   <pre>sudo apt-get install python2.7 python-dbus

* Currently supports 5 media players, namely Amarok, Banshee, Clementine, Guayadeque (my fav) and Rhythmbox.

* Launch the script using below command on the command-line.

   <pre>python syncCurrentSong.py</pre>

* The script needs your GMail credentials to update your Google Chat Status. However, it does not store it locally and will ask you everytime for security reasons.
<pre>
python syncCurrentSong.py
Please enter your GMail crendentials (the script doesn't store it)
Username: test\_account@gmail.com
Password: 
</pre>

* When you start a media player, it displays the current playlist song on the console and updates the same as your Google Chat Status Message.
<pre>
python syncCurrentSong.py 
...
♪ The Missing - Deerhunter (Monomania) ♪
</pre>

* You can turn the debug flag ON in syncCurrentSong.py for additional diagnostics.
<pre>self.DEBUG = 1</pre>
