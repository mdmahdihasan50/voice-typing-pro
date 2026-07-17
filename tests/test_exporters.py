from docx import Document

from voice_typing_pro.exporters import export_docx


def test_docx_export_keeps_bengali_text(tmp_path) -> None:
    target = tmp_path / "sample.docx"
    export_docx("বাংলা লেখা\nEnglish text", target, "Noto Sans Bengali", 16)
    document = Document(target)
    assert [paragraph.text for paragraph in document.paragraphs] == [
        "বাংলা লেখা",
        "English text",
    ]
