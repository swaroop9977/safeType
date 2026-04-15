function sendMessage(message) {
  return new Promise((resolve, reject) => {
    chrome.runtime.sendMessage(message, (response) => {
      if (chrome.runtime.lastError) {
        reject(new Error(chrome.runtime.lastError.message));
        return;
      }

      resolve(response);
    });
  });
}

function queryActiveTab() {
  return new Promise((resolve) => {
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => resolve(tabs[0]));
  });
}

function sendTabMessage(tabId, message) {
  return new Promise((resolve, reject) => {
    chrome.tabs.sendMessage(tabId, message, (response) => {
      if (chrome.runtime.lastError) {
        reject(new Error(chrome.runtime.lastError.message));
        return;
      }

      resolve(response);
    });
  });
}

function setStatus(text, isError = false) {
  const status = document.getElementById('status');
  status.textContent = text;
  status.style.color = isError ? '#ff8b8b' : '#9fb2c9';
}

function showResult(result) {
  const resultEl = document.getElementById('result');
  const riskScore = document.getElementById('risk-score');
  const riskLevel = document.getElementById('risk-level');
  const reasons = document.getElementById('reasons');
  const piiList = document.getElementById('pii-list');
  const suggestions = document.getElementById('suggestions');

  resultEl.classList.remove('hidden');
  riskScore.textContent = `${Math.round((result.risk_score || 0) * 100)}%`;
  riskLevel.textContent = result.risk_level || 'Unknown';

  reasons.innerHTML = '';
  (result.reasons || []).forEach((reason) => {
    const item = document.createElement('li');
    item.textContent = reason;
    reasons.appendChild(item);
  });

  piiList.innerHTML = '';
  (result.detected_pii || []).forEach((item) => {
    const chip = document.createElement('span');
    chip.className = 'chip';
    chip.textContent = `${item.type}: ${item.value}`;
    piiList.appendChild(chip);
  });

  suggestions.innerHTML = '';
  (result.safer_suggestions || []).forEach((item) => {
    const box = document.createElement('div');
    box.className = 'suggestion';

    const title = document.createElement('strong');
    title.textContent = item.type;

    const body = document.createElement('div');
    body.textContent = item.text || item.explanation || '';

    box.appendChild(title);
    box.appendChild(body);
    suggestions.appendChild(box);
  });
}

async function scanText(text) {
  const trimmed = (text || '').trim();

  if (!trimmed) {
    setStatus('Enter or capture text before scanning.', true);
    return;
  }

  setStatus('Scanning text...');

  try {
    const response = await sendMessage({
      type: 'SAFE_TYPE_SCAN_TEXT',
      text: trimmed,
    });

    if (!response?.ok) {
      throw new Error(response?.error || 'Scan failed');
    }

    showResult(response.result);
    setStatus('Scan complete');
  } catch (error) {
    setStatus(error.message, true);
  }
}

async function captureSelection() {
  const tab = await queryActiveTab();

  if (!tab?.id) {
    setStatus('Could not access the current tab.', true);
    return;
  }

  try {
    const response = await sendTabMessage(tab.id, { type: 'SAFE_TYPE_GET_SELECTION' });
    const input = document.getElementById('input');
    input.value = response?.text || '';

    if (!response?.text) {
      setStatus('No text selected on the page.', true);
      return;
    }

    setStatus('Selection captured');
  } catch (error) {
    setStatus('This page does not expose selectable text to the extension.', true);
  }
}

async function capturePageText() {
  const tab = await queryActiveTab();

  if (!tab?.id) {
    setStatus('Could not access the current tab.', true);
    return;
  }

  try {
    const response = await sendTabMessage(tab.id, { type: 'SAFE_TYPE_GET_PAGE_TEXT' });
    const input = document.getElementById('input');
    input.value = response?.text || '';

    if (!response?.text) {
      setStatus('No page text was captured.', true);
      return;
    }

    setStatus('Page text captured');
  } catch (error) {
    setStatus('Could not read page content from this tab.', true);
  }
}

async function refreshStatus() {
  try {
    const response = await sendMessage({ type: 'SAFE_TYPE_GET_STATUS' });
    if (!response?.ok) {
      throw new Error(response?.error || 'Status unavailable');
    }

    setStatus('Backend connected');
  } catch (error) {
    setStatus('Backend offline or unreachable.', true);
  }
}

document.addEventListener('DOMContentLoaded', () => {
  const input = document.getElementById('input');

  document.getElementById('scan-text').addEventListener('click', () => scanText(input.value));
  document.getElementById('use-selection').addEventListener('click', captureSelection);
  document.getElementById('use-page').addEventListener('click', capturePageText);

  refreshStatus();
});