import json
import nextcord
import time
import datetime
import asyncio


REMINDER_FILE="reminders.json"

def convert_to_timestamp(date_str):
    """
    Converts a date string in 'DD-MM-YYYY HH:MM' format to a Unix timestamp.
    """
    dt = datetime.datetime.strptime(date_str, "%d-%m-%Y %H:%M")
    timestamp = time.mktime(dt.timetuple())
    return timestamp


def seconds_from_now(inp:str):
    '''
    Enter Days Hours Minutes
    eg: 0 1 00 is 1 hour
    '''

    params=map(int,inp.split())
    seconds=params[0]*3600*24
    seconds+=params[1]*3600
    seconds+params[2]

    return params

class timekeeper():
    def __init__(self,bot):
        try:
            with open(REMINDER_FILE) as f:
                reminders=json.load(f)
                
        except:
            with open(REMINDER_FILE,"w") as f:
                reminders=[]
        for i in range(len(reminders)-1,-1,-1):
            if time.time()>reminders[i]["time_till_reminder"]:
                del reminders[i]
        
        self.reminders=sorted(reminders,key=lambda x:x["time_till_reminder"])
        self.bot=bot
        

    async def remind(self):

        await asyncio.sleep(self.reminders[0]["time_till_reminder"]-time.time())
        await self.bot.remind(self.reminders[0])
        del self.reminders[0]
        with open(REMINDER_FILE,'w') as f:
            json.dump(self.reminders,f)
        if self.reminders!=[]:
            await self.remind()