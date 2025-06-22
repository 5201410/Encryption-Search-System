async function search() {
    const queryFile = document.getElementById("queryFile").files[0];
    if (!queryFile) {
        alert("请先上传查询文档！");
        return;
    }

    const formData = new FormData();
    formData.append('query_file', queryFile);

    const response = await fetch('/search', {
        method: 'POST',
        body: formData
    });
    const data = await response.json();

    document.getElementById("encrypted_ids").textContent = JSON.stringify(data.encrypted_doc_ids, null, 2);
}

