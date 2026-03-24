import re

ALLOWED_IMAGE_TYPES = {
    "image/jpeg",
    "image/jpg",
    "image/png",
    "image/webp",
    "image/bmp",
    "image/gif",
    "image/tiff",
    "image/x-icon",
}

ALLOWED_AUDIO_TYPES = {
    "audio/mpeg",
    "audio/wav",
    "audio/x-wav",
    "audio/flac",
    "audio/ogg",
    "audio/webm",
    "audio/mp4",
}

ALLOWED_VIDEO_TYPES = {
    "video/mp4",
    "video/mov",
    "video/x-matroska",
    "video/x-msvideo",
    "video/webm",
}

ALLOWED_DOC_TYPES = {
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "text/plain",
}

YT_REGEX = re.compile(
    r"^(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:watch\?v=|shorts\/)|youtu\.be\/)([A-Za-z0-9_-]{11})(?:[&#?].*)?$"
)


MODEL_PROMPT_CHUNK_SUMMARY = """Summarize the following text in simple, clear sentences.
Keep only the most important information.
Keep your response under 200 words.

Text:
{context}

Write a brief summary:"""


MODEL_PROMPT_FINAL_SUMMARY = """You are given multiple summaries of different parts of a document.
Combine them into one final summary and title.

For the TITLE:
- Keep it very short (3-7 words)
- Capture the main idea

For the SUMMARY:
- Use short sentences
- Use simple everyday words
- Use bullet points to separate ideas
- Explain in a friendly, calm, supportive tone
- End with a "big idea" sentence in the simplest way possible

Summaries to combine:
{context}

Format your response EXACTLY like this:
TITLE: [your title here]
SUMMARY: [your summary here]"""

MODEL_PROMPT_QUERY = """
You are a kind teacher who helps a child with dyslexia understand things.
Always write with:

- Short, simple sentences (no more than 10 words).
- Easy, everyday words.
- Repetition of important ideas.
- Line breaks or bullet points for clear reading.
- A calm, friendly, and encouraging tone.

There are two parts below:
1️⃣ Question: {question}
2️⃣ Text to use: {context}

Please read both carefully.

Now, answer the **question** using the **text**. 
Make your answer simple and supportive so a dyslexic child can understand it easily.

End with a short “Big Idea” sentence that reminds them of the main point in the simplest way possible.
"""
