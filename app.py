import streamlit as st
from google import genai
from email.message import EmailMessage
import smtplib


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Suriya AI Chatbot",
    page_icon="🤖",
    layout="wide"
)


# ============================================================
# GEMINI CONFIGURATION
# ============================================================

client = genai.Client(
    api_key=st.secrets["GEMINI_API_KEY"]
)

MODEL_NAME = "gemini-3.5-flash-lite"


# ============================================================
# SESSION STATE
# ============================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "image_explanation" not in st.session_state:
    st.session_state.image_explanation = ""

if "uploaded_image" not in st.session_state:
    st.session_state.uploaded_image = None


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.title("🤖 Suriya AI")

    st.caption("Your AI Study Assistant")

    st.divider()

    st.subheader("✨ Features")

    st.write("📷 Image Analysis")
    st.write("🧠 AI Explanation")
    st.write("💬 Follow-up Chat")
    st.write("📚 Study Assistance")
    st.write("📧 Email Explanation")

    st.divider()

    st.subheader("🚀 How it works")

    st.write("1️⃣ Upload your study image")
    st.write("2️⃣ Click Analyze Image")
    st.write("3️⃣ Read the AI explanation")
    st.write("4️⃣ Ask follow-up questions")
    st.write("5️⃣ Send explanation by email")

    st.divider()

    st.info(
        "Snap a question, diagram, notes, "
        "code or study material and let "
        "Suriya AI explain it."
    )


# ============================================================
# MAIN TITLE
# ============================================================

st.title("🤖 Suriya AI Chatbot")

st.subheader("📚 Snap & Study")

st.write(
    "Your simple AI-powered study assistant. "
    "Upload a question, diagram, notes, code "
    "or other study material and get an easy explanation."
)

st.divider()


# ============================================================
# IMAGE UPLOAD
# ============================================================

st.header("📷 Upload Your Study Material")

uploaded_file = st.file_uploader(
    "Choose an image",
    type=[
        "jpg",
        "jpeg",
        "png",
        "webp"
    ],
    help="Upload a clear image of your study material."
)


# ============================================================
# IMAGE PREVIEW
# ============================================================

if uploaded_file is not None:

    st.subheader("🖼️ Selected Image")

    st.image(
        uploaded_file,
        caption="Your uploaded study material",
        use_container_width=True
    )

    st.write("")

    # ========================================================
    # ANALYZE IMAGE BUTTON
    # ========================================================

    analyze_button = st.button(
        "🔍 Analyze Image",
        type="primary",
        use_container_width=True
    )

    if analyze_button:

        with st.spinner(
            "🧠 Suriya AI is analyzing your image..."
        ):

            try:

                # Convert uploaded image into Gemini input
                image_part = genai.types.Part.from_bytes(
                    data=uploaded_file.getvalue(),
                    mime_type=uploaded_file.type
                )

                # ====================================================
                # DYNAMIC IMAGE PROMPT
                # ====================================================

                image_prompt = """
You are Suriya AI, an AI study assistant.

Analyze the uploaded image carefully.

First identify what the image contains.

It may contain:

- a question
- programming code
- mathematical problem
- diagram
- notes
- definition
- technical concept
- table
- formula
- exam question
- other study material

Then provide an explanation that matches the actual
content of the image.

IMPORTANT:

Do NOT automatically assume that the user wants
a 5-mark answer.

Do NOT force a fixed answer format.

The response should depend on the actual content.

If the image contains a QUESTION:
Solve or explain the question clearly.

If the image contains CODE:
Explain the code, logic and expected output.

If the image contains a DIAGRAM:
Explain the diagram and its important components.

If the image contains NOTES:
Summarize the important points.

If the image contains a MATHEMATICAL PROBLEM:
Solve it step by step.

If the image contains a CONCEPT:
Explain the concept clearly with simple examples.

If the image contains a DEFINITION:
Explain the definition in simple language.

If the image contains a TABLE:
Explain the important information in the table.

Use simple English.

Make the explanation easy for a student to understand.

Use headings or bullet points when they make
the explanation easier to read.

Do not add unrelated information.
"""

                # ====================================================
                # GEMINI IMAGE REQUEST
                # ====================================================

                response = client.models.generate_content(
                    model=MODEL_NAME,
                    contents=[
                        image_part,
                        image_prompt
                    ]
                )

                explanation = response.text

                # ====================================================
                # SAVE RESULT
                # ====================================================

                st.session_state.image_explanation = explanation

                st.session_state.uploaded_image = (
                    uploaded_file.getvalue()
                )

                # Clear previous conversation
                st.session_state.messages = []

                # Add AI explanation to chat history
                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": explanation
                    }
                )

                st.success(
                    "✅ Image analyzed successfully!"
                )

            except Exception as e:

                st.error(
                    "❌ Something went wrong while analyzing the image."
                )

                st.code(str(e))


# ============================================================
# DISPLAY AI EXPLANATION
# ============================================================

if st.session_state.image_explanation:

    st.divider()

    st.header("🧠 Suriya AI Explanation")

    st.write(
        st.session_state.image_explanation
    )


# ============================================================
# FOLLOW-UP CHAT
# ============================================================

st.divider()

st.header("💬 Ask Suriya AI")

if st.session_state.image_explanation:

    st.caption(
        "Ask any follow-up question about the uploaded study material."
    )

else:

    st.info(
        "📷 Upload and analyze an image first. "
        "Then you can ask follow-up questions."
    )


# ============================================================
# DISPLAY CHAT HISTORY
# ============================================================

for message in st.session_state.messages:

    if message["role"] == "user":

        with st.chat_message("user"):

            st.write(
                message["content"]
            )

    elif message["role"] == "assistant":

        with st.chat_message("assistant"):

            st.write(
                message["content"]
            )


# ============================================================
# CHAT INPUT
# ============================================================

user_question = st.chat_input(
    "Ask Suriya AI something..."
)


if user_question:

    # ========================================================
    # SAVE USER MESSAGE
    # ========================================================

    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_question
        }
    )

    # ========================================================
    # DISPLAY USER MESSAGE
    # ========================================================

    with st.chat_message("user"):

        st.write(
            user_question
        )


    # ========================================================
    # CHECK IMAGE
    # ========================================================

    if not st.session_state.image_explanation:

        answer = (
            "📷 Please upload and analyze a study image first. "
            "Then I can answer questions about it."
        )

    else:

        # ====================================================
        # GENERATE FOLLOW-UP ANSWER
        # ====================================================

        with st.spinner(
            "🤖 Suriya AI is thinking..."
        ):

            try:

                chat_prompt = f"""
You are Suriya AI, a helpful AI study assistant.

The student uploaded study material.

Here is the explanation generated from the image:

-----------------------------
{st.session_state.image_explanation}
-----------------------------

The student is now asking:

-----------------------------
{user_question}
-----------------------------

Answer the student's question based on
the uploaded study material and its explanation.

IMPORTANT:

- Do not automatically make the answer a 5-mark answer.
- Answer according to what the student is asking.
- Use simple English.
- Explain step by step when necessary.
- Give examples when useful.
- Keep the explanation student-friendly.
- Do not add unrelated information.
"""

                response = client.models.generate_content(
                    model=MODEL_NAME,
                    contents=chat_prompt
                )

                answer = response.text

            except Exception as e:

                answer = (
                    "❌ Sorry, something went wrong.\n\n"
                    + str(e)
                )


    # ========================================================
    # SAVE AI ANSWER
    # ========================================================

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer
        }
    )


    # ========================================================
    # DISPLAY AI ANSWER
    # ========================================================

    with st.chat_message("assistant"):

        st.write(
            answer
        )


# ============================================================
# EMAIL SECTION
# ============================================================

st.divider()

st.header("📧 Send Explanation by Email")

st.write(
    "You can send the latest AI-generated explanation "
    "to your email."
)


# ============================================================
# EMAIL INPUT
# ============================================================

email_address = st.text_input(
    "Enter your email address",
    placeholder="example@gmail.com"
)


# ============================================================
# SEND EMAIL BUTTON
# ============================================================

send_email_button = st.button(
    "📨 Send Explanation",
    use_container_width=True
)


if send_email_button:

    # ========================================================
    # CHECK EXPLANATION
    # ========================================================

    if not st.session_state.image_explanation:

        st.warning(
            "⚠️ Please analyze an image first."
        )

    # ========================================================
    # CHECK EMAIL
    # ========================================================

    elif not email_address:

        st.warning(
            "⚠️ Please enter your email address."
        )

    else:

        try:

            # ==================================================
            # GET GMAIL SECRETS
            # ==================================================

            sender_email = st.secrets[
                "GMAIL_ADDRESS"
            ]

            app_password = st.secrets[
                "GMAIL_APP_PASSWORD"
            ]


            # ==================================================
            # CREATE EMAIL
            # ==================================================

            msg = EmailMessage()

            msg["Subject"] = (
                "Suriya AI - Study Explanation"
            )

            msg["From"] = sender_email

            msg["To"] = email_address


            # ==================================================
            # EMAIL CONTENT
            # ==================================================

            email_body = f"""
Hello,

Here is your study explanation generated
by Suriya AI.

========================================

{st.session_state.image_explanation}

========================================

Generated by Suriya AI Chatbot.
"""

            msg.set_content(
                email_body
            )


            # ==================================================
            # CONNECT TO GMAIL
            # ==================================================

            with smtplib.SMTP_SSL(
                "smtp.gmail.com",
                465
            ) as smtp:

                smtp.login(
                    sender_email,
                    app_password
                )

                smtp.send_message(
                    msg
                )


            # ==================================================
            # SUCCESS
            # ==================================================

            st.success(
                "✅ Explanation sent successfully!"
            )


        except Exception as e:

            st.error(
                "❌ Email could not be sent."
            )

            st.code(
                str(e)
            )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "🤖 Suriya AI Chatbot | Powered by Gemini AI"
)
