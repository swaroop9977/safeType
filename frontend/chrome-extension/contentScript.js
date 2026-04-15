const MAX_CAPTURE_LENGTH = 20000;

function trimText(value) {
  return value.replace(/\s+/g, ' ').trim().slice(0, MAX_CAPTURE_LENGTH);
}

function getFocusedSelection() {
  const element = document.activeElement;

  if (!element) {
    return '';
  }

  const isTextInput =
    element instanceof HTMLTextAreaElement ||
    (element instanceof HTMLInputElement &&
      ['text', 'search', 'url', 'email', 'tel', 'password'].includes(element.type));

  if (!isTextInput) {
    return '';
  }

  const start = element.selectionStart ?? 0;
  const end = element.selectionEnd ?? 0;

  if (start === end) {
    return '';
  }

  return trimText(element.value.slice(start, end));
}

function getSelectionText() {
  const focusedSelection = getFocusedSelection();
  if (focusedSelection) {
    return focusedSelection;
  }

  const selection = window.getSelection();
  if (!selection) {
    return '';
  }

  return trimText(selection.toString());
}

function getPageText() {
  const bodyText = document.body?.innerText || '';
  return trimText(bodyText);
}

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message?.type === 'SAFE_TYPE_GET_SELECTION') {
    sendResponse({ ok: true, text: getSelectionText() });
    return false;
  }

  if (message?.type === 'SAFE_TYPE_GET_PAGE_TEXT') {
    sendResponse({ ok: true, text: getPageText() });
    return false;
  }

  return false;
});