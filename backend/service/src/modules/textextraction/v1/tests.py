
from TextExtractor import TextExtractor


file_path = "test.pdf"

texts, types, labels = TextExtractor.get_text(pdf_path = file_path,pattern_path="" )

for text in texts:
    print("---\n", text)
