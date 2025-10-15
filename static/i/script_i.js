function updateData() {
    const button = document.getElementById('hoverButton');
    const loading = document.getElementById('loadingMessage');

    button.disabled = true;
    loading.style.display = 'block';

    fetch('/update_data')
        .then(response => response.json())
        .then(data => {
            loading.style.display = 'none';
            button.disabled = false;
            setTimeout(() => alert(data.message), 100);
        })
        .catch(error => {
            console.error('Xəta:', error);
            loading.style.display = 'none';
            button.disabled = false;
            setTimeout(() => alert('Məlumatı yeniləyərkən xəta baş verdi.'), 100);
        });
}

const button = document.getElementById('hoverButton');
const tooltip = document.getElementById('tooltip');
let timer;

button.addEventListener('mouseenter', () => {
    timer = setTimeout(() => tooltip.classList.add('show-tooltip'), 500);
});

button.addEventListener('mouseleave', () => {
    clearTimeout(timer);
    tooltip.classList.remove('show-tooltip');
});
