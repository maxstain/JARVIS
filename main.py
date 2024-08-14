"""
# This project is made by Firas CHABCHOUB
# Date: 16/05/2024
# Description: This is an AI project that uses the OpenAI GPT-3 API
# to generate text based on the user's voice commands
# The project is divided into 3 main parts:
# 1. Speech to text conversion
# 2. Text to text conversion using GPT-3
# 3. Text to speech conversion
# The project uses the following libraries:
# - SpeechRecognition
# - pyttsx3
# - OpenAI GPT-3 API
# - requests
# - nltk
# - spacy
# - google-cloud-speech
# - pyaudio
# - tensorflow
# - torch
# The project is made for educational purposes only
# Project is still in progress
# Project name: J.A.R.V.I.S
# All rights reserved to Firas CHABCHOUB 2024
"""

import os
import sys
import time
import random

if sys.version_info[0] < 3:
    raise Exception("Python 3 or a more recent version is required.")
try:
    import requests
    import pyttsx3
    import speech_recognition
    import nltk
    import spacy
    import pyaudio
    import tensorflow
    import google_cloud_speech
    import torch
    import openai
except ImportError:
    print("Some libraries are missing, installing them now...")
    os.system("pip install -r requirements.txt")
    print("All libraries are installed successfully")

import requests
import pyttsx3
import speech_recognition as sr
import nltk
import spacy
import openai
from openai import OpenAI

print("About to download necessary NLTK resources, This may take a while...")
nltk.download('all')
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("Downloading the English model for spaCy...")
    os.system("python -m spacy download en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

conversation_history = []
current_keywords = set()
credentials_json = "./credentials.json"

# OpenAI API
client = OpenAI(
    # api_key=os.environ.get("OPENAI_API_KEY")
    api_key="sk-proj-U4v8yt3KdK2Te27Py3n1T3BlbkFJ4KksQrOFaONz1QoPTnPp"
)


def extract_keywords(text):
    keywords = set()
    doc = nlp(text)
    for token in doc.ents:
        keywords.add(token.text)
    # Access sentiment score directly
    sentiment_score = doc.sentiment  # This will be a numerical value

    if sentiment_score > 0:
        keywords.add("positive")
    elif sentiment_score < 0:
        keywords.add("negative")
    return keywords


def update_conversation_history(user_input, ai_response):
    global current_keywords
    # Extract keywords from user_input (using NLP techniques)
    keywords = extract_keywords(user_input)
    current_keywords.update(keywords)
    conversation_history.append((user_input, ai_response, keywords))


def get_conversation_history():
    return conversation_history


def get_current_keywords():
    return current_keywords


def get_response(text: str):
    # url = "https://chat-gpt26.p.rapidapi.com/"
    # url = "https://chatgpt-42.p.rapidapi.com/geminipro"
    url = "https://gemini-pro-ai.p.rapidapi.com/"

    conversation_history = get_conversation_history()
    current_keywords = get_current_keywords()

    # Consider conversation history and keywords when crafting the prompt
    prompt = ""
    if conversation_history and current_keywords and len(conversation_history) > 1 and len(current_keywords) > 1:
        prompt = f"In the conversation so far, the user has mentioned {current_keywords}. "
        last_user_input, _, _ = conversation_history[-1]
        prompt += f"Their last question was '{last_user_input}'. "
        prompt += f"Considering this context and the current input '{text}', "
        prompt += f"they might be interested in..."
    # Gemini Pro API payload format
    payload = {"contents": [
        {
            "role": "user",
            "parts": [{"text": prompt + text}]
        }
    ]}
    # headers = {
    #     "content-type": "application/json",
    #     "X-RapidAPI-Key": "61a70198edmshb08f1e98e9d907dp178f22jsn8ec21a1badf8",
    #     "X-RapidAPI-Host": "chatgpt-42.p.rapidapi.com"
    # }
    ### Gemini Pro API headers
    headers = {
        "x-rapidapi-key": "5b8211c40emsh56871076a0cd443p1623b5jsnf1a9f4569391",
        "x-rapidapi-host": "gemini-pro-ai.p.rapidapi.com",
        "Content-Type": "application/json"
    }

    # Works with RapidAPI
    response = requests.post(url, json=payload, headers=headers)
    # Works with OpenAI API V2
    # response = client.chat.completions.create(
    #     model="gpt-3.5-turbo",
    #     messages=[
    #         {
    #             "role": "user",
    #             "content": prompt + text
    #         }
    #     ],
    # )

    print(response.json())
    return response.json()


def text_to_speech(phrase: str):
    print("JARVIS: ", phrase)
    engine = pyttsx3.init()
    engine.say(phrase)
    engine.runAndWait()


def wait():
    time.sleep(2)


def get_weather_forecast(text: str):
    """
    This function fetches the specific weather information
    from the weather API according to the city given
    :param text:
    :return :
    """
    # Extract the country from the text
    doc = nlp(text)
    location = "Tunis"
    for ent in doc.ents:
        if ent.label_ == "GPE":
            location = ent.text
            break
    # Call a weather API or use a pre-defined response about weather
    url = f"https://api.weatherapi.com/v1/current.json?key=9140b212475c4b9f920175743241605&q={location}&aqi=yes"
    response = requests.get(url)
    data = response.json()
    temperature = data['current']['temp_c']
    condition = data['current']['condition']['text']
    return f"The weather in {location} is {condition} today. The temperature is {temperature} degrees Celsius."


def main():
    text_to_speech("Hello sir, I am JARVIS, your personal assistant. How can I help you today ?")
    while True:
        r = sr.Recognizer()
        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source)
            print("Listening...")
            audio = r.listen(source)
            try:
                text = r.recognize_google(audio)
                # Use Google Cloud Speech API for better accuracy TODO: FIX THIS
                # text = r.recognize_google_cloud(audio, language="en-US",
                #                                credentials_json=credentials_json)
                print("You: ", text)
                if text == "exit" or "goodbye" in text or "bye" in text or "see ya" in text or "see you" in text or text == "quit":
                    text_to_speech("Goodbye sir, have a nice day.")
                    break
                elif "weather" in text.lower():
                    # Call a weather API or use a pre-defined response about weather
                    custom_response = "Sure, here's the weather forecast..."
                    text_to_speech(custom_response)
                    custom_response = get_weather_forecast(text.lower())
                elif "history" in text.lower():
                    custom_response = "Sure, here's the conversation history..."
                    text_to_speech(custom_response)
                    for i, (user_input, ai_response, _) in enumerate(get_conversation_history()):
                        print(f"User: {user_input}")
                        print(f"JARVIS: {ai_response}")
                        if i == 5:
                            break
                    custom_response = "That's all for now."
                elif "thank you" in text.lower() or "thanks" in text.lower():
                    custom_response = "It's my pleasure, sir."
                    text_to_speech(custom_response)
                else:
                    tokens = nltk.word_tokenize(text)
                    text = nltk.pos_tag(tokens)[0][0].lower()
                    doc = nlp(text)
                    for token in doc:
                        if token.pos_ == "VERB":
                            text = token.text
                            break
                    response = get_response(text)
                    if 'message' in response:
                        ai_text = response['message']['content']
                    elif 'choices' in response:
                        ai_text = response['choices'][0]['message']['content']  # Access content from choices
                    else:
                        ai_text = response['result']
                    print("JARVIS: ", ai_text)
                    custom_response = ai_text
                text_to_speech(custom_response)
                update_conversation_history(text, custom_response)
            except sr.UnknownValueError as e:
                text_to_speech("Sorry, I didn't get that.")
                print(e)
            except sr.RequestError as e:
                text_to_speech("Sorry, I am not able to process your request.")
                print(e)
            except requests.exceptions.RequestException as e:
                text_to_speech("Sorry, I am not able to process your request.")
                print(e)
            except nltk.corpus.reader.util.MissingCorpusError as e:
                text_to_speech("Sorry, I need to download additional resources. Downloading now...")
                print(e)
                nltk.download('all')
            except KeyError as e:
                text_to_speech("Sorry, I am not able to process your request.")
                print(e)
            except Exception as e:
                text_to_speech("Sorry, I am not able to process your request.")
                print(e)


if __name__ == '__main__':
    main()
