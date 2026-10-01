import streamlit as st
from google import genai
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="Snap & Study",
    page_icon="📚"
)


# =========================================================
# GEMINI API
# =========================================================

GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]

client = genai.Client(
    api_key=GEMINI_API_KEY
)


# =========================================================
# PAGE TITLE
# =========================================================

st.title("📚 Snap & Study")
st.write("Your AI Study Assistant")


# =========================================================
# SESSION STATE
# =========================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "study_context" not in st.session_state:
    st.session_state.study_context = ""

if "latest_answer" not in st.session_state:
    st.session_state.latest_answer = ""


# =========================================================
# DISPLAY CHAT HISTORY
# =========================================================

for message in st.session_state.messages:

    with st.chat_message(message["role"]):
        st.write(message["content"])


# =========================================================
# IMAGE UPLOAD
# =========================================================

image = st.file_uploader(
    "📷 Upload your study image",
    type=["jpg", "jpeg", "png"]
)


# =========================================================
# ANALYZE IMAGE
# =========================================================

if image:

    if st.button("🔍 Analyze Image"):

        contents = [
            """
You are a study assistant.

Analyze the uploaded study image.

Identify the topic shown in the image.

Explain the topic as a 5-mark
Anna University examination answer.

Use simple English.

Give the answer in this structure:

1. Definition
2. Key Points
3. Working / Explanation
4. Advantages / Applications
5. Conclusion
"""
        ]

        contents.append(
            genai.types.Part.from_bytes(
                data=image.getvalue(),
                mime_type=image.type
            )
        )


        # =================================================
        # GEMINI REQUEST
        # =================================================

        answer = None

        for attempt in range(3):

            try:

                response = client.models.generate_content(
                    model="gemini-3.5-flash-lite",
                    contents=contents
                )

                answer = response.text

                break

            except Exception as e:

                error = str(e)

                if "503" in error and attempt < 2:

                    time.sleep(3)

                else:

                    answer = (
                        "❌ Gemini Error:\n\n"
                        + error
                    )


        # =================================================
        # STORE STUDY CONTEXT
        # =================================================

        # Only store a real AI answer.
        if answer and not answer.startswith("❌ Gemini Error"):

            st.session_state.study_context = answer

            st.session_state.latest_answer = answer


        # =================================================
        # SAVE CHAT
        # =================================================

        st.session_state.messages.append(
            {
                "role": "user",
                "content": "📷 I uploaded a study image."
            }
        )

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": answer
            }
        )


        # =================================================
        # SHOW ANSWER
        # =================================================

        st.write("### 🤖 5-Mark Answer")

        st.write(answer)


# =========================================================
# EMAIL FEATURE
# =========================================================

# Email section appears only when we have a real AI answer.

if st.session_state.latest_answer:

    st.divider()

    st.subheader("📧 Send Explanation by Email")

    receiver_email = st.text_input(
        "Enter the email address to receive the explanation"
    )


    if st.button("📨 Send Email"):

        if receiver_email.strip() == "":

            st.warning(
                "Please enter a receiver email address."
            )

        else:

            try:

                # =================================================
                # GET GMAIL DETAILS FROM SECRETS
                # =================================================

                sender_email = st.secrets["GMAIL_ADDRESS"]

                app_password = st.secrets[
                    "GMAIL_APP_PASSWORD"
                ]


                # =================================================
                # EMAIL CONTENT
                # =================================================

                subject = "Snap & Study - AI Study Explanation"

                body = f"""
Hello,

Here is your study explanation from Snap & Study.

----------------------------------------

{st.session_state.latest_answer}

----------------------------------------

Generated by Snap & Study.
"""


                # =================================================
                # CREATE EMAIL
                # =================================================

                message = MIMEMultipart()

                message["From"] = sender_email

                message["To"] = receiver_email

                message["Subject"] = subject

                message.attach(
                    MIMEText(body, "plain")
                )


                # =================================================
                # CONNECT TO GMAIL SMTP
                # =================================================

                server = smtplib.SMTP(
                    "smtp.gmail.com",
                    587
                )

                server.starttls()


                # =================================================
                # LOGIN
                # =================================================

                server.login(
                    sender_email,
                    app_password
                )


                # =================================================
                # SEND EMAIL
                # =================================================

                server.sendmail(
                    sender_email,
                    receiver_email,
                    message.as_string()
                )


                # =================================================
                # CLOSE SERVER
                # =================================================

                server.quit()


                st.success(
                    "✅ Explanation sent successfully!"
                )


            except Exception as e:

                st.error(
                    "❌ Email sending failed:\n\n"
                    + str(e)
                )


# =========================================================
# CONTINUE CONVERSATION
# =========================================================

question = st.chat_input(
    "Ask a follow-up question..."
)


if question:

    # =====================================================
    # CREATE CONTEXT
    # =====================================================

    if st.session_state.study_context:

        prompt = f"""
We are studying the topic from the uploaded image.

Here is the previous AI explanation:

{st.session_state.study_context}

The student now asks:

{question}

Answer the student's question based on
the study topic above.

Use simple English.

If suitable, give an exam-oriented answer.
"""

    else:

        prompt = question


    # =====================================================
    # GEMINI REQUEST
    # =====================================================

    try:

        response = client.models.generate_content(
            model="gemini-3.5-flash-lite",
            contents=prompt
        )

        answer = response.text


        # =================================================
        # SAVE USER QUESTION
        # =================================================

        st.session_state.messages.append(
            {
                "role": "user",
                "content": question
            }
        )


        # =================================================
        # SAVE AI ANSWER
        # =================================================

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": answer
            }
        )


        # =================================================
        # UPDATE CONTEXT
        # =================================================

        st.session_state.study_context += (
            "\n\nStudent Question:\n"
            + question
            + "\n\nAI Answer:\n"
            + answer
        )


        # =================================================
        # UPDATE LATEST ANSWER
        # =================================================

        st.session_state.latest_answer = answer


        # =================================================
        # DISPLAY ANSWER
        # =================================================

        st.write("### 🤖 AI Answer")

        st.write(answer)


    except Exception as e:

        st.error(
            "❌ Gemini Error:\n\n"
            + str(e)
        )