import os

HERE = os.path.abspath(os.path.dirname(__file__))

file_m = {
    "filename": "news.csv",
    "file_path": os.path.join(HERE, "multipart_m.bin"),
    "headers": {
        "content-type": "multipart/form-data; boundary=----WebKitFormBoundaryCtwHrjI6bEnjs7o6"
    },
    "hash": "08efc253e652810ba0ecf974d9943933",
    "content_type": "text/csv",
}

# file_m.update({"file_path": })


file_l = {
    "filename": "news-categorized.csv",
    "file_path": os.path.join(HERE, "multipart_l.bin"),
    "headers": {
        "content-type": "multipart/form-data; boundary=----WebKitFormBoundaryNPwhz5SCaFU3O6pE"
    },
    "hash": "0d6e5e071ad42df8a90dfe0c00bd48ed",
    "content_type": "text/csv",
}

file_data = [file_m, file_l]
