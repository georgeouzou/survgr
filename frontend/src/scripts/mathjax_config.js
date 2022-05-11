
window.MathJax = {
    loader: {load: ["input/tex", "output/chtml"]},
    tex: {
        inlineMath: [['$', '$'], ['\\(', '\\)']],
    },
    chtml: {
        displayAlign: 'left',
    },
};

(function () {
    let script = document.createElement('script');
    script.src = 'https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-chtml.js'
    script.async = true;
    document.head.appendChild(script);
})();
