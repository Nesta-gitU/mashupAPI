# How to use

## step 1
make sure you are in the mashupAPI directory 


## step 2
We will use docker to run the program. First install docker via the docker website.
Then build the docker file \
``
docker build -f Dockerfile -t nestami/mashup-api:dev .
``

Run the docker file \
``
docker run --rm -p 8000:8000 nestami/mashup-api:dev  
``

## step 3
open the locally hosted backend 

http://localhost:8000 

the backend is build with fastapi, by extending the localhost with 

http://localhost:8000/docs/ 

we can see the available commands and options for the api 

The api has the following end points:
- get_session_id() -> returns a session id based on uuid
- upload_music() -> lets you upload a music file in any music format suported by ffmpeg. returns the filepath where this song is saved
- play_audio() -> plays an audiofile that is on the backend by giving filepath
- mashup_two_songs(vocals_path, instrumental_path) -> given two filepaths for uploaded songs create a mashup. returns the filepath for the mashup.


this should be all that is neccecary to create a front end. The work flow is:
1. obtain session_id
2. upload two songs, keep track in the front end of which path the user wants to be vocals and which path the user wants to be instrumental.
3. after each song upload display the preprocessed song on the frontend and let the user play the song (if it turns out the back-end does not support playback and mashing up at the same time avoid it for now and let me know) 
3. call mashup two songs on the correct order of filepaths
