from app.schemas.db.chat import GetSummary
from app.services.db.chat import get_original_text, get_chat_messages
from app.utils.logger import get_logger
from sqlmodel import Session
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter
import html
import markdown


logger = get_logger(__name__)


def build_export_chat_content(details: GetSummary, session: Session):
    try:
        logger.debug("Starting to build the chat content for the pdf")

        text_data = get_original_text(details=details, session=session)

        if not text_data:
            raise ValueError("No summary or original data found")

        if "summary_text" not in text_data:
            raise ValueError("No summary text found")

        if "original_text" not in text_data:
            raise ValueError("No original text found")

        qna_data = get_chat_messages(details=details, session=session)

        export_data = {
            "original_text": text_data["original_text"],
            "summary_text": text_data["summary_text"],
            "qna": [] if len(qna_data) == 0 else qna_data,
            "title": getattr(text_data, "title", "") or "",
        }

        return export_data
    except ValueError:
        raise
    except Exception as e:
        logger.error(
            f"Failed to build the chat content for the pdf,error:{str(e)}",
            exc_info=True,
        )
        raise Exception("Failed to build the formated content for the pdf generation")


def safe_text(value: str) -> str:
    if not value:
        return ""
    # Escape special XML/HTML characters
    return html.escape(value)


def md_to_reportlab(text: str):
    if not text:
        return ""

    # 1. Escape dangerous HTML from user input
    safe = html.escape(text)

    # 2. Convert markdown to HTML
    html_text = markdown.markdown(safe)

    # 3. Return raw HTML (no escaping)
    return html_text


def generate_chat_pdf(content: dict, output_path: str):
    doc = SimpleDocTemplate(output_path, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    # Title
    title = safe_text(content.get("title", "Chat Export"))
    story.append(Paragraph(title, styles["Title"]))
    story.append(Spacer(1, 20))

    # Original text
    story.append(Paragraph("Original Text", styles["Heading2"]))
    story.append(
        Paragraph(safe_text(content.get("original_text", "")), styles["BodyText"])
    )
    story.append(Spacer(1, 12))

    # Summary
    story.append(Paragraph("Summary", styles["Heading2"]))
    story.append(
        Paragraph(md_to_reportlab(content.get("summary_text", "")), styles["BodyText"])
    )
    story.append(Spacer(1, 12))

    # Conversation
    story.append(Paragraph("Conversation", styles["Heading2"]))

    for item in content.get("qna", []):
        question_obj = item.get("question")
        answer_obj = item.get("responses")[0]

        question_text = md_to_reportlab(getattr(question_obj, "content", ""))
        answer_text = md_to_reportlab(getattr(answer_obj, "content", ""))

        story.append(Paragraph(f"Q: {question_text}", styles["BodyText"]))
        story.append(Paragraph(f"A: {answer_text}", styles["BodyText"]))
        story.append(Spacer(1, 10))

    doc.build(story)
