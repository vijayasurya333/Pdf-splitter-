from flask import Flask, render_template, request, send_file
import os
from PyPDF2 import PdfReader, PdfWriter
import tempfile

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/split", methods=["POST"])
def split_pdf():
    pdf_file = request.files["pdf"]
    method = request.form.get("method")
    pages_per_split = int(request.form.get("pages", 1))

    if not pdf_file:
        return "No PDF uploaded."

    # Save uploaded pdf temporarily
    temp_input = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    pdf_file.save(temp_input.name)

    reader = PdfReader(temp_input.name)
    total_pages = len(reader.pages)

    output_files = []

    # SPLIT BY PAGES
    if method == "pages":
        for start in range(0, total_pages, pages_per_split):
            writer = PdfWriter()
            end = min(start + pages_per_split, total_pages)

            for page_num in range(start, end):
                writer.add_page(reader.pages[page_num])

            temp_output = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
            with open(temp_output.name, "wb") as f_out:
                writer.write(f_out)

            output_files.append(temp_output.name)

    # If only one file output, return directly
    if len(output_files) == 1:
        return send_file(output_files[0], as_attachment=True)

    # If multiple files, zip them
    import zipfile
    zip_path = tempfile.NamedTemporaryFile(delete=False, suffix=".zip").name

    with zipfile.ZipFile(zip_path, "w") as zipf:
        for i, file in enumerate(output_files):
            zipf.write(file, f"part_{i+1}.pdf")

    return send_file(zip_path, as_attachment=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
