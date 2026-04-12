const DEFAULT_SETTINGS = {
  backendUrl: 'http://localhost:5000/api',
  apiKey: '',
};

function getSettings() {
  return new Promise((resolve) => {
    chrome.storage.sync.get(DEFAULT_SETTINGS, resolve);
  });
}

function setStatus(message, isError = false) {
  const status = document.getElementById('status');
  status.textContent = message;
  status.style.color = isError ? '#ff8b8b' : '#9fb2c9';
}

document.addEventListener('DOMContentLoaded', async () => {
  const backendUrlInput = document.getElementById('backend-url');
  const apiKeyInput = document.getElementById('api-key');
  const form = document.getElementById('settings-form');

  const settings = await getSettings();
  backendUrlInput.value = settings.backendUrl;
  apiKeyInput.value = settings.apiKey;

  form.addEventListener('submit', (event) => {
    event.preventDefault();

    chrome.storage.sync.set(
      {
        backendUrl: backendUrlInput.value.trim() || DEFAULT_SETTINGS.backendUrl,
        apiKey: apiKeyInput.value.trim(),
      },
      () => setStatus('Settings saved')
    );
  });
});