import random
import re
from datetime import datetime
from html import escape
from typing import Any, Dict, List

import streamlit as st


GENRES = [
    "Non-Fiction",
    "Fiction",
    "Business",
    "Self-Help",
    "Technology",
    "History",
    "Psychology",
]
LANGUAGES = ["Arabic", "English", "French", "Spanish", "German"]
STYLES = ["Professional", "Academic", "Creative", "Narrative", "Conversational"]


def init_state() -> None:
    st.session_state.setdefault("books", [])


def normalize_words(text: str) -> List[str]:
    words = re.findall(r"[\w\u0600-\u06FF]{4,}", text.lower())
    filtered = [w for w in words if len(w) > 3]
    return filtered[:80]


def pick_keywords(idea: str, limit: int = 18) -> List[str]:
    words = normalize_words(idea)
    score: Dict[str, int] = {}
    for w in words:
        score[w] = score.get(w, 0) + 1
    ranked = sorted(score.items(), key=lambda x: (-x[1], -len(x[0]), x[0]))
    top = [w for w, _ in ranked[:limit]]
    return top or ["الموضوع", "التطوير", "النتائج", "المنهج"]


def generate_outline(title: str, idea: str, genre: str, language: str, num_chapters: int) -> List[Dict[str, Any]]:
    keywords = pick_keywords(idea, limit=max(8, num_chapters + 4))
    chapters = []
    for i in range(num_chapters):
        topic = keywords[i % len(keywords)]
        nxt = keywords[(i + 1) % len(keywords)]
        if language == "Arabic":
            ch_title = f"{topic.title()} بين الرؤية والتطبيق"
            summary = f"يركز هذا الفصل على {topic} ويصلها عمليًا مع {nxt} ضمن إطار واضح يخدم هدف الكتاب."
        else:
            ch_title = f"{topic.title()}: From Vision to Practice"
            summary = f"This chapter connects {topic} with {nxt} through a practical and structured lens."
        chapters.append({"number": i + 1, "title": ch_title, "summary": summary})
    return chapters


def chapter_paragraph_ar(chapter_title: str, chapter_focus: str, style: str, idea: str, idx: int, total: int) -> str:
    connectors = [
        "في هذا السياق",
        "ومن زاوية عملية",
        "وعند النظر بعمق",
        "وبالانتقال إلى التطبيق",
        "وعلى مستوى النتائج",
    ]
    c = connectors[idx % len(connectors)]
    return (
        f"{c} يتضح أن {chapter_focus} ليست فكرة عابرة، بل محورًا مركزيًا في بناء كتاب احترافي متماسك. "
        f"يعتمد هذا الفصل على أسلوب {style.lower()} يوازن بين الشرح المفاهيمي والتطبيق الواقعي، بحيث ينتقل القارئ من الفهم العام إلى القدرة على التنفيذ. "
        f"عندما نربط عنوان الفصل "
        f"«{chapter_title}» بفكرة الكتاب الأساسية، تظهر لنا طبقات متعددة من المعنى تبدأ من تشخيص الوضع الحالي ثم تتدرج نحو تصميم حلول قابلة للقياس والتحسين. "
        f"الهدف هنا ليس تقديم نص إنشائي، وإنما بناء سرد مهني يوضح لماذا تنجح بعض المقاربات بينما تتعثر مقاربات أخرى رغم تشابه الأدوات. "
        f"ولهذا نحلل الفرضيات الأساسية بدقة ونفصل بين المؤشرات الحقيقية والانطباعات السريعة، حتى لا تضيع البوصلة الاستراتيجية في التفاصيل الثانوية. "
        f"كما يتم توسيع الأمثلة لتشمل مواقف متنوعة، لأن جودة الكتاب لا تقاس فقط بقوة الفكرة، بل بقدرتها على الصمود أمام واقع متغير ومتطلب. "
        f"ومن خلال هذا البناء المتدرج يصبح القارئ أقرب إلى اتخاذ قرارات واعية مدعومة بمنطق واضح، وهو ما يجعل هذا الفصل خطوة متقدمة ضمن المسار الكامل للكتاب. "
        f"إن فكرة الكتاب ({idea[:220]}) تُستخدم هنا كمرجع حي يضمن الترابط والاستمرارية بين جميع الفصول، بدل أن يتحول كل فصل إلى جزيرة مستقلة بلا امتداد معرفي."
    )


def chapter_paragraph_en(chapter_title: str, chapter_focus: str, style: str, idea: str, idx: int) -> str:
    lead = [
        "At this stage",
        "From a practical perspective",
        "When we examine the pattern closely",
        "In implementation terms",
    ][idx % 4]
    return (
        f"{lead}, {chapter_focus} should be treated as a structural pillar rather than a passing concept. "
        f"This chapter follows a {style.lower()} tone that combines conceptual clarity with executable guidance, so the reader can move from understanding to application. "
        f"By linking the chapter title '{chapter_title}' to the core book premise, we uncover a sequence that starts with diagnosis and advances toward measurable improvement. "
        f"The objective is not decorative prose, but professional narrative architecture that explains why certain methods produce durable outcomes while others collapse under pressure. "
        f"For that reason, assumptions are tested, signals are distinguished from noise, and trade-offs are made explicit before recommendations are introduced. "
        f"Expanded examples are used to simulate realistic conditions, because a strong chapter must survive complexity, constraints, and imperfect information. "
        f"As a result, the reader gains both strategic orientation and tactical confidence, allowing this chapter to function as a meaningful part of a complete, coherent book. "
        f"The main idea ({idea[:220]}) remains active throughout the passage so every section contributes to one integrated intellectual trajectory."
    )


def generate_chapter(ch: Dict[str, Any], book_info: Dict[str, Any], idea: str, prev_summary: str) -> str:
    language = book_info["language"]
    style = book_info["writing_style"]
    title = ch["title"]
    focus = ch.get("summary") or title
    target_paragraphs = 16
    blocks = []

    for i in range(target_paragraphs):
        if language == "Arabic":
            p = chapter_paragraph_ar(title, focus, style, idea, i, target_paragraphs)
        else:
            p = chapter_paragraph_en(title, focus, style, idea, i)
        if prev_summary and i in (4, 11):
            if language == "Arabic":
                p += f" ويرتبط ذلك بما انتهى إليه الفصل السابق: {prev_summary[:260]}، مما يخلق انتقالًا منطقيًا يحافظ على تدفق الكتاب." 
            else:
                p += f" This also extends the previous chapter's closing insight: {prev_summary[:260]}, creating continuity and narrative momentum."
        blocks.append(p)

    if language == "Arabic":
        conclusion = (
            "في الخلاصة، يقدم هذا الفصل نموذجًا عمليًا ومهنيًا يوضح كيف تتحول الفكرة من تصور عام إلى نتائج قابلة للتنفيذ والمتابعة. "
            "ومع نهاية هذا الجزء يصبح القارئ مستعدًا للانتقال إلى الفصل التالي وهو يمتلك إطارًا أكثر نضجًا في التحليل، "
            "وأدوات أوضح في الاختيار، وقدرة أعلى على تحويل المعرفة إلى أثر حقيقي ومستدام."
        )
    else:
        conclusion = (
            "In conclusion, this chapter establishes a professional pathway from abstract framing to actionable results. "
            "By the end, the reader is prepared for the next chapter with stronger analytical judgment, clearer execution tools, "
            "and a more disciplined ability to turn insight into sustained impact."
        )

    blocks.append(conclusion)
    return "\n\n".join(blocks).strip()


def build_html(book: Dict[str, Any]) -> str:
    toc_items = "".join(
        f'<div class="toc-item"><span class="toc-num">{str(ch["number"]).zfill(2)}</span><span>{escape(ch["title"])}</span></div>'
        for ch in book["chapters"]
    )

    chapters_html = ""
    for ch in book["chapters"]:
        paragraphs = [p.strip() for p in ch.get("content", "").split("\n\n") if len(p.strip()) > 20]
        p_html = "".join(f"<p>{escape(p)}</p>" for p in paragraphs)
        chapters_html += (
            f'<section class="chapter"><div class="ch-label">Chapter {ch["number"]}</div>'
            f'<h2>{escape(ch["title"])}</h2>{p_html}</section>'
        )

    return f"""<!doctype html>
<html lang="{escape(book['language'])}">
<head>
<meta charset="utf-8"/>
<title>{escape(book['title'])}</title>
<style>
body{{font-family:Georgia,serif;max-width:850px;margin:30px auto;line-height:1.9;padding:0 20px;color:#111}}
h1,h2{{font-family:Arial,sans-serif}}
.cover{{text-align:center;border-bottom:2px solid #222;padding:40px 0;margin-bottom:28px}}
.toc-item{{display:flex;gap:12px;padding:8px 0;border-bottom:1px solid #eee}}
.toc-num{{font-weight:700;color:#777;width:32px;flex-shrink:0}}
.chapter{{margin-top:40px;border-top:1px solid #ddd;padding-top:28px}}
.ch-label{{font-size:12px;color:#777;text-transform:uppercase;letter-spacing:.08em}}
p{{margin-bottom:1.2em;text-align:justify}}
</style>
</head>
<body>
<div class="cover"><h1>{escape(book['title'])}</h1><div>By {escape(book['author_name'])}</div></div>
<h3>Table of Contents</h3>
{toc_items}
{chapters_html}
</body>
</html>"""


def main() -> None:
    st.set_page_config(page_title="OminiBooks Free", layout="wide")
    init_state()

    st.title("📚 OMINIBOOKS — 100% Free Offline Generator")
    st.caption("بدون Anthropic API Key وبدون أي خدمة مدفوعة. توليد مجاني كامل داخل التطبيق.")

    with st.form("book_form"):
        col1, col2 = st.columns(2)
        with col1:
            title = st.text_input("Book Title", placeholder="اكتب عنوان كتابك")
            author_name = st.text_input("Author Name", value="Unknown Author")
            genre = st.selectbox("Genre", GENRES)
        with col2:
            language = st.selectbox("Language", LANGUAGES)
            writing_style = st.selectbox("Writing Style", STYLES)
            num_chapters = st.number_input("Chapters", min_value=1, max_value=30, value=8, step=1)

        idea = st.text_area(
            "Book Idea",
            height=180,
            placeholder="اكتب الفكرة بالتفصيل: الجمهور المستهدف، المحاور، النتائج التي تريدها...",
        )
        submitted = st.form_submit_button("⚡ Generate Book For Free")

    if submitted:
        if not title.strip() or not idea.strip():
            st.error("المرجو كتابة عنوان الكتاب وفكرته أولاً.")
        else:
            progress = st.progress(0)
            log = st.empty()
            book_info = {
                "title": title.strip(),
                "author_name": author_name.strip() or "Unknown Author",
                "genre": genre,
                "language": language,
                "writing_style": writing_style,
                "num_chapters": int(num_chapters),
            }

            log.info("Building professional outline...")
            chapters = generate_outline(title, idea, genre, language, int(num_chapters))
            progress.progress(10)

            book = {
                **book_info,
                "idea": idea,
                "created_at": datetime.utcnow().isoformat(),
                "chapters": [
                    {
                        "number": ch.get("number", i + 1),
                        "title": ch.get("title", f"Chapter {i + 1}"),
                        "summary": ch.get("summary", ""),
                        "content": "",
                    }
                    for i, ch in enumerate(chapters)
                ],
            }

            prev_summary = ""
            for i, ch in enumerate(book["chapters"]):
                log.info(f"Writing chapter {ch['number']}: {ch['title']}")
                content = generate_chapter(ch, book_info, idea, prev_summary)
                ch["content"] = content
                prev_summary = " ".join(content.split()[-80:])
                progress.progress(10 + int(((i + 1) / len(book["chapters"])) * 90))

            st.session_state.books.insert(0, book)
            st.success("تم توليد الكتاب كاملًا بشكل مجاني.")

    st.subheader("My Library")
    if not st.session_state.books:
        st.write("No books yet.")
    else:
        for idx, b in enumerate(st.session_state.books):
            with st.expander(f"{b['title']} — {b['author_name']} ({b['num_chapters']} chapters)", expanded=(idx == 0)):
                total_words = sum(len((ch.get("content") or "").split()) for ch in b["chapters"])
                st.caption(f"{b['genre']} · {b['language']} · {total_words:,} words")
                html = build_html(b)
                st.download_button(
                    label="Download HTML",
                    data=html,
                    file_name=f"{b['title'].replace(' ', '_')}.html",
                    mime="text/html",
                    key=f"dl_{idx}",
                )


if __name__ == "__main__":
    random.seed(42)
    main()
