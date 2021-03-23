import os

HERE = os.path.abspath(os.path.dirname(__file__))

file_m = {
    "filename": "news.csv",
    "multipart_file_path": os.path.join(HERE, "multipart_m.bin"),
    "file_path": os.path.join(HERE, "news.csv"),
    "headers": {
        "content-type": "multipart/form-data; boundary=----WebKitFormBoundaryCtwHrjI6bEnjs7o6"
    },
    "hash": "08efc253e652810ba0ecf974d9943933",
    "content_type": "text/csv",
}


file_l = {
    "filename": "news-categorized.csv",
    "multipart_file_path": os.path.join(HERE, "multipart_l.bin"),
    "file_path": os.path.join(HERE, "news-categorized.csv"),
    "headers": {
        "content-type": "multipart/form-data; boundary=----WebKitFormBoundaryNPwhz5SCaFU3O6pE"
    },
    "hash": "0d6e5e071ad42df8a90dfe0c00bd48ed",
    "content_type": "text/csv",
}

file_data = [file_m, file_l]
