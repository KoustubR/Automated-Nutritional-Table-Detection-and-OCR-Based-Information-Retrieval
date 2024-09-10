document.getElementById('upload-form').addEventListener('submit', async function(event) {
    event.preventDefault(); 
    const fileInput = document.getElementById('file-input');
    const formData = new FormData();
    formData.append('file', fileInput.files[0]);

    try {
        const response = await fetch('http://localhost:8000/extract_nutrients/', {
            method: 'POST',
            body: formData
        });

        if (response.ok) {
            const resultText = await response.text();
            const parsedResult = JSON.parse(resultText);  
            const finalResult = JSON.parse(parsedResult); 
            if (Array.isArray(finalResult)) {
                const nutrientInfo = document.getElementById('nutrient-info');
                nutrientInfo.innerHTML = renderNutrientTable(finalResult);
                nutrientInfo.style.display = 'block';
            }

            const imgResponse = await fetch('http://localhost:8000/crop/', {
                method: 'POST',
                body: formData
            });

            if (imgResponse.ok) {
                const blob = await imgResponse.blob();
                const imgUrl = URL.createObjectURL(blob);
                const croppedImage = document.getElementById('cropped-image');
                croppedImage.src = imgUrl;
                croppedImage.style.display = 'block';  
            }

            document.getElementById('content-container').style.display = 'flex';
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error uploading image');
    }
});

function renderNutrientTable(nutrients) {
    let table = `<table><thead><tr><th>Nutrient</th><th>Amount</th></tr></thead><tbody>`;
    nutrients.forEach(nutrient => {
        table += `<tr><td>${nutrient.Nutrient}</td><td>${nutrient.Amount}</td></tr>`;
    });
    table += `</tbody></table>`;
    return table;
}
