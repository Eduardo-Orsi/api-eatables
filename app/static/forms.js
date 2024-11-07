dayjs.extend(dayjs_plugin_duration);

let interval;
let imageIndex = 0;
let imageArray = [];

document.addEventListener("DOMContentLoaded", function() {
    function setMaxFiles(maxFiles) {
        const fileInput = document.getElementById('file-upload');
        fileInput.setAttribute('data-max-files', maxFiles);

        const fileLabel = document.querySelector('.custom-file-upload');
        fileLabel.innerHTML = `<i class="bi bi-camera"></i> Escolher fotos do casal (Máximo ${maxFiles})`;
    }

    function showTemporaryMessage(message) {
        const messageDiv = document.getElementById('size-exceeded');
        messageDiv.textContent = message;
        messageDiv.style.display = 'block';

        setTimeout(() => {
            messageDiv.style.display = 'none';
        }, 3000);
    }

    document.getElementById('file-upload').addEventListener('change', function() {
        const maxFiles = this.getAttribute('data-max-files') || 3; 
        if (this.files.length > maxFiles) {
            showTemporaryMessage(`Você pode selecionar no máximo ${maxFiles} fotos.`);
            this.value = ""; 
            return;
        }

        imageArray = []; // Limpa as imagens anteriores
        for (let i = 0; i < this.files.length; i++) {
            const file = this.files[i];
            const reader = new FileReader();
            reader.onload = function(event) {
                imageArray.push(event.target.result);
                if (imageArray.length === 1) {
                    displayImage(); // Exibe a primeira imagem imediatamente
                }
            };
            reader.readAsDataURL(file);
        }
    });

    function displayImage() {
        const imageContainer = document.getElementById('image-container');
        if (imageArray.length > 0) {
            imageContainer.innerHTML = `<img src="${imageArray[imageIndex]}" style="width: 100%; height: 100%;">`;
            imageIndex = (imageIndex + 1) % imageArray.length;
        }
    }

    setInterval(displayImage, 2000); // Troca de imagem a cada 3 segundos

    function updatePreview() {
        const name = document.getElementById("name").value;
        const message = document.getElementById("message").value;

        document.getElementById("preview-name").textContent = name.replace(/\s+/g, '-').toLowerCase();
        document.getElementById("preview-message").textContent = message;
    }

    document.getElementById("name").addEventListener("input", updatePreview);
    document.getElementById("message").addEventListener("input", updatePreview);

    document.getElementById("input-radio-plan-1").addEventListener("click", () => setMaxFiles(3));
    document.getElementById("input-radio-plan-2").addEventListener("click", () => setMaxFiles(7));

    function startCounter() {
        clearInterval(interval);
        const dateInput = document.getElementById("relationship-date").value;
        const timeInput = document.getElementById("relationship-time").value;
        const startDateTime = dayjs(`${dateInput}T${timeInput}`);

        if (!startDateTime.isValid()) {
            document.getElementById("time-since").textContent = "Data ou hora inválida";
            return;
        }

        interval = setInterval(() => {
            const now = dayjs();
            const duration = dayjs.duration(now.diff(startDateTime));

            const years = Math.floor(duration.asYears());
            const months = duration.months();
            const days = duration.days();
            const hours = duration.hours();
            const minutes = duration.minutes();
            const seconds = duration.seconds();

            document.getElementById("time-since").innerHTML = 
                `<span>${years} anos, ${months} meses, ${days} dias</span><br><span>${hours} horas, ${minutes} minutos e ${seconds} segundos</span>`;
        }, 1000);
    }

    document.getElementById("relationship-date").addEventListener("change", startCounter);
    document.getElementById("relationship-time").addEventListener("change", startCounter);
});
