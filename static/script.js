// 使用 Chart.js 來生成圖表
const ctxAudio = document.getElementById('audioChart').getContext('2d');
const audioChart = new Chart(ctxAudio, {
    type: 'bar',
    data: {
        labels: ['Positive', 'Negative', 'Neutral'],
        datasets: [{
            label: 'Audio',
            data: [10, 20, 30], // 替換為您的數據
            backgroundColor: ['#4caf50', '#f44336', '#ffeb3b'],
        }]
    },
    options: {
        scales: {
            y: {
                beginAtZero: true
            }
        }
    }
});

const ctxText = document.getElementById('textChart').getContext('2d');
const textChart = new Chart(ctxText, {
    type: 'bar',
    data: {
        labels: ['Positive', 'Negative', 'Neutral'],
        datasets: [{
            label: 'Text',
            data: [15, 25, 35], // 替換為您的數據
            backgroundColor: ['#4caf50', '#f44336', '#ffeb3b'],
        }]
    },
    options: {
        scales: {
            y: {
                beginAtZero: true
            }
        }
    }
});

const ctxFacial = document.getElementById('facialChart').getContext('2d');
const facialChart = new Chart(ctxFacial, {
    type: 'line',
    data: {
        labels: ['Month 1', 'Month 2', 'Month 3', 'Month 4'], // 替換為您的數據
        datasets: [{
            label: 'Facial',
            data: [5, 10, 15, 20], // 替換為您的數據
            backgroundColor: '#4caf50',
            borderColor: '#4caf50',
            fill: false,
        }]
    },
    options: {
        scales: {
            y: {
                beginAtZero: true
            }
        }
    }
});
