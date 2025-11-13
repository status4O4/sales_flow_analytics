const startDateInput = document.getElementById('start_date');
const endDateInput = document.getElementById('end_date');
const fetchButton = document.getElementById('fetch-data');
const errorMessage = document.getElementById('error-message');
const loadingIndicator = document.getElementById('loading');
const summarySection = document.getElementById('summary');
const periodSpan = document.getElementById('period');
const totalDaysSpan = document.getElementById('total-days');
const totalSalesSpan = document.getElementById('total-sales');
const salesTableBody = document.getElementById('sales-table-body');
const topDaysTableBody = document.getElementById('top-days-table-body');

let salesChart = null;
let movingAverageChart = null;

function getTodayDate() {
    return new Date().toISOString().split('T')[0];
}

function setupDateConstraints() {
    const today = getTodayDate();
    
    startDateInput.setAttribute('max', today);
    endDateInput.setAttribute('max', today);
    
    startDateInput.addEventListener('change', function() {
        if (this.value) {
            endDateInput.setAttribute('min', this.value);
        }
    });
    
    endDateInput.addEventListener('change', function() {
        if (this.value && startDateInput.value > this.value) {
            startDateInput.value = this.value;
        }
    });
}

const today = new Date();
const defaultStartDate = new Date(today.getFullYear() - 1, today.getMonth(), today.getDate());

function initializeDates() {
    setupDateConstraints();
    
    startDateInput.valueAsDate = defaultStartDate;
    endDateInput.valueAsDate = today;
    
    if (startDateInput.value) {
        endDateInput.setAttribute('min', startDateInput.value);
    }
}

fetchButton.addEventListener('click', fetchData);

document.querySelectorAll('th[data-sort]').forEach(header => {
    header.addEventListener('click', () => {
        const tableId = header.closest('table').id;
        const column = header.getAttribute('data-sort');
        sortTable(tableId, column);
    });
});

document.addEventListener('DOMContentLoaded', function() {
    const fetchButton = document.getElementById('fetch-data');
    const loadingOverlay = document.getElementById('loading');
    const mainContent = document.getElementById('main-content');
    const errorMessage = document.getElementById('error-message');

    initializeDates();

    if (fetchButton) {
        fetchButton.addEventListener('click', function() {
            loadingOverlay.classList.remove('hidden');
            errorMessage.classList.add('hidden');
        });
    }

    window.showSpinner = function() {
        loadingOverlay.classList.remove('hidden');
    };

    window.hideSpinner = function() {
        loadingOverlay.classList.add('hidden');
    };
});

async function fetchData() {
    const startDate = startDateInput.value;
    const endDate = endDateInput.value;
    
    const today = getTodayDate();
    if (endDate > today) {
        showError('Дата конца не может быть позже сегодняшнего дня');
        return;
    }
    
    if (startDate > endDate) {
        showError('Дата начала не может быть позже даты конца');
        return;
    }
       
    loadingIndicator.classList.remove('hidden');
    errorMessage.classList.add('hidden');
    summarySection.classList.add('hidden');
    
    try {
        const response = await fetch(`http://localhost:8000/sales/summary?start_date=${startDate}&end_date=${endDate}`);
        
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const data = await response.json();
        
        if (data.error) {
          throw new Error(data.error);
        }
        
        loadingIndicator.classList.add('hidden');
        
        displayData(data);
        
    } catch (error) {
        loadingIndicator.classList.add('hidden');
        showError(`Failed to fetch data: ${error.message}`);
        console.error('Error fetching data:', error);
    }
}

function displayData(data) {
    const summary = data.summary;
    periodSpan.textContent = `${summary.period.start_date} to ${summary.period.end_date}`;
    totalDaysSpan.textContent = summary.total_days;
    totalSalesSpan.textContent = summary.total_sales.toLocaleString('ru-RU', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 2
    });
    summarySection.classList.remove('hidden');
    
    displaySalesTable(data.moving_average);
    
    displayTopDaysTable(data.top_days);
    
    createCharts(data.moving_average);
}

function displaySalesTable(data) {
    salesTableBody.innerHTML = '';
    
    data.forEach(item => {
        const row = document.createElement('tr');
        
        const dateCell = document.createElement('td');
        dateCell.textContent = item.date;
        
        const salesCell = document.createElement('td');
        salesCell.textContent = item.sales;
        
        const movingAvgCell = document.createElement('td');
        movingAvgCell.textContent = item.moving_average;
        
        row.appendChild(dateCell);
        row.appendChild(salesCell);
        row.appendChild(movingAvgCell);
        
        salesTableBody.appendChild(row);
    });
}

function displayTopDaysTable(data) {
    topDaysTableBody.innerHTML = '';
    
    data.forEach(item => {
        const row = document.createElement('tr');
        
        const dateCell = document.createElement('td');
        dateCell.textContent = item.date;
        
        const salesCell = document.createElement('td');
        salesCell.textContent = item.sales;
        
        row.appendChild(dateCell);
        row.appendChild(salesCell);
        
        topDaysTableBody.appendChild(row);
    });
}

function createCharts(data) {
    const dates = data.map(item => item.date);
    const sales = data.map(item => item.sales);
    const movingAverages = data.map(item => item.moving_average);
    
    if (salesChart) {
        salesChart.destroy();
    }
    if (movingAverageChart) {
        movingAverageChart.destroy();
    }
    
    const salesCtx = document.getElementById('sales-chart').getContext('2d');
    salesChart = new Chart(salesCtx, {
        type: 'bar',
        data: {
            labels: dates,
            datasets: [{
                label: 'Daily Sales',
                data: sales,
                backgroundColor: 'rgba(54, 162, 235, 0.5)',
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return value.toLocaleString() + '₽';
                        }
                    }
                }
            }
        }
    });
    
    const movingAvgCtx = document.getElementById('moving-average-chart').getContext('2d');
    movingAverageChart = new Chart(movingAvgCtx, {
        type: 'line',
        data: {
            labels: dates,
            datasets: [
                {
                    label: 'Daily Sales',
                    data: sales,
                    borderColor: 'rgba(54, 162, 235, 1)',
                    backgroundColor: 'rgba(54, 162, 235, 0.1)',
                    borderWidth: 1,
                    fill: true
                },
                {
                    label: 'Moving Average',
                    data: movingAverages,
                    borderColor: 'rgba(255, 99, 132, 1)',
                    borderWidth: 2,
                    fill: false,
                    tension: 0.4
                }
            ]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return value.toLocaleString();
                        }
                    }
                }
            }
        }
    });
}

function sortTable(tableId, column) {
    const sortableHeaders = document.querySelectorAll('th[data-sort]');
    sortableHeaders.forEach(header => {
        header.style.cursor = 'pointer';
        header.addEventListener('click', function() {
            const table = this.closest('table');
            const tbody = table.querySelector('tbody');
            const rows = Array.from(tbody.querySelectorAll('tr'));
            const columnIndex = Array.from(this.parentElement.children).indexOf(this);
            const sortType = this.getAttribute('data-sort');
            const isAscending = !this.classList.contains('asc');
            
            table.querySelectorAll('th').forEach(th => {
                th.classList.remove('asc', 'desc');
            });
            
            this.classList.toggle('asc', isAscending);
            this.classList.toggle('desc', !isAscending);
            
            rows.sort((a, b) => {
                const aCell = a.children[columnIndex].textContent.trim();
                const bCell = b.children[columnIndex].textContent.trim();
                
                let aValue, bValue;
                
                switch(sortType) {
                    case 'date':
                        aValue = new Date(aCell);
                        bValue = new Date(bCell);
                        break;
                    case 'sales':
                    case 'moving_average':
                        aValue = parseFloat(aCell) || 0;
                        bValue = parseFloat(bCell) || 0;
                        break;
                    default:
                        aValue = aCell.toLowerCase();
                        bValue = bCell.toLowerCase();
                }
                
                if (aValue < bValue) return isAscending ? -1 : 1;
                if (aValue > bValue) return isAscending ? 1 : -1;
                return 0;
            });
            
            tbody.innerHTML = '';
            rows.forEach(row => tbody.appendChild(row));
        });
    });
}

function addSortingStyles() {
    const style = document.createElement('style');
    style.textContent = `
        th[data-sort] {
            position: relative;
            user-select: none;
        }
        
        th[data-sort]:hover {
            background-color: #f5f5f5;
        }
        
        th[data-sort].asc::after {
            content: ' ▲';
            font-size: 12px;
            color: #007bff;
        }
        
        th[data-sort].desc::after {
            content: ' ▼';
            font-size: 12px;
            color: #007bff;
        }
        
        th[data-sort]::after {
            content: ' ↕';
            font-size: 12px;
            color: #ccc;
            opacity: 0.5;
        }
        
        th[data-sort]:hover::after {
            opacity: 1;
        }
    `;
    document.head.appendChild(style);
}

document.addEventListener('DOMContentLoaded', function() {
    addSortingStyles();
    sortTable();
});

function updateTableSorting() {
    sortTable();
}

function showError(message) {
    errorMessage.textContent = message;
    errorMessage.classList.remove('hidden');
}
