document.getElementById('submit-btn').addEventListener('click', async function (e) {
    e.preventDefault();

    const fileInput = document.getElementById('user_file');
    const file = fileInput.files[0];

    const userRule = document.getElementById('user-rule-input').value;

    console.log(userRule);


    if (!file) {
        alert("Please select a file.");
        return;
    }

    const formData = new FormData();
    formData.append('file', file);
    formData.append('rule', userRule);


    try {
        const response = await fetch("/accept_file", {
            method: "POST",
            body: formData
        });

        if (!response.ok) {
            console.error("Server error");
            return;
        }

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);

        const a = document.createElement("a");
        a.href = url;
        a.download = "cleaned_data.csv";  // Suggested filename
        document.body.appendChild(a);
        a.click();

        window.URL.revokeObjectURL(url);
        a.remove();

        document.getElementById('cleaning-msg').style.display = "none";
        
    } catch (error) {
        console.log("Error:", error);
    }
});
