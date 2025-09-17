import streamlit as st
import google.generativeai as genai

# --- PASSWORD PROTECTION ---
def check_password():
    """Returns `True` if the user has the correct password."""
    # Initialize session state if it doesn't exist
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False

    # Show password input with autocomplete enabled
    password = st.text_input(
        "Password", 
        type="password", 
        autocomplete="current-password" # This line is the new addition
    )
    
    # Show confirm button
    if st.button("Confirm"):
        # Check if the entered password is correct
        if password == st.secrets["APP_PASSWORD"]:
            st.session_state["password_correct"] = True
            # Rerun the script to hide the login form and show the app
            st.rerun() 
        else:
            st.error("😕 Password incorrect")
            
    # Return the password status
    return st.session_state["password_correct"]


if not check_password():
    st.stop() # Do not render the rest of the app if password is not correct

# --- CONFIGURATION ---
st.set_page_config(
    page_title="Stormlight Companion",
    page_icon="📚"
)

# --- CORE LOGIC ---
def generate_live_response(user_question, spoiler_level):
    """Generates a response by prompting an AI with web search capabilities."""
    master_prompt = f"""
    **Your Role:** You are a spoiler-aware reading companion for Brandon Sanderson's "The Stormlight Archive." Your name is Pattern.
    **Your Core Task:** You will answer the user's question by performing a live web search limited **exclusively** to the `coppermind.net` website. You must not use any other websites or your own pre-existing knowledge.
    **CRITICAL SPOILER CONSTRAINT:**
    The user has only read up to and including the book **{spoiler_level}**.
    When you browse a Coppermind page, you must strictly adhere to their spoiler warnings. If a section of text is marked as a spoiler for a book beyond the user's reading level, you **MUST NOT** read, use, or mention any information from that section.
    **Instructions:**
    1. Receive the user's question.
    2. Formulate search queries for `coppermind.net`.
    3. Browse the search results and find the most relevant article(s).
    4. Read the article(s), carefully ignoring sections marked as spoilers beyond the user's reading level.
    5. Synthesize an answer using ONLY the information you were able to access.
    6. **NEW RULE:** If the user asks for a theory or prediction about future events, you are allowed to speculate. You **must** clearly state that you are guessing and base your theory **strictly** on the information available within the user's read books. Use phrases like "Based on what we've seen so far, one might guess that..." or "Mmm, a fascinating pattern. Perhaps it means..." Do not present theories as facts.
    7. If you cannot find any relevant information without accessing spoilered sections, you must state: "Mmm, answering that would require knowledge from a book you have not yet read. I cannot say more."
    **User's Question:**
    {user_question}
    """
    model = genai.GenerativeModel(model_name='gemini-1.5-pro-latest')
    response = model.generate_content(master_prompt)
    return response.text

# --- UI & APP FLOW ---
st.title("📚 Stormlight Companion")
st.caption("Live-searching the Coppermind with a spoiler-aware assistant.")

# UPDATED LIST OF BOOKS
spoiler_level = st.selectbox(
    "What is the last book you have completed?",
    ("The Way of Kings", "Words of Radiance", "Oathbringer", "Rhythm of War", "Wind and Truth")
)
st.info(f"Companion is configured with knowledge up to **{spoiler_level}**.")

# Configure the Google AI client with the secret key
try:
    genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])
except Exception as e:
    st.error("Could not configure Google AI. Have you added your API key to .streamlit/secrets.toml?")
    st.stop()

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display previous messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Handle new user input
if prompt := st.chat_input("Ask about characters, places, or theories..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Mmm, searching the patterns..."):
            response = generate_live_response(prompt, spoiler_level)
            st.markdown(response)
    
    st.session_state.messages.append({"role": "assistant", "content": response})
    
# --- ATTRIBUTION ---
st.markdown("---")
st.markdown("Knowledge sourced from [The Coppermind Wiki](https://coppermind.net), which is licensed under [CC BY-NC-SA 3.0](https://creativecommons.org/licenses/by-nc-sa/3.0/).")