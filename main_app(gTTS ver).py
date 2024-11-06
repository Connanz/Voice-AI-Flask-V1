from flask import Flask, request, jsonify, render_template, send_file
import google.generativeai as genai
from gtts import gTTS
import os
from dotenv import load_dotenv
import tempfile

# Untuk memperkenalkan nama app yang kita buat agar dapat di jalankan atau di run melalui terminal python.
app = Flask(__name__)
app.secret_key = 'Conannz'

# Untuk mengambil Gemini API key yang disimpan di file .env
load_dotenv()
gemini_api_key = os.getenv("GEMINI_API_KEY")

# Untuk konfigurasi Gemini API key.
genai.configure(api_key=gemini_api_key)

def gemini_ai(user_query):
    # Mengenerate sebuah response menggunakan Gemini API key.
    response_text = generate_response(user_query)
    
    return response_text

def generate_response(user_query):
    # Memastikan bahwa api key gemini sudah di set.
    if not gemini_api_key:
        raise ValueError("GEMINI_API_KEY environment variable is not set")
    
    # Instruksi prompt secara khusus kepada ai agar sesuai dengan yang kita inginkan.
    prompt = (f"""
            Jawablah pertanyaan dalam bahasa Indonesia dengan gaya formal serta sopan dan tanpa emoji.
            Ucapkan salam kepada pengguna secara konsisten menggunakan kata-kata maupun kalimat yang sama. 
            Jelaskan kepada para pengguna dengan singkat dan ringkas.
            Jangan bertanya kembali kepada user atau pengguna kecuali mereka meminta AI untuk bertanya balik.
            Hindari mengulangi kata-kata atau kalimat yang sama.
            Pertanyaan: "{user_query}"
            """)
    
    # Mengenerate konten menggunakan model yang dikonfigurasi.
    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt, stream=False)
    
    # Memfilter emoji dari response text agar AI tidak menjawab menggunakan emoji, lambang, dan sebagainya.
    response_text = response.text if response.parts else ""
    response_text = ''.join(char for char in response_text if char.isalnum() or char.isspace() or char in '.,')
    
    if response_text:
        return response_text
    else:
        raise ValueError("Empty response from Gemini API")

# Buat model
generation_config = {
  "temperature": 0.2, # Kreativitas yang bisa digunakan oleh AI.
  "top_p": 0.50, # Pemilihan kata yang masuk akal untuk digunakan selanjutnya dalam menjawab pertanyaan user oleh AI.
  "top_k": 48, # Maksimal kata berbeda yang dapat dikeluarkan oleh AI.
  "max_output_tokens": 400, # Maksimal token yang dapat dikeluarkan oleh AI.
  "response_mime_type": "text/plain", # Agar respon yang dihasilkan adalah text.
}

model = genai.GenerativeModel(
  model_name="gemini-1.5-flash",
  generation_config=generation_config,
)

chat_session = model.start_chat(
  history=[
  ]
)

response = chat_session.send_message(f"""
                                     Gunakan ucapan balasan yang konsisten yaitu kata-kata maupun kalimat yang sama kepada user maupun pengguna.
                                     Gunakan kata-kata maupun kalimat sesuai dengan waktu dari pengguna atau user""")
# Berfungsi untuk mengatur respon suara dari AI yang menjawab pertanyaan user menggunakan gTTS dengan beberapa konfigurasi tambahan seperti bahasa yang digunakan adalah bahasa Indonesia.
def speak_response(response_text, lang="id"):
    print("AI says:", response_text)
    tts = gTTS(response_text, lang=lang)

    # Simpan file suara secara sementara.
    temp_audio_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tts.save(temp_audio_file.name)
    return temp_audio_file.name

# Rute untuk bertanya pada AI.
@app.route('/ask', methods=['GET'])
def ask():
    user_query = request.args.get('query')
    if not user_query:
        return jsonify({'error': 'No query provided'}), 400
    
    response_text = gemini_ai(user_query)  # Dapatkan respons teks dari AI
    
    # Mengirim respons teks.
    return jsonify({'text_response': response_text})

# Rute untuk membuat file audio berdasarkan teks respons yang sudah dihasilkan.
@app.route('/audio', methods=['GET'])
def audio():
    response_text = request.args.get('text')
    if not response_text:
        return jsonify({'error': 'No text provided'}), 400
    
    audio_file = speak_response(response_text)
    return send_file(audio_file, mimetype="audio/mpeg")

# Rute Utama dari projek(voice-ai-real-time) ini atau sebagai tampilan utama html.
@app.route('/')
def indexidsnz():
    return render_template('indexidsnz.html')

# Bagian untuk menjalankan aplikasi, berkaitan dengan nama app pada bagian atas kodingan ini.
if __name__ == "__main__":
    app.run(host='0.0.0.0', debug=True)
# kodingan beserta keterangan ini ditulis oleh Richard a.k.a Connanz.
