from groq import Groq

client = Groq(api_key="YOUR_API_KEY")

def generate_plan_ai(tasks):
    prompt = f"Create a daily schedule: {tasks}"
    r = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[{"role":"user","content":prompt}]
    )
    return r.choices[0].message.content

def generate_suggestions_ai(tasks):
    prompt = f"Give productivity tips for: {tasks}"
    r = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[{"role":"user","content":prompt}]
    )
    return r.choices[0].message.content
