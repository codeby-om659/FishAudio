from fastapi import FastAPI,HTTPException,status
import mysql.connector
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import requests
from datetime import datetime
from fastapi.responses import Response

app= FastAPI(title="AI Voice TimeTable API")
FISH_AUDIO_API_KEY=""
MYSQL_CONFIG={
    "host":"localhost",
    "user":"root",#my sql username
    "password":"omverma67895@",#
    "database":"timetable_db"
}

def get_db():
    try:
        return mysql.connector.connect(**MYSQL_CONFIG)
    except mysql.connector.Error as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database ConnectionError:{err}"
        )


class UserCreate(BaseModel):
    name:str
    email:str
    prefered_language:str


class TaskCreate(BaseModel):
    user_id:int
    title:str
    description:str
    scheduled_time:datetime



#----API ENDPOINTS----
@app.get("/")
def home():
    return  {"msg":"backend is active"}
#1.CREATE NEW USER
@app.post("/users")
def crate_user(user:UserCreate):
    db=get_db()
    cursor=db.cursor()

    query="""
    INSERT INTO users (name,email,prefered_language)
    VALUE(%s,%s,%s)
    """
    Value=(
        user.name,
        user.email,
        user.prefered_language
    )
    try:
        cursor.execute(query,Value)
        db.commit()
        return {"status":"success","id":id,"message":"new user succesfully registered","name":user.name}
    except mysql.connector.Error as err:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"registration failed:{err}")
    finally:
        cursor.close()
        db.close()

#specific user ke liye task add kare
@app.post("/tasks")
def create_task(task:TaskCreate):
    db=get_db()
    cursor=db.cursor()
    try:
        cursor.execute("SELECT id FROM users WHERE id=%s",(task.user_id,))
        existing_user=cursor.fetchone()
        if not existing_user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"user id {task.user_id} not found")
        # step B :task insert kare
        query="""
        INSERT INTO tasks(user_id,title,description,scheduled_time)
        value(%s,%s,%s,%s)
        """
        value=(
            task.user_id,
            task.title,
            task.description,
            task.scheduled_time
        )
        cursor.execute(query,value)
        db.commit()
        task_id=cursor.lastrowid
        return {"id":task_id ,"user_id":task.user_id,"title":task.title,"message":"task added successfully"}
    except mysql.connector.Error as err:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"failed:{err}")
    finally:
        cursor.close()
        db.close()

#kisi specific user ke sare task fetch karne ke liye
@app.get("/users/{user_id}/task")
def get_user_task(user_id:int):
    db=get_db()
    cursor=db.cursor(dictionary=True)
    try:
        query=" SELECT * FROM tasks WHERE user_id=%s ORDER BY scheduled_time ASC"
        cursor.execute(query,(user_id,))
        result=cursor.fetchall()
        return {"msg":"all done","data":result}
    except mysql.connector.Error as err:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"failed{err}")
    
    finally:
        cursor.close()
        db.close()
#4 fish aaaaaudio api se Dynamic voice
@app.get("/task/{task_id}/voice-remainder")
def generate_voice_remiander(task_id:int):
    db=get_db()
    cursor=db.cursor(dictionary=True)
    try:
        query="""
        SELECT tasks.title,tasks.scheduled_time,users.name
        FROM tasks
        JOIN users ON tasks.user_id=users.id
        wHERE tasks.id=%s
        """
        cursor.execute(query,(task_id,))
        task_data=cursor.fetchone()

        if not task_data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail=f"Task not found")
        # Dynamic Scrips task
        formatted_time=task_data["scheduled_time"].strftime("%I:%M %p")
        prompt_text=f"Suno{task_data['name']}! Aapka task{task_data['title']}{formatted_time} baje schedule hai.kripya isse pura kare."

    #fish aaaaaaaaudio api reequest
        url="https://api.fish.audio/v1/tts"
        headers={
            "Authorization":"Bearer sk-fish-HabYz6HcbpCqQFuZzuQq65l4SCSGMd8KkYTQuMLvWQs",
            "Content-Type":"applicaton/json"
        }
        payload={
            "text":prompt_text,
            "format":"mp3"
        }
        response=requests.post(url,json=payload,headers=headers)

        if response.status_code==200:
            return Response(content=response.content,media_type="audio/mpeg")
        else:
            raise HTTPException(
                status_code=response.status_code,
                detail=f"Fish Audio Error:{response.text}"
            )
    finally:
        cursor.close()
        db.close()

        
