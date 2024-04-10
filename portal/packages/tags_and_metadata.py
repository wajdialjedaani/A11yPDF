# from pdfixsdk.Pdfix import *
#
# def browse_tags(parent: PdsStructElement, structTree):
#     """
#     Recursively browse tags and print their types.
#
#     Args:
#         parent (PdsStructElement): Parent struct element.
#         structTree: The structural tree of the PDF document for accessing elements.
#
#     Returns:
#         None
#     """
#     print(parent.GetType(True))
#     count = parent.GetNumChildren()
#     for i in range(count):
#         if parent.GetChildType(i) != kPdsStructChildElement:
#             continue
#         child = structTree.GetStructElementFromObject(parent.GetChildObject(i))
#         browse_tags(child, structTree)
#
# def check_pdf_tags_and_metadata(pdf_file):
#     # try:
#     doc = GetPdfix().OpenDoc(pdf_file, "")
#     if not doc:
#         raise Exception("Failed to open PDF document.")
#     structTree = doc.GetStructTree()
#     if not structTree:
#         return False, None, {"Error": "No structural tree found. The document might not be tagged."}
#
#     if structTree.GetNumKids() == 0:
#         return False, None, {"Error": "Structural tree is empty. No tags present."}
#
#     childElem = structTree.GetStructElement(0)
#     if not childElem:
#         return False, None, {"Error": "No root element in structural tree."}
#
#     # Assuming tags are present if we have a structural tree and can access its root element
#     tags_present = True
#     # Extract tags
#     print("Tags Present:")
#     browse_tags(childElem, structTree)
#
#     # Get metadata
#     metadata = {
#         'Title': doc.GetInfo('Title'),
#         'Author': doc.GetInfo('Author'),
#         'Subject': doc.GetInfo('Subject'),
#         'Keywords': doc.GetInfo('Keywords'),
#         'CreationDate': doc.GetInfo('CreationDate'),
#         'ModDate': doc.GetInfo('ModDate'),
#         'Producer': doc.GetInfo('Producer'),
#     }
#
#     return tags_present, None, metadata

    # except Exception as e:
    #     print(f"Error accessing PDF: {e}")
    #     return False, None, None


pdf_file = "/Users/sandeepkumarrudhravaram/WorkSpace/UntProjects/pdf_analyzer_prodv1/Team16_Sprint_2.pdf"
tags_present, tags, metadata = check_pdf_tags_and_metadata(pdf_file)

if tags_present:
    print("Tags are present in the PDF.")
else:
    print("Tags are not present in the PDF.")

if metadata:
    print("Available metadata:")
    for key, value in metadata.items():
        if value:  # Only print non-empty metadata values
            print(f"\t- {key}: {value}")
else:
    print("No metadata available in the PDF.")