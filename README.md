# utilsForDisplay

Python Flask Server created to work with an 800 x 480 pixel display. Features updating time, spotify, weather, and calendar.

Dependencies:

flask
  * Runs the server locally, open the provided url in a browser to see the application.
  
requests
  * Gets https request data from public urls.
  
spotipy
  * Accesses the Spotify API (specifically with the scope of user-read-playback-state)
  
icalendar
  * Processes calendar data from icals into events.
  
perlin_noise
  * A smooth noise generator for the moving background mesh.
  
PIL
  * Python's Image Processing Library
  
sklearn
  * Data segmentation algorithm
  * Used with PIL to take the pixel data of an image and pull the most "important" colors
