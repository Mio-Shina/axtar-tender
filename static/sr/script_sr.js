document.addEventListener("DOMContentLoaded", function() {
  flatpickr("#date_range", {
    mode: "range",
    dateFormat: "Y-m-d",
    locale: "az"
  });
});

function filterTable() {
  const dateRange = document.getElementById('date_range').value.trim();
  if (!dateRange) return;
  const dates = dateRange.split(" - ").map(d => d.trim());

  if (dates.length !== 2 || !dates[0] || !dates[1]) {
    alert("Filterin məlumatlarını doldurun");
    return;
  }

  const [start, end] = dates;
  const rows = document.querySelectorAll('tbody tr');

  rows.forEach(row => {
    const dateCell = row.cells[8];
    if (!dateCell) return;

    const rowDate = dateCell.textContent.trim();

    if (rowDate === "Yoxdur" || rowDate < start || rowDate > end) {
      row.style.display = 'none';
    } else {
      row.style.display = '';
    }
  });
}
