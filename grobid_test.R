library(papercheck)

grobid_url_without_slash = "https://grobid.papercheck.works"
data <- papercheck::pdf2grobid(
    filename = "/home/jakub/Projects/paper_testing/documents_to_test/pdfs/kelders-et-al-2024.pdf",
    grobid_url = grobid_url_without_slash
)
print(data)
print("-----------------------------------------------
------------------------------------------------------------------------")

grobid_url= "https://grobid.papercheck.works/"
data <- papercheck::pdf2grobid(
    filename = "/home/jakub/Projects/paper_testing/documents_to_test/pdfs/kelders-et-al-2024.pdf",
    grobid_url = grobid_url
)
print(data)


