const DEFAULT_SETTINGS = {
  backendUrl: 'http://localhost:5000/api',
  apiKey: '',
};

function normalizeBaseUrl(value) {
  return (value || DEFAULT_SETTINGS.backendUrl).replace(/\/+$/, '');
}

function getSettings() {
  return new Promise((resolve) => {
    chrome.storage.sync.get(DEFAULT_SETTINGS, resolve);
  });
}

function buildHeaders(apiKey) {
  const headers = {
    'Content-Type': 'application/json',
  };

  if (apiKey) {
    headers['X-API-Key'] = apiKey;
  }

  return headers;
}

async function postJson(path, body) {
  const settings = await getSettings();
  const response = await fetch(`${normalizeBaseUrl(settings.backendUrl)}${path}`, {
    method: 'POST',
    headers: buildHeaders(settings.apiKey),
    body: JSON.stringify(body),
  });

  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    throw new Error(data.error || `Request failed with status ${response.status}`);
  }

  return data;
}

async function getJson(path) {
  const settings = await getSettings();
  const headers = {};

  if (settings.apiKey) {
    headers['X-API-Key'] = settings.apiKey;
  }

  const response = await fetch(`${normalizeBaseUrl(settings.backendUrl)}${path}`, {
    method: 'GET',
    headers,
  });

  const data = await response.json().catch(() => ({}));

  if (!response.ok) {
    throw new Error(data.error || `Request failed with status ${response.status}`);
  }

  return data;
}

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message?.type === 'SAFE_TYPE_SCAN_TEXT') {
    postJson('/scan/text', {
      text: message.text || '',
      include_suggestions: true,
      include_highlights: true,
    })
      .then((result) => sendResponse({ ok: true, result }))
      .catch((error) => sendResponse({ ok: false, error: error.message }));

    return true;
  }

  if (message?.type === 'SAFE_TYPE_GET_STATUS') {
    getJson('/status')
      .then((result) => sendResponse({ ok: true, result }))
      .catch((error) => sendResponse({ ok: false, error: error.message }));

    return true;
  }

  if (message?.type === 'SAFE_TYPE_SAVE_SETTINGS') {
    chrome.storage.sync.set(
      {
        backendUrl: message.backendUrl || DEFAULT_SETTINGS.backendUrl,
        apiKey: message.apiKey || '',
      },
      () => sendResponse({ ok: true })
    );

    return true;
  }

  return false;
});