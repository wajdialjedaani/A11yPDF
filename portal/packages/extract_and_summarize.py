import pdfplumber
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer
def extract_and_summarize_text(pdf_file, summary_sentences=3):
    import nltk
    nltk.download('punkt')
    """
    Extracts text from a PDF and generates a summarized version.

    Args:
        pdf_file (str): Path to the PDF file.
        summary_sentences (int, optional): Number of sentences in the summary. Default is 3.

    Returns:
        tuple:
            - str: Extracted text from the PDF.
            - str: Summarized version of the text.
    """
    with pdfplumber.open(pdf_file) as pdf:
        # Extract text from all pages
        full_text = ""
        for page in pdf.pages:
            full_text += page.extract_text()

    # Create a plaintext parser
    parser = PlaintextParser.from_string(full_text, Tokenizer("english"))

    # Initialize LSA summarizer
    summarizer = LsaSummarizer()
    summarizer.stop_words = ["."]

    # Generate summary
    summarized_text = ""
    for sentence in summarizer(parser.document, summary_sentences):
        summarized_text += str(sentence) + " "

    return full_text, summarized_text

# # Example usage
# pdf_file = "/Users/sandeepkumarrudhravaram/WorkSpace/UntProjects/pdf_analyzer_prodv1/Team16_Sprint_2.pdf"
# full_text, summarized_text = extract_and_summarize_text(pdf_file)
#
# print("Full Text:")
# print(full_text)
#
# print("\nSummarized Text:")
# print(summarized_text)