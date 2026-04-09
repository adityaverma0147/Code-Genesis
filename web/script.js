const editorEl = document.getElementById('editor');
const lineNumsEl = document.getElementById('line-nums');
const charCountEl = document.getElementById('char-count');

function syncEditor() {
    const lines = editorEl.value.split('\n');
    lineNumsEl.innerHTML = lines.map((_, i) => i + 1).join('<br>');
    charCountEl.textContent = `${editorEl.value.length} chars · ${lines.length} line${lines.length !== 1 ? 's' : ''}`;
}

editorEl.addEventListener('input', syncEditor);
editorEl.addEventListener('scroll', () => {
    lineNumsEl.scrollTop = editorEl.scrollTop;
});

const EXAMPLES = {
    hello: `int main() {\n    printf("Hello, World!");\n    return 0;\n}`,
    factorial: `int factorial(int n) {\n    if (n <= 1) {\n        return 1;\n    }\n    return n * factorial(n - 1);\n}\n\nint main() {\n    int result = factorial(5);\n    printf(result);\n    return 0;\n}`,
    loop: `int main() {\n    int i = 0;\n    while (i < 10) {\n        printf(i);\n        i = i + 1;\n    }\n    return 0;\n}`,
    for: `int main() {\n    int sum = 0;\n    for (int i = 1; i <= 10; i++) {\n        sum = sum + i;\n    }\n    printf(sum);\n    return 0;\n}`,
    math: `int main() {\n    int a = 10 + 5 * 2;\n    int b = (a - 4) / 2;\n    printf(a);\n    printf(b);\n    return 0;\n}`,
    pointers: `#include <stdio.h>\n#define VAL 42\n\nint main() {\n    int x = 10;\n    int* p = &x;\n    \n    printf("Original x:");\n    printf(x);\n    \n    *p = VAL;\n    \n    printf("Updated x via *p:");\n    printf(x);\n    \n    return 0;\n}`
};

function loadEx(key) {
    editorEl.value = EXAMPLES[key];
    syncEditor();
    transpileUI();
}

function switchTab(name) {
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.toggle('active', btn.dataset.tab === name));
    document.querySelectorAll('.panel').forEach(panel => panel.classList.toggle('active', panel.id === `panel-${name}`));
}

function showToast(msg) {
    const toast = document.getElementById('toast');
    toast.textContent = msg;
    toast.classList.add('show');
    setTimeout(() => toast.classList.remove('show'), 3000);
}

function setStatus(state, msg) {
    const dot = document.getElementById('st-dot');
    dot.className = 'status-dot ' + state;
    document.getElementById('st-text').textContent = msg;
}

function clearAll() {
    editorEl.value = '';
    syncEditor();
    setStatus('', 'Editor cleared');
}

function copyPython() {
    const code = document.getElementById('out-python').textContent;
    navigator.clipboard.writeText(code);
    showToast('Python code copied to clipboard');
}

async function transpileUI() {
    const code = editorEl.value.trim();
    if (!code) {
        showToast('Please enter some C code');
        return;
    }

    const btn = document.getElementById('btn-run');
    const spinner = document.getElementById('spinner');
    btn.disabled = true;
    spinner.style.display = 'inline-block';
    setStatus('', 'Transpiling...');

    try {
        const response = await fetch('http://localhost:5000/api/transpile', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ code })
        });

        const data = await response.json();

        if (data.error) {
            setStatus('err', data.error);
            document.getElementById('out-tokens').textContent = data.error;
            return;
        }

        setStatus('ok', 'Transpilation successful');
        
        document.getElementById('out-tokens').textContent = data.tokens || 'No tokens produced';
        document.getElementById('out-ast').textContent = data.ast || 'No AST produced';
        document.getElementById('out-sym').textContent = data.symbols || 'No symbols found';
        document.getElementById('out-semantic').textContent = data.semantic || 'No semantic errors found';
        document.getElementById('out-ir').textContent = data.ir || 'No IR produced';
        document.getElementById('out-python').textContent = data.python || 'No Python code produced';

        // Stats
        document.getElementById('s-tokens').textContent = data.stats.tokens;
        document.getElementById('s-ir').textContent = data.stats.ir;
        document.getElementById('s-syms').textContent = data.stats.symbols;
        document.getElementById('s-lines').textContent = data.stats.lines;

    } catch (err) {
        setStatus('err', 'Connection error');
        showToast('Could not connect to the backend server');
    } finally {
        btn.disabled = false;
        spinner.style.display = 'none';
    }
}

// Init
syncEditor();
