from fastapi import FastAPI, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import shutil, subprocess, os, uuid, time
from pydub import AudioSegment
import aiofiles

from apscheduler.schedulers.background import BackgroundScheduler

# === Utility Functions ===
from utils import preprocess_song

app = FastAPI()
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
USER_FILES_DIR = os.path.join(BASE_DIR, "user_files")
os.makedirs(USER_FILES_DIR, exist_ok=True)
app.mount("/user_files", StaticFiles(directory=USER_FILES_DIR), name="user_files")

# === Cleanup Task ===
EXPIRATION_TIME_SECONDS = 60 * 60  # 1 hour, customize as needed

def cleanup_expired_sessions():
    now = time.time()
    for session_folder in os.listdir(USER_FILES_DIR):
        session_path = os.path.join(USER_FILES_DIR, session_folder)
        if os.path.isdir(session_path):
            folder_age = now - os.path.getmtime(session_path)
            if folder_age > EXPIRATION_TIME_SECONDS:
                print(f"[Cleanup] Deleting expired session: {session_folder}")
                shutil.rmtree(session_path, ignore_errors=True)

# === Scheduler Setup ===
scheduler = BackgroundScheduler()
scheduler.add_job(cleanup_expired_sessions, 'interval', minutes=30)  # every 30 minutes
scheduler.start()

# === FastAPI Endpoints ===
@app.get("/")
async def root():
    return {"message": "Welcome to the Mashup API.", 
            "user_files_dir": USER_FILES_DIR}

@app.get("/session_id")
async def get_session_id():
    """
    Generate a unique session ID for each request.
    This can be used to track user sessions and files.
    """
    return str(uuid.uuid4())

@app.post("/upload", response_model=dict)
async def upload_music(uploaded_file: UploadFile, session_id: str):
    session_dir = os.path.join(USER_FILES_DIR, session_id)
    os.makedirs(session_dir, exist_ok=True)

    original_path = os.path.join(session_dir, uploaded_file.filename)

    # Asynchronously save the file to disk
    async with aiofiles.open(original_path, 'wb') as out_file:
        while content := await uploaded_file.read(1024 * 1024):  # read in 1 MB chunks
            await out_file.write(content)

    # Convert file to WAV (sync is fine for CPU-bound tasks)
    wav_path = os.path.splitext(original_path)[0] + ".wav"
    audio = AudioSegment.from_file(original_path)
    audio.export(wav_path, format="wav")

    basename = os.path.basename(wav_path)
    processed_wav_path = os.path.join(session_dir, basename)
    preprocess_song(wav_path, output_file=processed_wav_path)

    return {
        "filename": basename,
        "url": processed_wav_path,
        "session_id": session_id
    }

@app.get("/play/{session_id}/{file_name}")
async def play_audio(session_id: str, file_base_name: str):
    """
    session_id: uuid of the session, should be returned when uploading a file
    file_base_name: name of the file to play, e.g. "processed.wav"
    """

    file_location = os.path.join(USER_FILES_DIR, session_id, file_base_name)
    return FileResponse(file_location, media_type="audio/wav")


@app.post("/mashup", response_model=dict)
def mashup_two_songs(file_path_vocals: str, file_path_instrumental: str, session_id: str, speed: str = "fast", key_shift: bool = True):
    """
    file_path_vocals: path to the song file that will be used for vocals
    file_path_instrumental: path to the song file that will be used for instrumental
    speed: "fast" or "slow", determines the speed of the processing

    this is the large operation with neural nets, it takes a while and the pytorch functions do not support async
    The point of this endpoint is:
    after the user has uploaded two files, and toggled on to be the vocal track and one to be the instrumental track,
    they can call this endpoint to create a mashup of the two files.
    """
    #file where the final mashup will be saved
    mashup_file = os.path.join(USER_FILES_DIR, session_id, "mashup_result.wav")

    audio1 = AudioSegment.from_file(file_path_vocals)
    audio2 = AudioSegment.from_file(file_path_instrumental)

    # Overlay audio1 en audio2 (zet audio2 bovenop audio1)
    combined_audio = audio1.overlay(audio2)
    combined_audio.export(mashup_file, format="wav")


    return {
        "message": "Mashup created successfully.",
        "mashup_file": mashup_file
    }

