from difflib import SequenceMatcher
from gtts import gTTS
import speech_recognition as sr
import emoji
import time
import requests
import json
import asyncio
import os
import playsound
import pygame


url = "http://localhost:11434/api/generate"
file_path = "queue.txt"
voice_path = "voice.mp3"
systemPrompt = "너는 매우 유능한 나의 비서야. 그리고 모든 대답은 반드시 한국어로 대답해 "
breakString = "종료해"
breakAnswer = "다음에 봐요. 안녕"
waitAnswer = "대기중입니다. 얼마든지 물어보세요"
errorAnswer1 = "죄송합니다. 다시 이야기https://developers.naver.com/products/papago/nmt 해주세요"
errorAnswer2 = "Google 음성 인식 서비스에서 결과를 요청할 수 없습니다"
#import sys #-- 텍스트 저장시 사용

pygame.mixer.init()
file = open(file_path, "a", encoding='utf-8')


def makeFile(voiceTxt) :
    global file
    file.write(voiceTxt + "\n")

def ollamaCall(transcript) :
    with open(file_path, 'r', encoding='utf-8') as file :
        # systemPromptList = []
        # systemPromptList.append(systemPrompt)
        # line = file.readlines()
        # file.close()
        prompt = "".join(systemPrompt + transcript)
        data = {
            "model": "llama-bllossom",
            "prompt": prompt
        }
        print("prompt", transcript)
        headers = {'Content-Type': 'application/json'}

        response = requests.post(url, json=data, headers=headers)
        res_text = ''

        if response.status_code == 200:
            json_objects = response.content.decode().strip().split("\n")
            data = [json.loads(obj) for obj in json_objects]
            
            # 변환된 데이터 출력
            for item in data:
                res_text += item['response']
            res_text = emoji.replace_emoji(res_text, replace='')
            makeFile(res_text)
            
        else:
            print("Error:", response.status_code, response.text)
        return res_text

def speak2(text):  #speak 함수 개선중
    try:
        tts = gTTS(text=text, lang='ko')
        tts.save(voice_path)

        pygame.mixer.music.load(voice_path)
        pygame.mixer.music.play()

        while pygame.mixer.music.get_busy():  # 음악 재생 중일 때
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:  # 키 입력 확인
                    if event.key == pygame.K_SPACE:  # 스페이스바를 누르면
                        pygame.mixer.music.stop()  # 음악 중지
                        print("음성 출력이 중단되었습니다.")
                        return

    except Exception as e:
        print(f"음성 출력 중 오류 발생: {e}")
    finally:
        os.remove(voice_path) 


def speak(text) :
    tts = gTTS(text=text, lang='ko')
    tts.save(voice_path)
    playsound.playsound(voice_path)
    os.remove(voice_path)
    
async def hearVoice() :
    r = sr.Recognizer()
    with sr.Microphone() as source:
            print(waitAnswer)
            audio=r.listen(source)
    try:
        transcript=r.recognize_google(audio, language="ko-KR")
        if SequenceMatcher(None, breakString, transcript).ratio() > 0.5 :
            file.close()
            return False

        makeFile(transcript)
        ollamaAnswer = ollamaCall(transcript)
        print (ollamaAnswer)
        speak (ollamaAnswer)

    except sr.UnknownValueError:
        print(errorAnswer1)
    except sr.RequestError as e:
        print(errorAnswer2 + " " + "{0}".format(e))

async def main():
    active = True
    while active:
        if await hearVoice() == False :
            speak(breakAnswer)
            break

if __name__ == "__main__":
    asyncio.run(main())