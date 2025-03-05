from api_keys import GEMINI_API_KEY
from google import genai

class gemini(genai.Client):

    def __init__(self,api_key=GEMINI_API_KEY) ->None:
        super().__init__(api_key=api_key)
    
    def gen(self,text:str) -> str:
        self.response=self.models.generate_content(model="gemini-2.0-flash", contents=text)
        return self.response.text
