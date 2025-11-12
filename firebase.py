import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
from collections import defaultdict

from fetcher import papers_from_codes

cred = credentials.Certificate("firebase.json")
firebase_admin.initialize_app(cred)
db = firestore.client()


def id(x):
    return x

# sorry im lowk a combinatorialist
codes_from_subject = {
    "combo": ["CO"],
    "prob": ["PR"],
    "nt": ["NT"],
    "ag": ["AG"],
    "anal": ["AP", "CA", "SP", "DS"],
    "geo": ["DG", "MG"]
}


subjects = codes_from_subject.keys()


def clear_collection(collection_name):
    docs = db.collection(collection_name).stream()
    for doc in docs:
        doc.reference.delete()

def db_from_paper(paper, index, date_counts):
    header, title, abstract_preview = paper.preview(id, date_counts, True, 20)
    preview = (
        header
        + f"<br><br><a href='{paper.link}' target='_blank'><b><big>"
        + title
        + "</big></b></a><br><br>"
        + abstract_preview
    )
    return {
        "order": index,
        "slides": [preview] + paper.abs_sentences(),
    }



for subject in subjects:
    clear_collection(f"{subject}-papers")
    papers = papers_from_codes(codes_from_subject[subject])
    papers.sort(key=lambda x: x.date, reverse=True)
    date_counts = defaultdict(int)
    for paper in papers:
        date_counts[paper.date] += 1
        paper.index = date_counts[paper.date]

    db_papers = [
        db_from_paper(paper, index + 1, date_counts)
        for (index, paper) in enumerate(papers)
    ]

    for db_paper in db_papers:
        doc_id = str(db_paper["order"])
        papers_ref = db.collection(f"{subject}-papers").document(doc_id).set(db_paper)
